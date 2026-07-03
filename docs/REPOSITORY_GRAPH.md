# REPOSITORY_GRAPH.md

Browser
    │
    ▼
Next.js Website
    │
    ▼
Chat Widget
    │
    ▼
POST /api/v1/chat
    │
    ▼
ChatAPIView
    │
    ▼
ChatService
    │
    ├── KnowledgeLoader
    ├── PromptBuilder
    ├── LeadService
    └── OpenRouterClient
            │
            ▼
      ResponseValidator
            │
            ▼
        Final Response