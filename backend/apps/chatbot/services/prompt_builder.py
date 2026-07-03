from .knowledge_loader import KnowledgeLoader

class PromptBuilder:
    def __init__(self):
        self.knowledge_loader = KnowledgeLoader()

    def build_system_prompt(self, user_message):
        # Keyword-based intent classification
        user_message_lower = user_message.lower()
        
        load_company = False
        load_services = False
        load_industries = False
        load_faq = False
        load_contact = False
        
        # Simple heuristics
        if any(word in user_message_lower for word in ['who', 'about', 'company', 'mission', 'founded']):
            load_company = True
        if any(word in user_message_lower for word in ['service', 'web', 'mobile', 'ai', 'develop']):
            load_services = True
        if any(word in user_message_lower for word in ['industry', 'healthcare', 'finance', 'ecommerce', 'e-commerce']):
            load_industries = True
        if any(word in user_message_lower for word in ['how long', 'timeline', 'cost', 'price', 'support', 'startup', 'faq']):
            load_faq = True
        if any(word in user_message_lower for word in ['contact', 'email', 'phone', 'address', 'book', 'call']):
            load_contact = True
            
        # Fallback: if no clear intent, load company and services as defaults
        if not any([load_company, load_services, load_industries, load_faq, load_contact]):
            load_company = True
            load_services = True
            load_faq = True
            
        knowledge_text = self.knowledge_loader.get_scoped_knowledge_as_text(
            company=load_company,
            services=load_services,
            industries=load_industries,
            faq=load_faq,
            contact=load_contact
        )
        
        system_prompt = f"""You are the official AI Business Consultant for B10 IT Solution.

Your purpose is to help visitors understand:
- B10 IT Solution
- Company information
- Services offered
- Industries served
- Engagement process
- Consultation process
- Contact information
- Project requirements gathering

Use ONLY the provided Knowledge Base.

Knowledge Base:
{knowledge_text}

Never answer:
- General coding questions
- Homework
- Recipes
- Medical advice
- Legal advice
- Financial advice
- Politics
- Entertainment
- Sports
- General knowledge unrelated to B10 IT Solution

If a question is outside your scope:
1. Politely refuse.
2. State that you are a business consultant for B10 IT Solution.
3. Redirect the conversation toward how B10 IT Solution can help.

Never invent information.
Never claim services that are not present in the Knowledge Base.
If information is unavailable, admit that you do not know and offer a consultation or contact option.
Keep responses concise, professional, and helpful.
"""
        return system_prompt

    def build_messages(self, history, user_message):
        messages = [
            {"role": "system", "content": self.build_system_prompt(user_message)}
        ]
        
        for msg in history:
            messages.append({"role": msg.role, "content": msg.content})
            
        messages.append({"role": "user", "content": user_message})
        return messages
