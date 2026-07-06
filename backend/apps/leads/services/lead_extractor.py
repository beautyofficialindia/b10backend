import re

class LeadExtractor:
    industry_map = {
        'healthcare': 'healthtech',
        'health tech': 'healthtech',
        'healthtech': 'healthtech',
        'education': 'edtech',
        'edtech': 'edtech',
        'ecommerce': 'ecommerce',
        'e-commerce': 'ecommerce',
        'saas': 'saas',
        'marketplace': 'marketplaces',
        'enterprise': 'enterprise',
        'finance': 'finance',
    }

    def extract(self, text):
        extracted = {}
        
        # 1. Email Extraction
        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
        if email_match:
            extracted['email'] = email_match.group(0).lower()
            
        # 2. Phone Extraction (simple heuristic)
        phone_match = re.search(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text)
        if phone_match:
            extracted['phone'] = phone_match.group(0)
            
        # 3. Industry Heuristics
        text_lower = text.lower()
        for industry, normalized in self.industry_map.items():
            if industry in text_lower:
                extracted['industry'] = normalized
                break
                
        # 4. Project Type Heuristics
        if any(word in text_lower for word in ['website', 'web app', 'portal', 'web']):
            extracted['project_type'] = 'web_application_development'
        elif any(word in text_lower for word in ['mobile', 'ios', 'android', 'app']):
            extracted['project_type'] = 'mobile_application_development'
        elif any(word in text_lower for word in ['ai', 'artificial intelligence', 'machine learning', 'bot', 'gpt']):
            extracted['project_type'] = 'ai_powered_solutions'
        elif any(word in text_lower for word in ['custom software', 'crm', 'erp', 'dashboard']):
            extracted['project_type'] = 'custom_software_development'
        elif any(word in text_lower for word in ['ui', 'ux', 'design']):
            extracted['project_type'] = 'ui_ux_design'
            
        # 5. Budget Heuristics
        if '$' in text or 'budget' in text_lower or 'k' in text_lower:
            budget_match = re.search(r'\$?\d+[kKmM]?', text)
            if budget_match:
                extracted['budget_range'] = budget_match.group(0)

        # 6. Timeline Heuristics
        if any(word in text_lower for word in ['asap', 'immediately', 'urgent']):
            extracted['timeline'] = 'immediate'
        elif any(word in text_lower for word in ['1-3 months', '1 to 3 months', 'three months']):
            extracted['timeline'] = '1_3_months'
        elif any(word in text_lower for word in ['3-6 months', '3 to 6 months', 'six months']):
            extracted['timeline'] = '3_6_months'
        elif 'explor' in text_lower:
            extracted['timeline'] = 'exploratory'

        # 7. Name and company hints
        name_match = re.search(r'\b(?:my name is|i am|i\'m)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)', text)
        if name_match:
            extracted['full_name'] = name_match.group(1).strip()

        company_match = re.search(r'\b(?:company is|from|at)\s+([A-Z][A-Za-z0-9&.\-\s]{2,60})', text)
        if company_match:
            extracted['company_name'] = company_match.group(1).strip().rstrip('.')
                
        # Requirements (capture text that isn't just a tiny greeting)
        if len(text.split()) > 7 and 'project_type' in extracted:
            extracted['requirements'] = text
            
        return extracted
