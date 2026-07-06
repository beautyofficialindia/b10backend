class AIProviderError(Exception):
    pass


class AIProviderConfigurationError(AIProviderError):
    pass


class AIProviderTimeoutError(AIProviderError):
    pass
