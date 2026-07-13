import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.test import Client
from apps.knowledge_base.models import KnowledgeEntry
from django.conf import settings

def main():
    settings.ALLOWED_HOSTS = ['testserver']
    client = Client(SERVER_NAME='testserver')
    print("Step 1: Set KNOWLEDGE_SOURCE=database")
    settings.KNOWLEDGE_SOURCE = 'db'

    print("Step 2: Create Knowledge Entry")
    entry = KnowledgeEntry.objects.create(
        category='service',
        title='OpenAI Office Hours',
        content='B10 Solutions provides AI consulting and cloud automation services.',
        status='published'
    )
    print(f"Created: {entry.title}")

    print("Step 3: Ask chatbot")
    response = client.post('/api/v1/chat/', {"message": "What services does B10 provide?"}, content_type='application/json')
    print("Chatbot Response:", response.json().get('response'))

    print("Step 4: Archive article and ask again")
    entry.status = 'archived'
    entry.save()
    response2 = client.post('/api/v1/chat/', {"message": "What services does B10 provide?"}, content_type='application/json')
    print("Chatbot Response after archiving:", response2.json().get('response'))

    print("Step 5: Switch KNOWLEDGE_SOURCE=json and ask again")
    settings.KNOWLEDGE_SOURCE = 'json'
    response3 = client.post('/api/v1/chat/', {"message": "What services does B10 provide?"}, content_type='application/json')
    print("Chatbot Response with JSON:", response3.json().get('response'))

    # Cleanup
    entry.delete()

if __name__ == '__main__':
    main()
