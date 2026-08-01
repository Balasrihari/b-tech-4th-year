"""OCR Service for processing image-based documents"""
import pytesseract
from PIL import Image
import io
from typing import Optional
from loguru import logger


class OCRService:
    """Service for extracting text from images using Tesseract OCR"""
    
    def __init__(self):
        self.supported_formats = ['.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif']
    
    def extract_text_from_image(
        self,
        image_data: bytes,
        language: str = 'eng',
        config: Optional[str] = None
    ) -> str:
        """
        Extract text from image data
        
        Args:
            image_data: Raw image bytes
            language: OCR language (default: 'eng')
            config: Tesseract configuration string
            
        Returns:
            Extracted text from image
        """
        try:
            # Open image from bytes
            image = Image.open(io.BytesIO(image_data))
            
            # Configure Tesseract options
            custom_config = config if config else '--oem 3 --psm 6'
            
            # Extract text
            text = pytesseract.image_to_string(
                image,
                lang=language,
                config=custom_config
            )
            
            logger.info(f"Successfully extracted {len(text)} characters from image")
            return text.strip()
            
        except Exception as e:
            logger.error(f"OCR extraction failed: {e}")
            raise
    
    def extract_text_with_confidence(
        self,
        image_data: bytes,
        language: str = 'eng'
    ) -> tuple[str, float]:
        """
        Extract text from image with confidence score
        
        Args:
            image_data: Raw image bytes
            language: OCR language
            
        Returns:
            Tuple of (extracted_text, confidence_score)
        """
        try:
            image = Image.open(io.BytesIO(image_data))
            
            # Get data with confidence
            data = pytesseract.image_to_data(
                image,
                lang=language,
                output_type=pytesseract.Output.DICT
            )
            
            # Calculate average confidence
            confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            # Extract text
            text = pytesseract.image_to_string(image, lang=language)
            
            logger.info(f"OCR confidence: {avg_confidence:.2f}%")
            return text.strip(), avg_confidence
            
        except Exception as e:
            logger.error(f"OCR extraction with confidence failed: {e}")
            raise
    
    def is_supported_format(self, file_extension: str) -> bool:
        """Check if file format is supported for OCR"""
        return file_extension.lower() in self.supported_formats
    
    def preprocess_image(self, image_data: bytes) -> bytes:
        """
        Preprocess image for better OCR results
        
        Args:
            image_data: Raw image bytes
            
        Returns:
            Preprocessed image bytes
        """
        try:
            image = Image.open(io.BytesIO(image_data))
            
            # Convert to grayscale
            if image.mode != 'L':
                image = image.convert('L')
            
            # Resize if too large (max 3000px)
            max_size = 3000
            if max(image.size) > max_size:
                ratio = max_size / max(image.size)
                new_size = tuple(int(dim * ratio) for dim in image.size)
                image = image.resize(new_size, Image.Resampling.LANCZOS)
            
            # Enhance contrast
            from PIL import ImageEnhance
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(2.0)
            
            # Convert back to bytes
            output = io.BytesIO()
            image.save(output, format='PNG')
            return output.getvalue()
            
        except Exception as e:
            logger.error(f"Image preprocessing failed: {e}")
            return image_data


# Global OCR service instance
ocr_service = OCRService()
