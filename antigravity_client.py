"""
Jednoduchý ukázkový skript pro Antigravity SDK.
Vytvoří agenta, pošle mu zprávu a vypíše odpověď.

Instalace:
    pip install google-antigravity
"""

import asyncio
import os
from google.antigravity import Agent, LocalAgentConfig


async def main():
    # Načti API klíč z prostředí (nikdy nepiš klíč přímo do kódu)
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "Chybí GEMINI_API_KEY. Nastav ho pomocí:\n"
            "  export GEMINI_API_KEY='tvůj-klíč'"
        )

    # Konfigurace agenta – minimální, bez zbytečných oprávnění
    config = LocalAgentConfig(
        api_key=api_key,
        system_instructions=(
            "Jsi přátelský pomocný asistent. "
            "Odpovídej stručně a česky."
        ),
    )

    print("🚀 Spouštím Antigravity agenta...")

    async with Agent(config) as agent:
        print("✅ Agent úspěšně inicializován.\n")

        # Odeslání jednoduché zprávy
        prompt = "Ahoj! Představ se a řekni, co umíš."
        print(f"👤 Uživatel: {prompt}\n")

        response = await agent.chat(prompt)
        text = await response.text()

        print(f"🤖 Agent: {text}")


if __name__ == "__main__":
    asyncio.run(main())
