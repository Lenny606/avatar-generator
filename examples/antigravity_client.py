"""
Ukázkový skript pro Antigravity SDK s vlastními Python nástroji (tools).
Agent může volat zaregistrované funkce označené dekorátorem @tool.

Instalace:
    pip install google-antigravity

Spuštění:
    export GEMINI_API_KEY='tvůj-klíč'
    .venv/bin/python examples/antigravity_client.py
"""

import asyncio
import os
import sys

# Přidání cesty k projektu
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google.antigravity import Agent, LocalAgentConfig
from src.services.ai_tools import get_weather, calculate, get_joke, get_system_info


# ─── Hlavní logika ────────────────────────────────────────────────────────────

async def main():
    # Načti API klíč z prostředí (nikdy nepiš klíč přímo do kódu)
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "Chybí GEMINI_API_KEY. Nastav ho pomocí:\n"
            "  export GEMINI_API_KEY='tvůj-klíč'"
        )

    # Konfigurace agenta s registrovanými nástroji
    config = LocalAgentConfig(
        api_key=api_key,
        system_instructions=(
            "Jsi přátelský asistent. Odpovídej česky a stručně. "
            "Máš k dispozici nástroje: get_weather, calculate, get_joke, get_system_info. "
            "Používej je aktivně při odpovídání na dotazy."
        ),
        tools=[get_weather, calculate, get_joke, get_system_info],
    )

    print("🚀 Spouštím Antigravity agenta s nástroji...")
    print(f"   Nástroje: get_weather | calculate | get_joke | get_system_info\n")

    async with Agent(config) as agent:
        print("✅ Agent úspěšně inicializován.\n")
        print("─" * 50)

        # Testovací dotazy – každý využije jiný nástroj
        prompts = [
            "Jaké je teď počasí v Praze a v Brně?",
            "Kolik je (42 * 7) + 13? A jaké je 100 / 4?",
            "Řekni mi vtip.",
            "Jaké informace máš o mém systému?",
        ]

        for prompt in prompts:
            print(f"👤 Uživatel: {prompt}")
            response = await agent.chat(prompt)
            text = await response.text()
            print(f"🤖 Agent:    {text}")
            print("─" * 50)


if __name__ == "__main__":
    asyncio.run(main())
