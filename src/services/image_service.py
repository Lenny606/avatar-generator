import os
from PIL import Image, ImageEnhance, ImageFilter, ImageOps

class ImageService:
    @staticmethod
    def adjust_brightness(image, factor):
        """Upraví jas obrázku."""
        if image:
            enhancer = ImageEnhance.Brightness(image)
            return enhancer.enhance(factor)
        return None

    @staticmethod
    def adjust_contrast(image, factor):
        """Upraví kontrast obrázku."""
        if image:
            enhancer = ImageEnhance.Contrast(image)
            return enhancer.enhance(factor)
        return None

    @staticmethod
    def convert_to_bw(image):
        """Převede obrázek na černobílý (RGB)."""
        if image:
            return image.convert("L").convert("RGB")
        return None

    @staticmethod
    def resize_for_display(image, max_size=(800, 600)):
        """Změní velikost obrázku pro náhled při zachování poměru stran."""
        if image:
            img_copy = image.copy()
            img_copy.thumbnail(max_size)
            return img_copy
        return None

    @staticmethod
    def crop_to_face(image, face_coords, padding=0.4):
        """Ořízne obrázek na detekovaný obličej ve čtvercovém formátu."""
        if not image or len(face_coords) == 0:
            return image

        # Najít největší obličej (předpokládáme, že face_coords jsou (x, y, w, h))
        x, y, w, h = max(face_coords, key=lambda f: f[2] * f[3])

        # Výpočet středu a rozměru pro čtvercový ořez
        cx, cy = x + w // 2, y + h // 2
        side = int(max(w, h) * (1 + padding))
        
        left = max(0, cx - side // 2)
        top = max(0, cy - side // 2)
        right = min(image.width, cx + side // 2)
        bottom = min(image.height, cy + side // 2)
        
        return image.crop((left, top, right, bottom))

    @staticmethod
    def apply_sketch_filter(image):
        """Aplikuje filtr 'skica' (tužková kresba)."""
        if not image:
            return None
        # Převod na grayscale a nalezení hran
        edges = image.convert("L").filter(ImageFilter.FIND_EDGES)
        # Invertovat barvy, aby byly čáry černé na bílém
        return ImageOps.invert(edges).convert("RGB")

    @staticmethod
    def apply_sepia_filter(image):
        """Aplikuje sépiový filtr."""
        if not image:
            return None
        sepia_matrix = (
            0.393, 0.769, 0.189, 0,
            0.349, 0.686, 0.168, 0,
            0.272, 0.534, 0.131, 0
        )
        return image.convert("RGB", sepia_matrix)

    @staticmethod
    def apply_gaussian_blur(image, radius=5):
        """Aplikuje Gaussovské rozmazání."""
        if not image:
            return None
        return image.filter(ImageFilter.GaussianBlur(radius=radius))

    @staticmethod
    def overlay_sticker(base_image, sticker_path, scale=0.3):
        """Překryje hlavní obrázek nálepkou (stickerem)."""
        if not base_image or not os.path.exists(sticker_path):
            return base_image
        
        sticker = Image.open(sticker_path).convert("RGBA")
        
        # Změna velikosti stickeru relativně k hlavnímu obrázku
        new_width = int(base_image.width * scale)
        aspect_ratio = sticker.height / sticker.width
        new_height = int(new_width * aspect_ratio)
        sticker = sticker.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Výchozí pozice (uprostřed)
        position = (
            (base_image.width - sticker.width) // 2,
            (base_image.height - sticker.height) // 2
        )
            
        # Vložení stickeru s využitím alfa kanálu
        result = base_image.convert("RGBA")
        overlay = Image.new("RGBA", result.size, (0, 0, 0, 0))
        overlay.paste(sticker, position)
        
        combined = Image.alpha_composite(result, overlay)
        return combined.convert("RGB")
