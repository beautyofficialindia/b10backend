import os
import json
from django.conf import settings

class KnowledgeLoader:
    def __init__(self, knowledge_dir=None):
        if knowledge_dir is None:
            self.knowledge_dir = os.path.join(settings.BASE_DIR.parent, 'knowledge')
        else:
            self.knowledge_dir = knowledge_dir

    def _load_json(self, filename):
        file_path = os.path.join(self.knowledge_dir, filename)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return None
        except json.JSONDecodeError:
            return None

    def get_company_info(self):
        return self._load_json('company.json')

    def get_services(self):
        return self._load_json('services.json')

    def get_industries(self):
        return self._load_json('industries.json')

    def get_faq(self):
        return self._load_json('faq.json')

    def get_contact_info(self):
        return self._load_json('contact.json')

    def get_scoped_knowledge_as_text(self, company=True, services=True, industries=True, faq=True, contact=True):
        text = ""
        if company:
            data = self.get_company_info()
            if data: text += f"Company Information:\n{json.dumps(data, indent=2)}\n\n"
        if services:
            data = self.get_services()
            if data: text += f"Services Provided:\n{json.dumps(data, indent=2)}\n\n"
        if industries:
            data = self.get_industries()
            if data: text += f"Industries Served:\n{json.dumps(data, indent=2)}\n\n"
        if faq:
            data = self.get_faq()
            if data: text += f"Frequently Asked Questions (FAQ):\n{json.dumps(data, indent=2)}\n\n"
        if contact:
            data = self.get_contact_info()
            if data: text += f"Contact Information:\n{json.dumps(data, indent=2)}\n\n"
        return text
