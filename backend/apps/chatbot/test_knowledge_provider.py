from django.test import TestCase, override_settings
from apps.chatbot.services.knowledge_provider import (
    KnowledgeProviderFactory,
    JsonKnowledgeProvider,
    DatabaseKnowledgeProvider
)
from apps.knowledge_base.models import KnowledgeEntry
from apps.chatbot.services.knowledge_loader import KnowledgeLoader

class KnowledgeProviderTests(TestCase):
    def setUp(self):
        from apps.knowledge_base.models import Category
        self.company_cat, _ = Category.objects.get_or_create(slug='company', defaults={'name': 'Company'})
        self.service_cat, _ = Category.objects.get_or_create(slug='service', defaults={'name': 'Service'})
        self.faq_cat, _ = Category.objects.get_or_create(slug='faq', defaults={'name': 'FAQ'})
        
        # Create some test knowledge entries in the DB
        KnowledgeEntry.objects.create(
            category=self.company_cat,
            title='About Us',
            content='We are B10 IT Solution.',
            status='published',
            structured_data={"founded": "2020"}
        )
        KnowledgeEntry.objects.create(
            category=self.service_cat,
            title='Web Development',
            content='We build websites.',
            status='published',
            structured_data={"id": "web-dev", "name": "Web Development"}
        )
        # Draft entry (should be ignored)
        KnowledgeEntry.objects.create(
            category=self.faq_cat,
            title='Draft FAQ',
            content='This is a draft.',
            status='draft'
        )

    def test_factory_returns_json_by_default(self):
        provider = KnowledgeProviderFactory.get_provider()
        self.assertIsInstance(provider, JsonKnowledgeProvider)

    @override_settings(KNOWLEDGE_SOURCE='db')
    def test_factory_returns_db_when_configured(self):
        provider = KnowledgeProviderFactory.get_provider()
        self.assertIsInstance(provider, DatabaseKnowledgeProvider)

    @override_settings(KNOWLEDGE_SOURCE='garbage')
    def test_factory_returns_json_on_garbage_config(self):
        provider = KnowledgeProviderFactory.get_provider()
        self.assertIsInstance(provider, JsonKnowledgeProvider)

    @override_settings(KNOWLEDGE_SOURCE='db')
    def test_db_provider_category_data(self):
        provider = KnowledgeProviderFactory.get_provider()
        
        company_data = provider.get_category_data('company')
        self.assertIsInstance(company_data, dict)
        self.assertEqual(company_data['title'], 'About Us')
        self.assertEqual(company_data['founded'], '2020')

        services_data = provider.get_category_data('services')
        self.assertIsInstance(services_data, list)
        self.assertEqual(len(services_data), 1)
        self.assertEqual(services_data[0]['title'], 'Web Development')
        self.assertEqual(services_data[0]['id'], 'web-dev')

        faq_data = provider.get_category_data('faq')
        self.assertEqual(len(faq_data), 0)  # draft should be ignored

    @override_settings(KNOWLEDGE_SOURCE='db')
    def test_db_provider_scoped_text(self):
        provider = KnowledgeProviderFactory.get_provider()
        text = provider.get_scoped_knowledge_as_text()
        
        self.assertIn("About Us", text)
        self.assertIn("We are B10 IT Solution.", text)
        self.assertIn("Web Development", text)
        self.assertNotIn("Draft FAQ", text)

    def test_json_provider_fallbacks(self):
        provider = JsonKnowledgeProvider()
        loader = KnowledgeLoader()
        
        # Test that JsonKnowledgeProvider maps to KnowledgeLoader outputs
        self.assertEqual(provider.get_category_data('company'), loader.get_company_info())
        self.assertEqual(provider.get_category_data('services'), loader.get_services())
        self.assertEqual(provider.get_category_data('faq'), loader.get_faq())
        self.assertEqual(provider.get_scoped_knowledge_as_text(), loader.get_scoped_knowledge_as_text())
