from __future__ import annotations

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Count, Q, QuerySet

from apps.user_management.models import UserAuditLog

User = get_user_model()


class RoleService:
    """Encapsulates all business logic for role management."""

    PROTECTED_ROLES = {'Admin', 'Sales', 'Support'}

    @staticmethod
    def list_roles(search: str | None = None, ordering: str | None = None) -> QuerySet:
        qs = Group.objects.annotate(
            permissions_count=Count('permissions', distinct=True),
            users_count=Count('user', distinct=True),
        )
        if search:
            qs = qs.filter(name__icontains=search)
        if ordering:
            bare = ordering.lstrip('-')
            if bare in ('name', 'id'):
                qs = qs.order_by(ordering)
            else:
                qs = qs.order_by('name')
        else:
            qs = qs.order_by('name')
        return qs

    @staticmethod
    def get_role(role_id: int) -> Group:
        return Group.objects.get(pk=role_id)

    @staticmethod
    def create_role(name: str, permissions: list[str], actor: User) -> Group:
        if Group.objects.filter(name__iexact=name).exists():
            raise ValidationError({'name': 'A role with this name already exists.'})

        perm_objects = RoleService._validate_permissions(permissions)

        role = Group.objects.create(name=name)
        if perm_objects:
            role.permissions.set(perm_objects)

        RoleService._create_audit_log(
            actor=actor,
            action='role_created',
            description=f"Created role '{name}'",
            metadata={'role_id': role.pk, 'role_name': name},
        )
        return role

    @staticmethod
    def update_role(role: Group, name: str, actor: User) -> Group:
        if Group.objects.filter(name__iexact=name).exclude(pk=role.pk).exists():
            raise ValidationError({'name': 'A role with this name already exists.'})

        old_name = role.name
        role.name = name
        role.save(update_fields=['name'])

        RoleService._create_audit_log(
            actor=actor,
            action='role_updated',
            description=f"Updated role '{old_name}' -> '{name}'",
            metadata={'role_id': role.pk, 'old_name': old_name, 'new_name': name},
        )
        return role

    @staticmethod
    def delete_role(role: Group, actor: User) -> None:
        if role.name in RoleService.PROTECTED_ROLES:
            raise ValidationError(
                {'detail': f"Cannot delete protected role '{role.name}'."}
            )

        role_name = role.name
        role_id = role.pk
        role.delete()

        RoleService._create_audit_log(
            actor=actor,
            action='role_deleted',
            description=f"Deleted role '{role_name}'",
            metadata={'role_id': role_id, 'role_name': role_name},
        )

    @staticmethod
    def set_permissions(role: Group, codenames: list[str], actor: User) -> Group:
        perm_objects = RoleService._validate_permissions(codenames)

        old_perms = sorted(
            role.permissions.values_list('content_type__app_label', 'codename')
        )
        old_perm_strings = [f"{al}.{cn}" for al, cn in old_perms]

        role.permissions.set(perm_objects)

        new_perm_strings = sorted(codenames) if codenames else []

        RoleService._create_audit_log(
            actor=actor,
            action='role_permissions_changed',
            description=f"Changed permissions for role '{role.name}'",
            metadata={
                'role_id': role.pk,
                'old_permissions': old_perm_strings,
                'new_permissions': new_perm_strings,
            },
        )
        return role

    @staticmethod
    def list_role_users(role: Group, search: str | None = None) -> QuerySet:
        qs = role.user_set.all()
        if search:
            qs = qs.filter(
                Q(username__icontains=search)
                | Q(email__icontains=search)
                | Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
            )
        return qs.order_by('username')

    @staticmethod
    @transaction.atomic
    def add_users(role: Group, user_ids: list[int], actor: User) -> dict:
        added_count = 0
        skipped = []

        for uid in user_ids:
            try:
                user = User.objects.get(pk=uid)
            except User.DoesNotExist:
                skipped.append({'id': uid, 'reason': 'user not found'})
                continue

            if role.user_set.filter(pk=uid).exists():
                skipped.append({'id': uid, 'reason': 'already in role'})
                continue

            role.user_set.add(user)
            added_count += 1

        RoleService._create_audit_log(
            actor=actor,
            action='role_users_added',
            description=f"Added {added_count} user(s) to role '{role.name}'",
            metadata={
                'role_id': role.pk,
                'user_ids': user_ids,
                'added_count': added_count,
                'skipped': skipped,
            },
        )
        return {'added_count': added_count, 'skipped': skipped}

    @staticmethod
    @transaction.atomic
    def remove_users(role: Group, user_ids: list[int], actor: User) -> dict:
        removed_count = 0
        skipped = []

        for uid in user_ids:
            try:
                user = User.objects.get(pk=uid)
            except User.DoesNotExist:
                skipped.append({'id': uid, 'reason': 'user not found'})
                continue

            if not role.user_set.filter(pk=uid).exists():
                skipped.append({'id': uid, 'reason': 'not in role'})
                continue

            # Last superuser protection: cannot remove last active superuser from Admin
            if role.name == 'Admin' and user.is_superuser and user.is_active:
                active_superusers_in_admin = role.user_set.filter(
                    is_superuser=True, is_active=True
                ).count()
                if active_superusers_in_admin <= 1:
                    skipped.append({'id': uid, 'reason': 'cannot remove last active superuser from Admin'})
                    continue

            role.user_set.remove(user)
            removed_count += 1

        RoleService._create_audit_log(
            actor=actor,
            action='role_users_removed',
            description=f"Removed {removed_count} user(s) from role '{role.name}'",
            metadata={
                'role_id': role.pk,
                'user_ids': user_ids,
                'removed_count': removed_count,
                'skipped': skipped,
            },
        )
        return {'removed_count': removed_count, 'skipped': skipped}

    @staticmethod
    def list_available_permissions() -> QuerySet:
        return Permission.objects.select_related('content_type').order_by(
            'content_type__app_label', 'codename'
        )

    # ─── Internal helpers ──────────────────────────────────────────────

    @staticmethod
    def _validate_permissions(codenames: list[str]) -> list[Permission]:
        if not codenames:
            return []

        permissions = []
        invalid = []
        for codename in codenames:
            parts = codename.split('.', 1)
            if len(parts) != 2:
                invalid.append(codename)
                continue
            app_label, code = parts
            try:
                perm = Permission.objects.get(
                    content_type__app_label=app_label, codename=code
                )
                permissions.append(perm)
            except Permission.DoesNotExist:
                invalid.append(codename)

        if invalid:
            raise ValidationError(
                {'permissions': f"Invalid permissions: {', '.join(invalid)}"}
            )
        return permissions

    @staticmethod
    def _create_audit_log(
        actor: User,
        action: str,
        description: str,
        metadata: dict | None = None,
    ) -> None:
        UserAuditLog.objects.create(
            actor=actor,
            target_user=None,
            action=action,
            description=description,
            metadata=metadata or {},
        )
