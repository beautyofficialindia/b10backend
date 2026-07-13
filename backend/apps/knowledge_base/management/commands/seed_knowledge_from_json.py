import json
import logging

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from apps.knowledge_base.models import KnowledgeEntry, Category

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Seed KnowledgeEntry table from JSON files in knowledge/ directory"

    def handle(self, *args, **options):
        knowledge_dir = settings.BASE_DIR.parent / 'knowledge'
        created = 0
        skipped = 0
        failed = 0

        FILE_MAP = [
            ('company.json', self._seed_company),
            ('services.json', self._seed_services),
            ('industries.json', self._seed_industries),
            ('faq.json', self._seed_faq),
            ('contact.json', self._seed_contact),
        ]

        for filename, handler in FILE_MAP:
            file_path = knowledge_dir / filename
            try:
                data = json.loads(file_path.read_text(encoding='utf-8'))
                c, s = handler(data)
                created += c
                skipped += s
            except (FileNotFoundError, json.JSONDecodeError) as e:
                self.stderr.write(self.style.ERROR(f"Error processing {filename}: {e}"))
                logger.error(f"Error processing {filename}: {e}")
                failed += 1

        self.stdout.write(
            f"Seeding complete: {created} created, {skipped} skipped, {failed} failed."
        )

    def _create_or_skip(self, title, category, content, structured_data=None):
        """Create entry if slug doesn't exist, otherwise skip."""
        slug = slugify(title)
        if not slug:
            slug = 'entry'

        if KnowledgeEntry.objects.filter(slug=slug).exists():
            self.stderr.write(self.style.WARNING(f"Skipped (slug exists): {title}"))
            logger.warning(f"Skipped (slug exists): {title}")
            return 0, 1  # created=0, skipped=1

        KnowledgeEntry.objects.create(
            category=category,
            title=title,
            slug=slug,
            content=content or '',
            structured_data=structured_data or {},
            source='json_import',
            status='draft',
        )
        return 1, 0  # created=1, skipped=0

    def _seed_company(self, data):
        """Single entry: category=company_category, title='Company Info'."""
        content = data.get('description', '')
        return self._create_or_skip(
            title='Company Info',
            category=company_category,
            content=content,
            structured_data=data,
        )

    def _seed_services(self, data):
        """Map name→title, description→content, technologies→structured_data."""
        created = 0
        skipped = 0
        for service in data:
            structured = {}
            if 'technologies' in service:
                structured['technologies'] = service['technologies']
            c, s = self._create_or_skip(
                title=service.get('name', 'Unnamed Service'),
                category=service_category,
                content=service.get('description', ''),
                structured_data=structured,
            )
            created += c
            skipped += s
        return created, skipped

    def _seed_industries(self, data):
        """Map name→title, description→content."""
        created = 0
        skipped = 0
        for industry in data:
            c, s = self._create_or_skip(
                title=industry.get('name', 'Unnamed Industry'),
                category='industry',
                content=industry.get('description', ''),
            )
            created += c
            skipped += s
        return created, skipped

    def _seed_faq(self, data):
        """Map question→title, answer→content."""
        created = 0
        skipped = 0
        for faq in data:
            c, s = self._create_or_skip(
                title=faq.get('question', 'Unnamed FAQ'),
                category=faq_category,
                content=faq.get('answer', ''),
            )
            created += c
            skipped += s
        return created, skipped

    def _seed_contact(self, data):
        """Single entry: category='contact', title='Contact Info'."""
        email = data.get('email', '')
        phone = data.get('phone', '')
        address = data.get('address', '')
        content = f"Email: {email}. Phone: {phone}. Address: {address}."
        return self._create_or_skip(
            title='Contact Info',
            category='contact',
            content=content,
            structured_data=data,
        )
