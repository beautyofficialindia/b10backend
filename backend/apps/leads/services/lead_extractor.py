import re

class LeadExtractor:
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
        industries = ['healthcare', 'finance', 'ecommerce', 'e-commerce', 'education', 'real estate', 'retail', 'manufacturing', 'logistics', 'fitness']
        for industry in industries:
            if industry in text_lower:
                extracted['industry'] = industry
                break
                
        # 4. Project Type Heuristics
        if any(word in text_lower for word in ['website', 'web app', 'portal', 'web']):
            extracted['project_type'] = 'Web Development'
        elif any(word in text_lower for word in ['mobile', 'ios', 'android', 'app']):
            extracted['project_type'] = 'Mobile App'
        elif any(word in text_lower for word in ['ai', 'artificial intelligence', 'machine learning', 'bot', 'gpt']):
            extracted['project_type'] = 'AI Solution'
            
        # 5. Budget Heuristics
        if '$' in text or 'budget' in text_lower or 'k' in text_lower:
            budget_match = re.search(r'\$?\d+[kKmM]?', text)
            if budget_match:
                extracted['budget_range'] = budget_match.group(0)
                
        # Requirements (capture text that isn't just a tiny greeting)
        if len(text.split()) > 7 and 'project_type' in extracted:
            extracted['requirements'] = text
            
        return extracted
