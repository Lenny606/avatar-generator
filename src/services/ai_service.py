import abc
import io
import os
from PIL import Image as PILImage
from google.antigravity import Agent, LocalAgentConfig, types

class BaseAIClient(abc.ABC):
    @abc.abstractmethod
    async def edit_image(self, image: PILImage.Image, prompt: str) -> str:
        """
        Odešle obrázek s promptem k AI a vrátí textovou odpověď.
        """
        pass

class GeminiAIClient(BaseAIClient):
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")

    async def edit_image(self, image: PILImage.Image, prompt: str) -> str:
        if not self.api_key:
            return "Chyba: Chybí API klíč (GEMINI_API_KEY)."

        # Konverze PIL Image na bytes
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='JPEG')
        img_bytes = img_byte_arr.getvalue()

        config = LocalAgentConfig(
            api_key=self.api_key,
            system_instructions="Jsi expert na úpravu fotografií a avatarů. "
                              "Uživatel ti pošle fotku a instrukce k její úpravě. "
                              "Popiš uživateli detailně, co bys s fotkou udělal, nebo mu poraď."
        )

        try:
            async with Agent(config) as agent:
                image_part = types.Image(data=img_bytes, mime_type="image/jpeg")
                response = await agent.chat([prompt, image_part])
                return await response.text()
        except Exception as e:
            return f"Chyba při volání AI: {str(e)}"

class OpenAIClient(BaseAIClient):
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")

    async def edit_image(self, image: PILImage.Image, prompt: str) -> str:
        if not self.api_key:
            return "Chyba: Chybí API klíč (OPENAI_API_KEY)."
        # Zde by byla reálná implementace přes openai SDK
        return f"OpenAI (DALL-E/GPT-4o): Simulované zpracování promptu '{prompt}'."

class StabilityAIClient(BaseAIClient):
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("STABILITY_API_KEY")

    async def edit_image(self, image: PILImage.Image, prompt: str) -> str:
        if not self.api_key:
            return "Chyba: Chybí API klíč (STABILITY_API_KEY)."
        # Zde by byla reálná implementace přes Stability AI API
        return f"Stability AI: Simulovaná stylizace obrazu dle '{prompt}'."

class AIService:
    _registry = {
        "gemini": GeminiAIClient,
        "openai": OpenAIClient,
        "stability": StabilityAIClient
    }

    @staticmethod
    def get_client(provider="gemini"):
        provider = provider.lower()
        if provider in AIService._registry:
            return AIService._registry[provider]()
        else:
            raise ValueError(f"Neznámý poskytovatel: {provider}")

    @staticmethod
    def get_available_providers():
        return list(AIService._registry.keys())
