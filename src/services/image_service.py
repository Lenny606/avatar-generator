from PIL import ImageEnhance

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
