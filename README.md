# AI Avatar Generator & Editor

Tato aplikace umožňuje uživatelům pořizovat fotografie pomocí webkamery, provádět základní úpravy obrazu a využívat umělou inteligenci (Google Gemini) pro pokročilou editaci nebo analýzu obrázků.

## Funkce

- **Kamera**: Živý náhled z kamery a zachycení snímku.
- **Základní úpravy**: Nastavení jasu, kontrastu a převod do černobílé podoby.
- **AI Editace**: Odeslání obrázku s textovým promptem do AI (Gemini) pro úpravu nebo radu.
- **Ukládání**: Možnost uložit výsledný obrázek ve formátu JPG nebo PNG.
- **Modulární architektura**: Rozdělení logiky na služby (Služba kamery, Služba obrazu, AI Služba) a uživatelské rozhraní.

## Architektura projektu

Projekt je strukturován pro dobrou čitelnost a snadnou rozšiřitelnost:

- `main.py`: Hlavní vstupní bod aplikace.
- `src/main.py`: Vnitřní inicializace GUI a načtení konfigurace.
- `src/ui/`: Obsahuje definici uživatelského rozhraní (Tkinter).
- `src/services/`: Obsahuje byznys logiku:
    - `camera_service.py`: Práce s OpenCV pro přístup ke kameře.
    - `image_service.py`: Úpravy obrázků pomocí knihovny Pillow.
    - `ai_service.py`: Klient pro AI (implementováno pro Gemini přes `google-antigravity`).
    - `ai_tools.py`: Sdílené nástroje pro AI agenty.
- `examples/`: Ukázkové skripty pro testování AI klienta samostatně.

## Instalace

1. Naklonujte repozitář.
2. Vytvořte virtuální prostředí a nainstalujte závislosti:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Pro Linux/macOS
   # nebo
   .venv\Scripts\activate     # Pro Windows
   pip install opencv-python Pillow google-antigravity python-dotenv
   ```
3. Vytvořte soubor `.env` (můžete zkopírovat `.env.example`) a vložte svůj API klíč:
   ```env
   GEMINI_API_KEY=vás_api_klíč
   ```

## Spuštění

Aplikaci spustíte pomocí:
```bash
python main.py
```

## Požadavky

- Python 3.12+
- Webkamera
- Internetové připojení (pro AI funkce)
- Nainstalované systémové knihovny pro Tkinter (pokud nejsou součástí distribuce Pythonu, např. `python3-tk` na Linuxu)
