import abc
from django.conf import settings
from apps.knowledge_base.services.knowledge_service import KnowledgeService
from apps.chatbot.services.knowledge_loader import KnowledgeLoader
from apps.knowledge_base.models import KnowledgeEntry


class BaseKnowledgeProvider(abc.ABC):
    """
    Abstract base class for providing knowledge to the chatbot.
    """

    @abc.abstractmethod
    def get_scoped_knowledge_as_text(self, company=True, services=True, industries=True, faq=True, contact=True) -> str:
        """
        Returns a formatted text string containing the knowledge base information,
        suitable for insertion into an LLM prompt.
        """
        pass

    @abc.abstractmethod
    def get_category_data(self, category: str):
        """
        Returns structured data (list or dict) for a given category name.
        Expected categories: 'company', 'services', 'industries', 'faq', 'contact'
        """
        pass


class JsonKnowledgeProvider(BaseKnowledgeProvider):
    """
    Provides knowledge by reading from static JSON files on the disk.
    This maintains backward compatibility with the original chatbot implementation.
    """

    def __init__(self):
        self.loader = KnowledgeLoader()
        self._category_map = {
            'company': self.loader.get_company_info,
            'services': self.loader.get_services,
            'industries': self.loader.get_industries,
            'faq': self.loader.get_faq,
            'contact': self.loader.get_contact_info,
        }

    def get_scoped_knowledge_as_text(self, company=True, services=True, industries=True, faq=True, contact=True) -> str:
        return self.loader.get_scoped_knowledge_as_text(company, services, industries, faq, contact)

    def get_category_data(self, category: str):
        func = self._category_map.get(category)
        if func:
            return func()
        return None


class DatabaseKnowledgeProvider(BaseKnowledgeProvider):
    """
    Provides knowledge by querying the database's KnowledgeEntry model.
    Only returns published and non-deleted entries.
    """

    def get_scoped_knowledge_as_text(self, company=True, services=True, industries=True, faq=True, contact=True) -> str:
        # Relies on the existing service which properly formats the output to mimic KnowledgeLoader
        return KnowledgeService.get_scoped_knowledge_as_text(
            company=company,
            services=services,
            industries=industries,
            faq=faq,
            contact=contact
        )

    def get_category_data(self, category: str):
        # Map provider categories to model categories
        category_map = {
            'company': 'company',
            'services': 'service',
            'industries': 'industry',
            'faq': 'faq',
            'contact': 'contact'
        }
        
        model_category = category_map.get(category)
        if not model_category:
            return None
            
        entries = KnowledgeEntry.objects.filter(
            category__slug=model_category,
            status='published',
            is_deleted=False
        ).order_by('sort_order', 'created_at')
        
        # company and contact conventionally expect a dict instead of a list in the frontend/APIs
        if category in ('company', 'contact'):
            if not entries.exists():
                return {}
            # Take the first entry and merge its structured data
            e = entries.first()
            data = {"title": e.title, "content": e.content}
            if isinstance(e.structured_data, dict) and e.structured_data:
                data.update(e.structured_data)
            return data
            
        # services, industries, faq expect a list of dicts
        if not entries.exists():
            return []
            
        data_list = []
        for e in entries:
            data = {"title": e.title, "content": e.content}
            if isinstance(e.structured_data, dict) and e.structured_data:
                data.update(e.structured_data)
            data_list.append(data)
            
        return data_list


class KnowledgeProviderFactory:
    """
    Factory for instantiating the correct KnowledgeProvider based on Django settings.
    """

    @staticmethod
    def get_provider() -> BaseKnowledgeProvider:
        source = getattr(settings, 'KNOWLEDGE_SOURCE', 'json').lower()
        if source in ('db', 'database'):
            return DatabaseKnowledgeProvider()
        return JsonKnowledgeProvider()
