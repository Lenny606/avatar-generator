import tkinter as tk
from dotenv import load_dotenv
import os
import sys

# Přidání cesty k projektu do sys.path, aby fungovaly absolutní importy z 'src'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ui.app_window import AvatarAppWindow

def main():
    # Načtení proměnných prostředí
    load_dotenv()

    root = tk.Tk()
    app = AvatarAppWindow(root)
    
    # Nastavení korektního ukončení
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    
    root.mainloop()

if __name__ == "__main__":
    main()
