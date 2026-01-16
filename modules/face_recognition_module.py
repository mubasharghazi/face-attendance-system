"""
Face Recognition Module
Handles face detection and recognition operations.
"""

import face_recognition
import cv2
import numpy as np
from typing import List, Tuple, Optional, Dict, Any
import time


class FaceRecognitionModule:
    """Manages face detection and recognition using face_recognition library."""
    
    def __init__(self, tolerance: float = 0.6, model: str = 'hog', 
                 process_every_n_frames: int = 2):
        """
        Initialize face recognition module.
        
        Args:
            tolerance: Recognition tolerance (lower is more strict)
            model: Detection model ('hog' or 'cnn')
            process_every_n_frames: Process every nth frame for performance
        """
        self.tolerance = tolerance
        self.model = model
        self.process_every_n_frames = process_every_n_frames
        self.frame_count = 0
        
        # Cache for known face encodings
        self.known_face_encodings = []
        self.known_face_names = []
        self.known_face_ids = []
    
    def load_known_faces(self, students: List[Dict[str, Any]]):
        """
        Load known faces from student database.
        
        Args:
            students: List of student dictionaries with face_encoding
        """
        self.known_face_encodings = []
        self.known_face_names = []
        self.known_face_ids = []
        
        for student in students:
            if 'face_encoding' in student and student['face_encoding'] is not None:
                self.known_face_encodings.append(student['face_encoding'])
                self.known_face_names.append(student['name'])
                self.known_face_ids.append(student['student_id'])
    
    def detect_faces(self, image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Detect faces in an image.
        
        Args:
            image: Input image (BGR format from OpenCV)
        
        Returns:
            List of face locations as (top, right, bottom, left)
        """
        try:
            # Convert BGR to RGB
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Detect faces
            face_locations = face_recognition.face_locations(rgb_image, model=self.model)
            
            return face_locations
        except Exception as e:
            print(f"Error detecting faces: {e}")
            return []
    
    def encode_face(self, image: np.ndarray, face_location: Optional[Tuple] = None) -> Optional[np.ndarray]:
        """
        Generate face encoding from image.
        
        Args:
            image: Input image (BGR format)
            face_location: Optional specific face location
        
        Returns:
            Face encoding array or None if no face found
        """
        try:
            # Convert BGR to RGB
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Get face encoding
            if face_location:
                encodings = face_recognition.face_encodings(rgb_image, [face_location])
            else:
                encodings = face_recognition.face_encodings(rgb_image)
            
            if encodings:
                return encodings[0]
            return None
        except Exception as e:
            print(f"Error encoding face: {e}")
            return None
    
    def recognize_faces(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """
        Recognize faces in an image.
        
        Args:
            image: Input image (BGR format)
        
        Returns:
            List of dictionaries with recognition results
        """
        self.frame_count += 1
        
        # Skip frames for performance
        if self.frame_count % self.process_every_n_frames != 0:
            return []
        
        try:
            # Convert BGR to RGB
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Resize for faster processing
            small_frame = cv2.resize(rgb_image, (0, 0), fx=0.5, fy=0.5)
            
            # Detect faces
            face_locations = face_recognition.face_locations(small_frame, model=self.model)
            face_encodings = face_recognition.face_encodings(small_frame, face_locations)
            
            results = []
            
            for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                # Scale back up face locations
                top *= 2
                right *= 2
                bottom *= 2
                left *= 2
                
                # Compare with known faces
                matches = face_recognition.compare_faces(
                    self.known_face_encodings, face_encoding, tolerance=self.tolerance
                )
                
                name = "Unknown"
                student_id = None
                confidence = 0.0
                
                if True in matches:
                    # Calculate face distances
                    face_distances = face_recognition.face_distance(
                        self.known_face_encodings, face_encoding
                    )
                    
                    best_match_index = np.argmin(face_distances)
                    
                    if matches[best_match_index]:
                        name = self.known_face_names[best_match_index]
                        student_id = self.known_face_ids[best_match_index]
                        # Convert distance to confidence (0-1 scale)
                        confidence = 1.0 - face_distances[best_match_index]
                
                results.append({
                    'location': (top, right, bottom, left),
                    'name': name,
                    'student_id': student_id,
                    'confidence': confidence,
                    'is_known': student_id is not None
                })
            
            return results
        except Exception as e:
            print(f"Error recognizing faces: {e}")
            return []
    
    def draw_face_boxes(self, image: np.ndarray, recognition_results: List[Dict[str, Any]]) -> np.ndarray:
        """
        Draw bounding boxes and labels on detected faces.
        
        Args:
            image: Input image
            recognition_results: List of recognition results
        
        Returns:
            Image with drawn boxes
        """
        output_image = image.copy()
        
        for result in recognition_results:
            top, right, bottom, left = result['location']
            name = result['name']
            confidence = result['confidence']
            is_known = result['is_known']
            
            # Choose color based on recognition
            if is_known:
                color = (0, 255, 0)  # Green for known faces
            else:
                color = (0, 0, 255)  # Red for unknown faces
            
            # Draw rectangle
            cv2.rectangle(output_image, (left, top), (right, bottom), color, 2)
            
            # Draw label background
            label = f"{name}"
            if is_known:
                label += f" ({confidence:.2%})"
            
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.6
            thickness = 1
            
            (text_width, text_height), baseline = cv2.getTextSize(
                label, font, font_scale, thickness
            )
            
            # Draw background rectangle for text
            cv2.rectangle(
                output_image,
                (left, bottom - text_height - 10),
                (right, bottom),
                color,
                -1
            )
            
            # Draw text
            cv2.putText(
                output_image,
                label,
                (left + 6, bottom - 6),
                font,
                font_scale,
                (255, 255, 255),
                thickness,
                cv2.LINE_AA
            )
        
        return output_image
    
    def validate_face_for_registration(self, image: np.ndarray) -> Tuple[bool, str, Optional[np.ndarray]]:
        """
        Validate that image contains exactly one face for registration.
        
        Args:
            image: Input image
        
        Returns:
            Tuple of (is_valid, message, face_encoding)
        """
        try:
            # Detect faces
            face_locations = self.detect_faces(image)
            
            if len(face_locations) == 0:
                return False, "No face detected in image. Please try again.", None
            
            if len(face_locations) > 1:
                return False, f"Multiple faces detected ({len(face_locations)}). Please ensure only one person is in frame.", None
            
            # Generate encoding
            face_encoding = self.encode_face(image, face_locations[0])
            
            if face_encoding is None:
                return False, "Failed to generate face encoding. Please try again.", None
            
            return True, "Face validated successfully.", face_encoding
        except Exception as e:
            return False, f"Error validating face: {str(e)}", None
    
    def set_tolerance(self, tolerance: float) -> bool:
        """
        Update recognition tolerance.
        
        Args:
            tolerance: New tolerance value (0.3-1.0)
        
        Returns:
            bool: True if tolerance was updated, False if invalid
        """
        if 0.3 <= tolerance <= 1.0:
            self.tolerance = tolerance
            return True
        return False
    
    def get_tolerance(self) -> float:
        """
        Get current recognition tolerance.
        
        Returns:
            Current tolerance value
        """
        return self.tolerance
    
    def reset_frame_count(self):
        """Reset frame counter."""
        self.frame_count = 0
