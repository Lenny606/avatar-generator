import random
import platform
from datetime import datetime
from google.antigravity import tool

@tool
def get_weather(city: str) -> str:
    """Vrátí fiktivní aktuální počasí pro zadané město."""
    conditions = ["Slunečno", "Oblačno", "Déšť", "Bouřka", "Mlha", "Sněžení"]
    temp = random.randint(-5, 38)
    condition = random.choice(conditions)
    return f"{city}: {condition}, {temp}°C (dummy data)"

@tool
def calculate(expression: str) -> str:
    """
    Vyhodnotí jednoduchý matematický výraz (sčítání, odčítání, násobení, dělení).
    """
    try:
        allowed = set("0123456789+-*/(). ")
        if not all(c in allowed for c in expression):
            return "Chyba: Výraz obsahuje nepodporované znaky."
        result = eval(expression, {"__builtins__": {}})  # noqa: S307
        return f"{expression} = {result}"
    except ZeroDivisionError:
        return "Chyba: Dělení nulou."
    except Exception as e:
        return f"Chyba při výpočtu: {e}"

@tool
def get_joke() -> str:
    """Vrátí náhodný programátorský vtip."""
    jokes = [
        "Proč programátoři preferují tmavý režim? Protože světlo přitahuje bugy.",
        "Jak se jmenuje pes programátora? Lassie = 'fetch'",
        "Kolik programátorů je potřeba na výměnu žárovky? Žádný, to je hardwarový problém.",
        "Rekurze: viz 'Rekurze'.",
        "99 malých bugů v kódu... oprav jeden, teď jich je 127.",
    ]
    return random.choice(jokes)

@tool
def get_system_info() -> dict:
    """Vrátí základní informace o systému: OS, Python verzi a aktuální čas."""
    return {
        "os": platform.system(),
        "os_version": platform.version(),
        "python": platform.python_version(),
        "architecture": platform.machine(),
        "current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
