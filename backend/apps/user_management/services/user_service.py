from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q, QuerySet
from django.utils.dateparse import parse_datetime, parse_date

from apps.user_management.models import UserAuditLog

User = get_user_model()


def _parse_date_param(value):
    """Parse a date/datetime string from query parameter. Handles ISO 8601 variants."""
    if value is None:
        return None
    if not isinstance(value, str):
        return value
    # Try full datetime first
    result = parse_datetime(value)
    if result:
        return result
    # Try date-only
    result = parse_date(value)
    if result:
        from django.utils import timezone as tz
        from datetime import datetime, time
        return tz.make_aware(datetime.combine(result, time.min))
    # Try with manual timezone fix (e.g. +0530 → +05:30)
    import re
    fixed = re.sub(r'([+-]\d{2})(\d{2})$', r'\1:\2', value)
    result = parse_datetime(fixed)
    return result

User = get_user_model()


class UserService:
    """
    Encapsulates all business logic for user management.
    All state-changing methods create UserAuditLog entries.
    """

    # ─── Allowed ordering fields ───────────────────────────────────────
    ALLOWED_ORDERING_FIELDS = {
        'username', 'email', 'date_joined', 'last_login',
        'first_name', 'last_name',
    }

    # ─── Public methods ────────────────────────────────────────────────

    @staticmethod
    def list_users(
        search: str | None = None,
        ordering: str | None = None,
        is_active: bool | None = None,
        is_staff: bool | None = None,
        is_superuser: bool | None = None,
        group: str | None = None,
        date_joined_after=None,
        date_joined_before=None,
        last_login_after=None,
        last_login_before=None,
    ) -> QuerySet:
        """
        Returns filtered, ordered queryset of Users.
        Uses prefetch_related("groups") for efficient serialization.
        """
        qs = User.objects.prefetch_related("groups").all()

        # Search: case-insensitive partial match with OR logic
        if search:
            qs = qs.filter(
                Q(username__icontains=search)
                | Q(email__icontains=search)
                | Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
            )

        # Boolean filters
        if is_active is not None:
            qs = qs.filter(is_active=is_active)
        if is_staff is not None:
            qs = qs.filter(is_staff=is_staff)
        if is_superuser is not None:
            qs = qs.filter(is_superuser=is_superuser)

        # Group filter
        if group:
            qs = qs.filter(groups__name=group)

        # Date range filters
        if date_joined_after:
            parsed = _parse_date_param(date_joined_after)
            if parsed:
                qs = qs.filter(date_joined__gte=parsed)
        if date_joined_before:
            parsed = _parse_date_param(date_joined_before)
            if parsed:
                qs = qs.filter(date_joined__lte=parsed)
        if last_login_after:
            parsed = _parse_date_param(last_login_after)
            if parsed:
                qs = qs.filter(last_login__gte=parsed)
        if last_login_before:
            parsed = _parse_date_param(last_login_before)
            if parsed:
                qs = qs.filter(last_login__lte=parsed)

        # Ordering
        if ordering:
            # Strip leading - to get the bare field name
            bare_field = ordering.lstrip('-')
            if bare_field in UserService.ALLOWED_ORDERING_FIELDS:
                qs = qs.order_by(ordering)
            else:
                # Default ordering if invalid field provided
                qs = qs.order_by('-date_joined')
        else:
            qs = qs.order_by('-date_joined')

        return qs

    @staticmethod
    def get_user(user_id: int) -> User:
        """
        Returns User with prefetched groups and permissions.
        Raises User.DoesNotExist if not found.
        """
        return (
            User.objects
            .prefetch_related("groups", "user_permissions")
            .get(pk=user_id)
        )

    @staticmethod
    def create_user(data: dict, actor: User) -> User:
        """
        Creates a new User with validated data.
        Raises ValidationError on invalid input.
        """
        username = data['username']
        email = data['email'].strip().lower()
        password = data['password']
        first_name = data.get('first_name', '')
        last_name = data.get('last_name', '')
        groups = data.get('groups', [])
        is_active = data.get('is_active', True)
        is_staff = data.get('is_staff', True)
        is_superuser = data.get('is_superuser', False)

        # Validate username uniqueness (case-insensitive)
        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError(
                {'username': 'A user with this username already exists.'}
            )

        # Validate email uniqueness (case-insensitive)
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError(
                {'email': 'A user with this email already exists.'}
            )

        # Validate group names
        group_objects = UserService._validate_group_names(groups)

        # Validate password against AUTH_PASSWORD_VALIDATORS
        # Create a temporary user object for attribute similarity check
        temp_user = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
        )
        try:
            validate_password(password, user=temp_user)
        except ValidationError as e:
            raise ValidationError({'password': e.messages})

        # Create the user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            is_active=is_active,
            is_staff=is_staff,
            is_superuser=is_superuser,
        )

        # Assign groups
        if group_objects:
            user.groups.set(group_objects)

        # Audit log
        UserService._create_audit_log(
            actor=actor,
            target_user=user,
            action='user_created',
            description=f"Created user '{username}' with email '{email}'",
        )

        return user

    @staticmethod
    def update_user(user: User, data: dict, actor: User) -> User:
        """
        Updates User fields. Raises ValidationError on invalid input.
        """
        # Reject username field
        if 'username' in data:
            raise ValidationError(
                {'username': 'Username cannot be modified after creation.'}
            )

        old_values = {}
        new_values = {}

        # Email uniqueness check
        if 'email' in data:
            email = data['email'].strip().lower()
            if User.objects.filter(email__iexact=email).exclude(pk=user.pk).exists():
                raise ValidationError(
                    {'email': 'A user with this email already exists.'}
                )
            old_values['email'] = user.email
            new_values['email'] = email
            user.email = email

        # Validate group names if provided
        groups_changed = False
        if 'groups' in data:
            group_objects = UserService._validate_group_names(data['groups'])
            old_groups = list(user.groups.values_list('name', flat=True))

            # Last active superuser protection: cannot remove from Admin group
            if UserService._is_last_active_superuser(user):
                new_group_names = [g.name for g in group_objects]
                if 'Admin' not in new_group_names and 'Admin' in old_groups:
                    raise ValidationError(
                        {'groups': 'Cannot remove the last active superuser from the Admin group.'}
                    )

            user.groups.set(group_objects)
            new_groups = list(user.groups.values_list('name', flat=True))
            if set(old_groups) != set(new_groups):
                groups_changed = True
                old_values['groups'] = sorted(old_groups)
                new_values['groups'] = sorted(new_groups)

        # Last active superuser protection: cannot set is_superuser=False
        if 'is_superuser' in data and data['is_superuser'] is False:
            if UserService._is_last_active_superuser(user):
                raise ValidationError(
                    {'is_superuser': 'Cannot remove superuser status from the last active superuser.'}
                )

        # Update scalar fields
        scalar_fields = ['first_name', 'last_name', 'is_active', 'is_staff', 'is_superuser']
        for field in scalar_fields:
            if field in data:
                old_val = getattr(user, field)
                new_val = data[field]
                if old_val != new_val:
                    old_values[field] = old_val
                    new_values[field] = new_val
                    setattr(user, field, new_val)

        user.save()

        # Audit log for update
        if old_values or new_values:
            UserService._create_audit_log(
                actor=actor,
                target_user=user,
                action='user_updated',
                description=f"Updated user '{user.username}'",
                metadata={'old_values': old_values, 'new_values': new_values},
            )

        # Additional audit log for group changes
        if groups_changed:
            UserService._create_audit_log(
                actor=actor,
                target_user=user,
                action='groups_changed',
                description=f"Changed groups for user '{user.username}'",
                metadata={
                    'old_values': {'groups': old_values.get('groups', [])},
                    'new_values': {'groups': new_values.get('groups', [])},
                },
            )

        return user

    @staticmethod
    def activate_user(user: User, actor: User) -> User:
        """Sets is_active=True. Creates audit log."""
        user.is_active = True
        user.save(update_fields=['is_active'])

        UserService._create_audit_log(
            actor=actor,
            target_user=user,
            action='user_activated',
            description=f"Activated user '{user.username}'",
        )

        return user

    @staticmethod
    def deactivate_user(user: User, actor: User) -> User:
        """
        Sets is_active=False.
        Raises ValidationError on protection violations.
        """
        # Self-deactivation check
        if user.pk == actor.pk:
            raise ValidationError(
                {'detail': 'You cannot deactivate your own account.'}
            )

        # Last active superuser protection
        if UserService._is_last_active_superuser(user):
            raise ValidationError(
                {'detail': 'Cannot deactivate the last active superuser.'}
            )

        user.is_active = False
        user.save(update_fields=['is_active'])

        UserService._create_audit_log(
            actor=actor,
            target_user=user,
            action='user_deactivated',
            description=f"Deactivated user '{user.username}'",
        )

        return user

    @staticmethod
    def reset_password(user: User, password: str, actor: User) -> None:
        """
        Validates and sets new password.
        Raises ValidationError on invalid password.
        """
        try:
            validate_password(password, user=user)
        except ValidationError as e:
            raise ValidationError({'password': e.messages})

        user.set_password(password)
        user.save(update_fields=['password'])

        UserService._create_audit_log(
            actor=actor,
            target_user=user,
            action='password_reset',
            description=f"Password reset for user '{user.username}'",
        )

    @staticmethod
    @transaction.atomic
    def bulk_activate(user_ids: list[int], actor: User) -> dict:
        """
        Activates multiple users within a transaction.
        Returns summary with activated_count and skipped list.
        """
        activated_count = 0
        skipped = []

        for user_id in user_ids:
            try:
                user = User.objects.get(pk=user_id)
            except User.DoesNotExist:
                skipped.append({'id': user_id, 'reason': 'user not found'})
                continue

            if user.is_active:
                skipped.append({'id': user_id, 'reason': 'already active'})
                continue

            user.is_active = True
            user.save(update_fields=['is_active'])
            activated_count += 1

            UserService._create_audit_log(
                actor=actor,
                target_user=user,
                action='bulk_activated',
                description=f"Bulk activated user '{user.username}'",
            )

        return {
            'activated_count': activated_count,
            'skipped': skipped,
        }

    @staticmethod
    @transaction.atomic
    def bulk_deactivate(user_ids: list[int], actor: User) -> dict:
        """
        Deactivates multiple users within a transaction.
        Returns summary with deactivated_count and skipped list.
        """
        deactivated_count = 0
        skipped = []

        for user_id in user_ids:
            try:
                user = User.objects.get(pk=user_id)
            except User.DoesNotExist:
                skipped.append({'id': user_id, 'reason': 'user not found'})
                continue

            # Self-deactivation check
            if user.pk == actor.pk:
                skipped.append({'id': user_id, 'reason': 'cannot deactivate yourself'})
                continue

            # Already inactive
            if not user.is_active:
                skipped.append({'id': user_id, 'reason': 'already inactive'})
                continue

            # Last active superuser protection
            if UserService._is_last_active_superuser(user):
                skipped.append({'id': user_id, 'reason': 'cannot deactivate last active superuser'})
                continue

            user.is_active = False
            user.save(update_fields=['is_active'])
            deactivated_count += 1

            UserService._create_audit_log(
                actor=actor,
                target_user=user,
                action='bulk_deactivated',
                description=f"Bulk deactivated user '{user.username}'",
            )

        return {
            'deactivated_count': deactivated_count,
            'skipped': skipped,
        }

    @staticmethod
    def get_audit_log(user_id: int) -> QuerySet:
        """Returns UserAuditLog entries for user ordered by created_at desc."""
        return (
            UserAuditLog.objects
            .filter(target_user_id=user_id)
            .select_related('actor')
            .order_by('-created_at')
        )

    # ─── Internal helpers ──────────────────────────────────────────────

    @staticmethod
    def _is_last_active_superuser(user: User) -> bool:
        """True when user is the only active superuser in the system."""
        if not user.is_superuser or not user.is_active:
            return False
        count = User.objects.filter(is_superuser=True, is_active=True).count()
        return count == 1

    @staticmethod
    def _validate_group_names(group_names: list[str]) -> list:
        """
        Validates all group names exist. Returns Group objects.
        Raises ValidationError listing invalid names if any don't exist.
        """
        if not group_names:
            return []

        existing_groups = Group.objects.filter(name__in=group_names)
        existing_names = set(existing_groups.values_list('name', flat=True))
        invalid_names = [name for name in group_names if name not in existing_names]

        if invalid_names:
            raise ValidationError(
                {'groups': f"The following groups do not exist: {', '.join(invalid_names)}"}
            )

        return list(existing_groups)

    @staticmethod
    def _create_audit_log(
        actor: User,
        target_user: User,
        action: str,
        description: str,
        metadata: dict | None = None,
    ) -> None:
        """Creates a UserAuditLog record."""
        UserAuditLog.objects.create(
            actor=actor,
            target_user=target_user,
            action=action,
            description=description,
            metadata=metadata or {},
        )
