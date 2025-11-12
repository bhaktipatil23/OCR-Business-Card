from pdf2image import convert_from_path
from PIL import Image
from typing import List
import os

class PDFConverter:
    
    @staticmethod
    def convert_pdf_to_images(pdf_path: str) -> List[Image.Image]:
        """Convert PDF pages to images"""
        try:
            images = convert_from_path(pdf_path, dpi=300)
            print(f"📄 Converted PDF to {len(images)} images")
            return images
        except Exception as e:
            print(f"❌ PDF conversion error: {e}")
            return []
    
    @staticmethod
    def preprocess_image(image: Image.Image) -> Image.Image:
        """Enhance image for better OCR"""
        # Convert to grayscale
        image = image.convert('L')
        
        # Resize if too large (max 2000px width)
        max_width = 2000
        if image.width > max_width:
            ratio = max_width / image.width
            new_size = (max_width, int(image.height * ratio))
            image = image.resize(new_size, Image.Resampling.LANCZOS)
        
        return image