"""Module for interacting with the Anthropic API."""
from anthropic import Anthropic, AsyncAnthropic
from config.settings import settings

class AnthropicClient:
    """Client for interacting with the Anthropic API."""

    def __init__(self, model=None):
        """Initialize the Anthropic client."""
        self.client = Anthropic(api_key=settings.anthropic_api_key)
        self.model = model or settings.anthropic_model
        self.async_client = AsyncAnthropic(api_key=settings.anthropic_api_key)

    def complete(self, system_prompt, user_message, temperature=0.7, max_tokens=1000):
        """Synchronous completion"""
        try:
            response = self.client.messages.create(
                model=self.model,
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}],
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.content[0].text
        except (ValueError, SyntaxError, TypeError) as e:
            print(f"Error completing message: {e}")
            # Implement retry logic here
            return None

    async def complete_async(self, system_prompt, user_message, temperature=0.7, max_tokens=1000):
        """Asynchronous completion"""
        try:
            response = await self.async_client.messages.create(
                model=self.model,
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}],
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.content[0].text
        except (ValueError, SyntaxError, TypeError) as e:
            print(f"Error completing message: {e}")
            # Implement retry logic here
            return None
