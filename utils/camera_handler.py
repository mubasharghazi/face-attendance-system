"""
Camera Handler Module
Manages webcam operations.
"""

import cv2
import threading
from typing import Optional, Tuple
import numpy as np


class CameraHandler:
    """Handles camera capture and frame processing."""
    
    def __init__(self, camera_index: int = 0, width: int = 640, height: int = 480):
        """
        Initialize camera handler.
        
        Args:
            camera_index: Camera device index
            width: Frame width
            height: Frame height
        """
        self.camera_index = camera_index
        self.width = width
        self.height = height
        self.capture = None
        self.is_running = False
        self.current_frame = None
        self.lock = threading.Lock()
    
    def start(self) -> bool:
        """
        Start camera capture.
        
        Returns:
            bool: True if camera started successfully
        """
        try:
            self.capture = cv2.VideoCapture(self.camera_index)
            
            if not self.capture.isOpened():
                return False
            
            # Set resolution
            self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            
            self.is_running = True
            return True
        except Exception as e:
            print(f"Error starting camera: {e}")
            return False
    
    def stop(self):
        """Stop camera capture and release resources."""
        self.is_running = False
        if self.capture is not None:
            self.capture.release()
            self.capture = None
        self.current_frame = None
    
    def read_frame(self) -> Optional[np.ndarray]:
        """
        Read a frame from the camera.
        
        Returns:
            Frame as numpy array or None if failed
        """
        if not self.is_running or self.capture is None:
            return None
        
        try:
            ret, frame = self.capture.read()
            if ret:
                with self.lock:
                    self.current_frame = frame.copy()
                return frame
            return None
        except Exception as e:
            print(f"Error reading frame: {e}")
            return None
    
    def get_current_frame(self) -> Optional[np.ndarray]:
        """
        Get the current frame (thread-safe).
        
        Returns:
            Current frame or None
        """
        with self.lock:
            if self.current_frame is not None:
                return self.current_frame.copy()
        return None
    
    def is_available(self) -> bool:
        """
        Check if camera is available.
        
        Returns:
            bool: True if camera is available
        """
        return self.is_running and self.capture is not None and self.capture.isOpened()
    
    def capture_frame(self) -> Optional[np.ndarray]:
        """
        Capture a single frame.
        
        Returns:
            Captured frame or None
        """
        return self.read_frame()
    
    @staticmethod
    def get_available_cameras(max_tested: int = 10) -> list[int]:
        """
        Get list of available camera indices.
        
        Args:
            max_tested: Maximum number of camera indices to test
        
        Returns:
            List of available camera indices
        """
        available = []
        for i in range(max_tested):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                available.append(i)
                cap.release()
        return available
    
    def set_resolution(self, width: int, height: int) -> bool:
        """
        Change camera resolution.
        
        Args:
            width: New width
            height: New height
        
        Returns:
            bool: True if successful
        """
        if self.capture is None:
            return False
        
        try:
            self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            self.width = width
            self.height = height
            return True
        except Exception as e:
            print(f"Error setting resolution: {e}")
            return False
