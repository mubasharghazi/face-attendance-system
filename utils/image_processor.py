"""
Image Processor Module
Image preprocessing and quality checks.
"""

import cv2
import numpy as np
from typing import Optional, Tuple
from PIL import Image


class ImageProcessor:
    """Handles image preprocessing and quality validation."""
    
    @staticmethod
    def preprocess_image(image: np.ndarray, target_size: Optional[Tuple[int, int]] = None) -> np.ndarray:
        """
        Preprocess image for face recognition.
        
        Args:
            image: Input image
            target_size: Target size (width, height) for resizing
        
        Returns:
            Preprocessed image
        """
        # Resize if target size specified
        if target_size:
            image = cv2.resize(image, target_size)
        
        # Convert to RGB if BGR
        if len(image.shape) == 3 and image.shape[2] == 3:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        return image
    
    @staticmethod
    def check_image_quality(image: np.ndarray) -> Tuple[bool, str]:
        """
        Check if image quality is sufficient for face recognition.
        
        Args:
            image: Input image
        
        Returns:
            Tuple of (is_good_quality, message)
        """
        # Check if image is too dark
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        mean_brightness = np.mean(gray)
        
        if mean_brightness < 40:
            return False, "Image is too dark. Please improve lighting."
        
        if mean_brightness > 240:
            return False, "Image is too bright. Please reduce lighting."
        
        # Check if image is blurry (using Laplacian variance)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        if laplacian_var < 100:
            return False, "Image is too blurry. Please hold steady and try again."
        
        # Check image size
        height, width = image.shape[:2]
        if width < 200 or height < 200:
            return False, "Image resolution is too low."
        
        return True, "Image quality is good."
    
    @staticmethod
    def enhance_image(image: np.ndarray) -> np.ndarray:
        """
        Enhance image for better face recognition.
        
        Args:
            image: Input image
        
        Returns:
            Enhanced image
        """
        # Apply histogram equalization to improve contrast
        if len(image.shape) == 3:
            # Convert to LAB color space
            lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            
            # Apply CLAHE to L channel
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            l = clahe.apply(l)
            
            # Merge channels
            enhanced = cv2.merge([l, a, b])
            enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
        else:
            # Grayscale image
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(image)
        
        return enhanced
    
    @staticmethod
    def resize_for_display(image: np.ndarray, max_width: int = 640, 
                          max_height: int = 480) -> np.ndarray:
        """
        Resize image for display while maintaining aspect ratio.
        
        Args:
            image: Input image
            max_width: Maximum width
            max_height: Maximum height
        
        Returns:
            Resized image
        """
        height, width = image.shape[:2]
        
        # Calculate scaling factor
        scale_w = max_width / width
        scale_h = max_height / height
        scale = min(scale_w, scale_h, 1.0)  # Don't upscale
        
        new_width = int(width * scale)
        new_height = int(height * scale)
        
        return cv2.resize(image, (new_width, new_height))
    
    @staticmethod
    def convert_cv_to_pil(image: np.ndarray) -> Image.Image:
        """
        Convert OpenCV image to PIL Image.
        
        Args:
            image: OpenCV image (BGR)
        
        Returns:
            PIL Image (RGB)
        """
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        return Image.fromarray(rgb_image)
    
    @staticmethod
    def convert_pil_to_cv(image: Image.Image) -> np.ndarray:
        """
        Convert PIL Image to OpenCV image.
        
        Args:
            image: PIL Image (RGB)
        
        Returns:
            OpenCV image (BGR)
        """
        rgb_array = np.array(image)
        return cv2.cvtColor(rgb_array, cv2.COLOR_RGB2BGR)
    
    @staticmethod
    def draw_text_with_background(image: np.ndarray, text: str, position: Tuple[int, int],
                                  font_scale: float = 0.6, thickness: int = 2,
                                  text_color: Tuple[int, int, int] = (255, 255, 255),
                                  bg_color: Tuple[int, int, int] = (0, 0, 0),
                                  padding: int = 5) -> np.ndarray:
        """
        Draw text with background on image.
        
        Args:
            image: Input image
            text: Text to draw
            position: Position (x, y)
            font_scale: Font scale
            thickness: Text thickness
            text_color: Text color (B, G, R)
            bg_color: Background color (B, G, R)
            padding: Padding around text
        
        Returns:
            Image with text
        """
        font = cv2.FONT_HERSHEY_SIMPLEX
        
        # Get text size
        (text_width, text_height), baseline = cv2.getTextSize(
            text, font, font_scale, thickness
        )
        
        x, y = position
        
        # Draw background rectangle
        cv2.rectangle(
            image,
            (x - padding, y - text_height - padding),
            (x + text_width + padding, y + baseline + padding),
            bg_color,
            -1
        )
        
        # Draw text
        cv2.putText(
            image,
            text,
            (x, y),
            font,
            font_scale,
            text_color,
            thickness,
            cv2.LINE_AA
        )
        
        return image
    
    @staticmethod
    def save_image(image: np.ndarray, filepath: str, quality: int = 95) -> bool:
        """
        Save image to file.
        
        Args:
            image: Image to save
            filepath: Output filepath
            quality: JPEG quality (0-100)
        
        Returns:
            bool: True if successful
        """
        try:
            cv2.imwrite(filepath, image, [cv2.IMWRITE_JPEG_QUALITY, quality])
            return True
        except Exception as e:
            print(f"Error saving image: {e}")
            return False
