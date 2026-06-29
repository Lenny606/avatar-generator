import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from PIL import ImageTk
import threading
import asyncio
import os
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
        self.show_faces_var = tk.BooleanVar(value=False)
        
        # Historie a Galerie
        self.history = []
        self.redo_stack = []
        self.gallery_images = []

        self._setup_ui()
        self._update_camera_loop()

    def _setup_ui(self):
        # Hlavní rozvržení
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Galerie (dole)
        self._setup_gallery()

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
        
        # Undo / Redo
        history_frame = ttk.Frame(self.control_frame)
        history_frame.pack(fill=tk.X, pady=5)
        ttk.Button(history_frame, text="⟲ Zpět", command=self._undo).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(history_frame, text="⟳ Vpřed", command=self._redo).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Checkbutton(self.control_frame, text="Zobrazovat obličeje", variable=self.show_faces_var).pack(fill=tk.X, pady=2)

        ttk.Separator(self.control_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)

        # Jednoduché úpravy
        adjust_frame = ttk.LabelFrame(self.control_frame, text="Základní úpravy", padding="5")
        adjust_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(adjust_frame, text="Zvýšit jas", command=lambda: self._apply_adjustment("brightness", 1.2)).pack(fill=tk.X, pady=2)
        ttk.Button(adjust_frame, text="Zvýšit kontrast", command=lambda: self._apply_adjustment("contrast", 1.2)).pack(fill=tk.X, pady=2)
        ttk.Button(adjust_frame, text="Oříznout na obličej", command=self._auto_crop_face).pack(fill=tk.X, pady=2)

        # Filtry
        filter_frame = ttk.LabelFrame(self.control_frame, text="Umělecké filtry", padding="5")
        filter_frame.pack(fill=tk.X, pady=5)

        ttk.Button(filter_frame, text="Černobílá", command=self._make_bw).pack(fill=tk.X, pady=2)
        ttk.Button(filter_frame, text="Skica (Tužka)", command=lambda: self._apply_filter("sketch")).pack(fill=tk.X, pady=2)
        ttk.Button(filter_frame, text="Sépie", command=lambda: self._apply_filter("sepia")).pack(fill=tk.X, pady=2)
        ttk.Button(filter_frame, text="Rozmazat", command=lambda: self._apply_filter("blur")).pack(fill=tk.X, pady=2)

        # Doplňky (Stickers)
        sticker_frame = ttk.LabelFrame(self.control_frame, text="Doplňky", padding="5")
        sticker_frame.pack(fill=tk.X, pady=5)
        
        self.sticker_var = tk.StringVar()
        self.sticker_combo = ttk.Combobox(sticker_frame, textvariable=self.sticker_var, state="readonly")
        self.sticker_combo.pack(fill=tk.X, pady=2)
        self._update_sticker_list()
        
        ttk.Button(sticker_frame, text="Aplikovat doplňek", command=self._apply_sticker).pack(fill=tk.X, pady=2)
        ttk.Button(sticker_frame, text="Obnovit seznam", command=self._update_sticker_list).pack(fill=tk.X, pady=2)

        # AI úpravy
        ai_frame = ttk.LabelFrame(self.control_frame, text="AI Úpravy", padding="5")
        ai_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(ai_frame, text="Poskytovatel:").pack(fill=tk.X)
        self.ai_provider_var = tk.StringVar(value="gemini")
        self.ai_provider_combo = ttk.Combobox(ai_frame, textvariable=self.ai_provider_var, state="readonly")
        self.ai_provider_combo['values'] = AIService.get_available_providers()
        self.ai_provider_combo.pack(fill=tk.X, pady=2)

        ttk.Button(ai_frame, text="AI Upravit / Stylizovat", command=self._ai_edit_prompt).pack(fill=tk.X, pady=5)

        ttk.Separator(self.control_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)

        # Ukládání
        ttk.Button(self.control_frame, text="Uložit obrázek", command=self._save_image).pack(fill=tk.X, pady=20)

        self.status_var = tk.StringVar(value="Připraven")
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def _update_camera_loop(self):
        """Smyčka pro aktualizaci náhledu kamery."""
        if self.current_image is None:
            frame_img = self.camera.get_frame(draw_faces=self.show_faces_var.get())
            if frame_img:
                self._display_image(frame_img)
        
        self.root.after(10, self._update_camera_loop)

    def _display_image(self, pil_image):
        """Zobrazí obrázek v GUI."""
        display_img = ImageService.resize_for_display(pil_image)
        self.photo = ImageTk.PhotoImage(image=display_img)
        self.image_label.configure(image=self.photo)

    def _setup_gallery(self):
        self.gallery_labelframe = ttk.LabelFrame(self.root, text="Galerie (Poslední snímky)", padding="5")
        self.gallery_labelframe.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)
        
        self.gallery_canvas = tk.Canvas(self.gallery_labelframe, height=120)
        self.gallery_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(self.gallery_labelframe, orient=tk.HORIZONTAL, command=self.gallery_canvas.xview)
        scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.gallery_canvas.configure(xscrollcommand=scrollbar.set)
        
        self.gallery_inner_frame = ttk.Frame(self.gallery_canvas)
        self.gallery_canvas.create_window((0, 0), window=self.gallery_inner_frame, anchor="nw")
        
        self.gallery_inner_frame.bind("<Configure>", lambda e: self.gallery_canvas.configure(scrollregion=self.gallery_canvas.bbox("all")))

    def _add_to_gallery(self, pil_image):
        """Přidá obrázek do galerie."""
        thumb = pil_image.copy()
        thumb.thumbnail((100, 100))
        tk_thumb = ImageTk.PhotoImage(thumb)
        
        # Musíme udržet referenci na tk_thumb
        self.gallery_images.append((tk_thumb, pil_image))
        
        btn = ttk.Button(self.gallery_inner_frame, image=tk_thumb, command=lambda img=pil_image: self._load_from_gallery(img))
        btn.pack(side=tk.LEFT, padx=5)
        
        # Automatický posun na konec
        self.gallery_canvas.xview_moveto(1.0)

    def _load_from_gallery(self, pil_image):
        self._save_to_history()
        self.current_image = pil_image.copy()
        self._display_image(self.current_image)
        self.status_var.set("Načteno z galerie")

    def _save_to_history(self):
        if self.current_image:
            self.history.append(self.current_image.copy())
            if len(self.history) > 20:
                self.history.pop(0)
            self.redo_stack.clear()

    def _undo(self):
        if self.history:
            self.redo_stack.append(self.current_image.copy())
            self.current_image = self.history.pop()
            self._display_image(self.current_image)
            self.status_var.set("Krok zpět")

    def _redo(self):
        if self.redo_stack:
            self.history.append(self.current_image.copy())
            self.current_image = self.redo_stack.pop()
            self._display_image(self.current_image)
            self.status_var.set("Krok vpřed")

    def _capture_photo(self):
        self.current_image = self.camera.get_last_frame_as_image()
        if self.current_image:
            self._add_to_gallery(self.current_image)
            self._display_image(self.current_image)
            self.status_var.set("Fotka pořízena")

    def _resume_camera(self):
        self.current_image = None
        self.status_var.set("Kamera aktivní")

    def _apply_adjustment(self, adj_type, factor):
        if self.current_image:
            self._save_to_history()
            if adj_type == "brightness":
                self.current_image = ImageService.adjust_brightness(self.current_image, factor)
            elif adj_type == "contrast":
                self.current_image = ImageService.adjust_contrast(self.current_image, factor)
            self._display_image(self.current_image)

    def _make_bw(self):
        if self.current_image:
            self._save_to_history()
            self.current_image = ImageService.convert_to_bw(self.current_image)
            self._display_image(self.current_image)

    def _apply_filter(self, filter_type):
        if self.current_image:
            self._save_to_history()
            if filter_type == "sketch":
                self.current_image = ImageService.apply_sketch_filter(self.current_image)
            elif filter_type == "sepia":
                self.current_image = ImageService.apply_sepia_filter(self.current_image)
            elif filter_type == "blur":
                self.current_image = ImageService.apply_gaussian_blur(self.current_image)
            self._display_image(self.current_image)
            self.status_var.set(f"Filtr {filter_type} aplikován")

    def _auto_crop_face(self):
        if self.current_image:
            # Pro detekci potřebujeme frame v OpenCV formátu (nebo použít CameraService.detect_faces)
            # detect_faces bez argumentů použije last_frame
            faces = self.camera.detect_faces()
            if len(faces) > 0:
                self._save_to_history()
                self.current_image = ImageService.crop_to_face(self.current_image, faces)
                self._display_image(self.current_image)
                self.status_var.set("Oříznuto na obličej")
            else:
                messagebox.showinfo("Informace", "Na snímku nebyl detekován žádný obličej.")

    def _update_sticker_list(self):
        sticker_dir = "assets/stickers"
        if os.path.exists(sticker_dir):
            stickers = [f for f in os.listdir(sticker_dir) if f.lower().endswith('.png')]
            self.sticker_combo['values'] = stickers
            if stickers and not self.sticker_var.get():
                self.sticker_combo.current(0)
        else:
            self.sticker_combo['values'] = []

    def _apply_sticker(self):
        sticker_name = self.sticker_var.get()
        if not sticker_name:
            messagebox.showwarning("Varování", "Vyberte nejdříve doplňek!")
            return
            
        if self.current_image:
            self._save_to_history()
            sticker_path = os.path.join("assets/stickers", sticker_name)
            self.current_image = ImageService.overlay_sticker(self.current_image, sticker_path)
            self._display_image(self.current_image)
            self.status_var.set(f"Doplňek {sticker_name} aplikován")

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
            provider = self.ai_provider_var.get()
            client = AIService.get_client(provider)
            result_text = asyncio.run(client.edit_image(self.current_image, prompt))
            self.root.after(0, lambda: self._finish_ai_edit(result_text))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("AI Chyba", str(e)))
            self.root.after(0, lambda: self.status_var.set("Chyba AI"))

    def _finish_ai_edit(self, result_text, result_image=None):
        if result_image:
            self._save_to_history()
            self.current_image = result_image
            self._display_image(self.current_image)
            self._add_to_gallery(self.current_image)
        
        messagebox.showinfo("AI Odpověď", result_text)
        self.status_var.set("AI dokončeno")

    def on_close(self):
        self.camera.release()
        self.root.destroy()
