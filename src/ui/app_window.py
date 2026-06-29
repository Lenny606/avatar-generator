import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from PIL import ImageTk
import threading
import asyncio
from src.services.camera_service import CameraService
from src.services.image_service import ImageService
from src.services.ai_service import AIService

class AvatarAppWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Avatar Generator & Editor (Refactored)")
        self.root.geometry("1200x800")

        # Inicializace služeb
        self.camera = CameraService()
        if not self.camera.is_opened():
            messagebox.showerror("Chyba", "Nepodařilo se otevřít kameru.")
        
        self.current_image = None  # PIL Image objekt
        self.photo = None

        self._setup_ui()
        self._update_camera_loop()

    def _setup_ui(self):
        # Hlavní rozvržení
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Levý panel - Kamera / Obrázek
        self.view_frame = ttk.Frame(self.main_frame)
        self.view_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.image_label = ttk.Label(self.view_frame)
        self.image_label.pack(fill=tk.BOTH, expand=True)

        # Pravý panel - Ovládání
        self.control_frame = ttk.Frame(self.main_frame, width=300, padding="10")
        self.control_frame.pack(side=tk.RIGHT, fill=tk.Y)

        ttk.Label(self.control_frame, text="Ovládání", font=("Arial", 16, "bold")).pack(pady=10)

        # Tlačítka kamery
        ttk.Button(self.control_frame, text="Vyfotit", command=self._capture_photo).pack(fill=tk.X, pady=5)
        ttk.Button(self.control_frame, text="Zpět ke kameře", command=self._resume_camera).pack(fill=tk.X, pady=5)

        ttk.Separator(self.control_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)

        # Jednoduché úpravy
        ttk.Label(self.control_frame, text="Jednoduché úpravy", font=("Arial", 12, "bold")).pack(pady=5)
        
        ttk.Button(self.control_frame, text="Zvýšit jas", command=lambda: self._apply_adjustment("brightness", 1.2)).pack(fill=tk.X, pady=2)
        ttk.Button(self.control_frame, text="Zvýšit kontrast", command=lambda: self._apply_adjustment("contrast", 1.2)).pack(fill=tk.X, pady=2)
        ttk.Button(self.control_frame, text="Černobílá", command=self._make_bw).pack(fill=tk.X, pady=2)

        ttk.Separator(self.control_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)

        # AI úpravy
        ttk.Label(self.control_frame, text="AI Úpravy", font=("Arial", 12, "bold")).pack(pady=5)
        ttk.Button(self.control_frame, text="AI Upravit (Prompt)", command=self._ai_edit_prompt).pack(fill=tk.X, pady=5)

        ttk.Separator(self.control_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)

        # Ukládání
        ttk.Button(self.control_frame, text="Uložit obrázek", command=self._save_image).pack(fill=tk.X, pady=20)

        self.status_var = tk.StringVar(value="Připraven")
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def _update_camera_loop(self):
        """Smyčka pro aktualizaci náhledu kamery."""
        if self.current_image is None:
            frame_img = self.camera.get_frame()
            if frame_img:
                self._display_image(frame_img)
        
        self.root.after(10, self._update_camera_loop)

    def _display_image(self, pil_image):
        """Zobrazí obrázek v GUI."""
        display_img = ImageService.resize_for_display(pil_image)
        self.photo = ImageTk.PhotoImage(image=display_img)
        self.image_label.configure(image=self.photo)

    def _capture_photo(self):
        self.current_image = self.camera.get_last_frame_as_image()
        if self.current_image:
            self._display_image(self.current_image)
            self.status_var.set("Fotka pořízena")

    def _resume_camera(self):
        self.current_image = None
        self.status_var.set("Kamera aktivní")

    def _apply_adjustment(self, adj_type, factor):
        if self.current_image:
            if adj_type == "brightness":
                self.current_image = ImageService.adjust_brightness(self.current_image, factor)
            elif adj_type == "contrast":
                self.current_image = ImageService.adjust_contrast(self.current_image, factor)
            self._display_image(self.current_image)

    def _make_bw(self):
        if self.current_image:
            self.current_image = ImageService.convert_to_bw(self.current_image)
            self._display_image(self.current_image)

    def _save_image(self):
        if self.current_image:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".jpg", 
                filetypes=[("JPEG", "*.jpg"), ("PNG", "*.png")]
            )
            if file_path:
                self.current_image.save(file_path)
                messagebox.showinfo("Uloženo", f"Obrázek byl uložen do {file_path}")

    def _ai_edit_prompt(self):
        if not self.current_image:
            messagebox.showwarning("Varování", "Nejdříve pořiďte fotku!")
            return

        prompt = simpledialog.askstring("AI Editace", "Zadejte, co má AI s obrázkem udělat:")
        if prompt:
            self.status_var.set("AI zpracovává...")
            threading.Thread(target=self._run_ai_edit_thread, args=(prompt,), daemon=True).start()

    def _run_ai_edit_thread(self, prompt):
        try:
            client = AIService.get_client("gemini")
            result_text = asyncio.run(client.edit_image(self.current_image, prompt))
            self.root.after(0, lambda: self._finish_ai_edit(result_text))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("AI Chyba", str(e)))
            self.root.after(0, lambda: self.status_var.set("Chyba AI"))

    def _finish_ai_edit(self, result_text):
        messagebox.showinfo("AI Odpověď", result_text)
        self.status_var.set("AI dokončeno")

    def on_close(self):
        self.camera.release()
        self.root.destroy()
