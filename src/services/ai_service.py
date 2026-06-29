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
    async def edit_image(self, image: PILImage.Image, prompt: str) -> str:
        return f"OpenAI (simulace): Přijal jsem obrázek a prompt: '{prompt}'"

class AIService:
    @staticmethod
    def get_client(provider="gemini"):
        if provider == "gemini":
            return GeminiAIClient()
        elif provider == "openai":
            return OpenAIClient()
        else:
            raise ValueError(f"Neznámý poskytovatel: {provider}")
