import os
import cv2
import numpy as np
from roboflow import Roboflow
from typing import List, Dict, Any, Optional
import logging

class RoboflowMoldDetector:
    """
    Roboflow-based mold detection using the mouldy-wall-classification model
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Roboflow mold detector
        
        Args:
            api_key: Roboflow API key. If None, will try to get from environment
        """
        self.api_key = api_key or os.getenv('ROBOFLOW_API_KEY')
        self.model = None
        self.confidence_threshold = 0.5
        self.overlap_threshold = 0.5
        
        if not self.api_key:
            logging.warning("No Roboflow API key provided. Mold detection will be disabled.")
            return
            
        try:
            self._initialize_model()
        except Exception as e:
            logging.error(f"Failed to initialize Roboflow model: {e}")
            self.model = None
    
    def _initialize_model(self):
        """Initialize the Roboflow model"""
        try:
            rf = Roboflow(api_key=self.api_key)
            project = rf.workspace("research-placement").project("mouldy-wall-classification")
            self.model = project.version(2).model
            logging.info("Roboflow mold detection model initialized successfully")
        except Exception as e:
            logging.error(f"Error initializing Roboflow model: {e}")
            raise
    
    def is_available(self) -> bool:
        """Check if the model is available for use"""
        return self.model is not None
    
    def detect_mold(self, frame: np.ndarray, frame_number: int) -> List[Dict[str, Any]]:
        """
        Detect mold in a video frame using Roboflow model
        
        Args:
            frame: Input video frame as numpy array
            frame_number: Frame number for tracking
            
        Returns:
            List of mold detections with bounding boxes and confidence scores
        """
        if not self.is_available():
            return []
        
        try:
            # Convert frame to RGB (Roboflow expects RGB)
            if len(frame.shape) == 3 and frame.shape[2] == 3:
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            else:
                rgb_frame = frame
            
            # Get frame dimensions
            height, width = frame.shape[:2]
            
            # Run inference
            predictions = self.model.predict(
                rgb_frame,
                confidence=self.confidence_threshold,
                overlap=self.overlap_threshold
            )
            
            detections = []
            
            # Process predictions
            if hasattr(predictions, 'json') and predictions.json():
                for prediction in predictions.json()['predictions']:
                    # Extract bounding box coordinates
                    x_center = prediction['x']
                    y_center = prediction['y']
                    box_width = prediction['width']
                    box_height = prediction['height']
                    
                    # Convert to normalized coordinates (0-1)
                    x_norm = max(0, min(1, (x_center - box_width/2) / width))
                    y_norm = max(0, min(1, (y_center - box_height/2) / height))
                    width_norm = min(1 - x_norm, box_width / width)
                    height_norm = min(1 - y_norm, box_height / height)
                    
                    # Determine severity based on confidence and size
                    confidence = prediction['confidence']
                    area = width_norm * height_norm
                    severity = self._determine_severity(confidence, area)
                    
                    detection = {
                        'id': f"mold_{frame_number}_{len(detections)}",
                        'type': 'mold',
                        'severity': severity,
                        'confidence': confidence,
                        'frame_number': frame_number,
                        'location': {
                            'x': x_norm,
                            'y': y_norm,
                            'width': width_norm,
                            'height': height_norm
                        },
                        'description': self._generate_description(prediction, confidence),
                        'recommendations': self._get_mold_recommendations(severity),
                        'raw_prediction': prediction  # Store raw data for debugging
                    }
                    
                    detections.append(detection)
            
            logging.info(f"Frame {frame_number}: Detected {len(detections)} mold instances")
            return detections
            
        except Exception as e:
            logging.error(f"Error during mold detection on frame {frame_number}: {e}")
            return []
    
    def _determine_severity(self, confidence: float, area: float) -> str:
        """
        Determine severity based on confidence score and affected area
        
        Args:
            confidence: Model confidence score (0-1)
            area: Normalized area of detection (0-1)
            
        Returns:
            Severity level: 'low', 'medium', 'high', or 'critical'
        """
        # High confidence and large area = critical
        if confidence > 0.8 and area > 0.1:
            return 'critical'
        
        # High confidence or large area = high
        elif confidence > 0.7 or area > 0.05:
            return 'high'
        
        # Medium confidence = medium
        elif confidence > 0.6:
            return 'medium'
        
        # Low confidence = low
        else:
            return 'low'
    
    def _generate_description(self, prediction: Dict, confidence: float) -> str:
        """Generate human-readable description of the mold detection"""
        class_name = prediction.get('class', 'mold')
        confidence_pct = int(confidence * 100)
        
        descriptions = {
            'mold': f"Mold growth detected with {confidence_pct}% confidence",
            'mouldy': f"Moldy surface identified with {confidence_pct}% confidence",
            'fungal': f"Fungal growth observed with {confidence_pct}% confidence"
        }
        
        return descriptions.get(class_name.lower(), f"Mold-like substance detected with {confidence_pct}% confidence")
    
    def _get_mold_recommendations(self, severity: str) -> List[str]:
        """Get recommendations based on mold severity"""
        base_recommendations = [
            "Identify and eliminate moisture source",
            "Improve ventilation in affected area",
            "Monitor for spread to adjacent areas"
        ]
        
        severity_specific = {
            'critical': [
                "IMMEDIATE professional mold remediation required",
                "Evacuate area until professional assessment",
                "Contact certified mold remediation specialist",
                "Consider temporary relocation if extensive"
            ],
            'high': [
                "Professional mold remediation recommended",
                "Wear protective equipment when in area",
                "Schedule professional air quality testing",
                "Document extent for insurance purposes"
            ],
            'medium': [
                "Professional assessment recommended",
                "Clean with appropriate mold removal products",
                "Increase air circulation and dehumidification",
                "Monitor closely for expansion"
            ],
            'low': [
                "Clean affected area with mold removal solution",
                "Ensure proper ventilation",
                "Regular monitoring recommended",
                "Address any moisture issues promptly"
            ]
        }
        
        return base_recommendations + severity_specific.get(severity, [])
    
    def set_confidence_threshold(self, threshold: float):
        """Set the confidence threshold for detections"""
        self.confidence_threshold = max(0.1, min(1.0, threshold))
        logging.info(f"Mold detection confidence threshold set to {self.confidence_threshold}")
    
    def set_overlap_threshold(self, threshold: float):
        """Set the overlap threshold for non-maximum suppression"""
        self.overlap_threshold = max(0.1, min(1.0, threshold))
        logging.info(f"Mold detection overlap threshold set to {self.overlap_threshold}")