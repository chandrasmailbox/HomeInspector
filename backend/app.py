from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import cv2
import time
import random
import threading
import uuid
from datetime import datetime
import numpy as np
from config import config
from models.roboflow_detector import RoboflowMoldDetector
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Load configuration
env = os.environ.get('FLASK_ENV', 'development')
app.config.from_object(config[env])

# Configure CORS
CORS(app, origins=app.config['CORS_ORIGINS'])

# Create necessary directories
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['THUMBNAIL_FOLDER'], exist_ok=True)

# Initialize AI models
mold_detector = RoboflowMoldDetector(app.config['ROBOFLOW_API_KEY'])

# Global storage for analysis sessions
analysis_sessions = {}

class VideoAnalyzer:
    """Main video analysis class that coordinates different detection models"""
    
    def __init__(self):
        self.mold_detector = mold_detector
        
    def analyze_video(self, video_path: str, session_id: str):
        """Analyze video for defects using AI models"""
        try:
            logger.info(f"Starting analysis for session {session_id}")
            
            # Update session status
            analysis_sessions[session_id]['is_analyzing'] = True
            analysis_sessions[session_id]['started_at'] = datetime.now()
            
            # Open video
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                raise Exception("Could not open video file")
            
            # Get video properties
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            duration = total_frames / fps if fps > 0 else 0
            
            analysis_sessions[session_id].update({
                'total_frames': total_frames,
                'duration': duration,
                'fps': fps
            })
            
            frame_skip = app.config['FRAME_SKIP_RATIO']
            all_detections = []
            frame_number = 0
            processed_frames = 0
            
            logger.info(f"Processing video: {total_frames} frames, {duration:.1f}s duration")
            
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Process every Nth frame for efficiency
                if frame_number % frame_skip == 0:
                    processed_frames += 1
                    
                    # Update progress
                    progress = (frame_number / total_frames) * 100
                    analysis_sessions[session_id].update({
                        'progress': progress,
                        'current_frame': frame_number,
                        'processed_frames': processed_frames
                    })
                    
                    # Run AI detection models
                    frame_detections = []
                    
                    # Mold detection using Roboflow
                    if self.mold_detector.is_available():
                        mold_detections = self.mold_detector.detect_mold(frame, frame_number)
                        frame_detections.extend(mold_detections)
                    
                    # Add other detection methods here (cracks, water damage, etc.)
                    frame_detections.extend(self._detect_other_defects(frame, frame_number))
                    
                    # Add timestamp information
                    timestamp = (frame_number / total_frames) * duration
                    for detection in frame_detections:
                        detection['timestamp'] = timestamp
                        detection['video_timestamp'] = frame_number / fps if fps > 0 else 0
                    
                    all_detections.extend(frame_detections)
                    
                    # Generate thumbnails for significant detections
                    for detection in frame_detections:
                        if detection['confidence'] > 0.7:  # Only for high-confidence detections
                            self._generate_thumbnail(frame, detection, session_id)
                
                frame_number += 1
                
                # Simulate processing time
                time.sleep(0.01)
            
            cap.release()
            
            # Compile final results
            results = self._compile_results(session_id, all_detections, processed_frames)
            
            # Update session with results
            analysis_sessions[session_id].update({
                'is_analyzing': False,
                'progress': 100,
                'completed_at': datetime.now(),
                'results': results
            })
            
            logger.info(f"Analysis completed for session {session_id}. Found {len(all_detections)} defects.")
            
        except Exception as e:
            logger.error(f"Analysis failed for session {session_id}: {e}")
            analysis_sessions[session_id].update({
                'is_analyzing': False,
                'error': str(e),
                'completed_at': datetime.now()
            })
    
    def _detect_other_defects(self, frame: np.ndarray, frame_number: int):
        """Detect other types of defects (cracks, water damage, etc.)"""
        # This is where you would add other detection algorithms
        # For now, we'll use simplified computer vision techniques
        
        detections = []
        
        # Simple crack detection using edge detection
        crack_detections = self._detect_cracks_cv(frame, frame_number)
        detections.extend(crack_detections)
        
        # Simple water damage detection using color analysis
        water_detections = self._detect_water_damage_cv(frame, frame_number)
        detections.extend(water_detections)
        
        return detections
    
    def _detect_cracks_cv(self, frame: np.ndarray, frame_number: int):
        """Simple crack detection using OpenCV"""
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            edges = cv2.Canny(blurred, 50, 150)
            
            # Find contours
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            detections = []
            height, width = frame.shape[:2]
            
            for i, contour in enumerate(contours):
                # Filter contours by area and aspect ratio
                area = cv2.contourArea(contour)
                if area < 100:  # Too small
                    continue
                
                # Get bounding rectangle
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = w / h if h > 0 else 0
                
                # Look for linear features (potential cracks)
                if aspect_ratio > 3 or aspect_ratio < 0.3:
                    confidence = min(0.8, area / 1000)  # Simple confidence based on size
                    
                    if confidence > 0.4:  # Minimum threshold
                        detection = {
                            'id': f"crack_{frame_number}_{i}",
                            'type': 'crack',
                            'severity': 'medium' if confidence > 0.6 else 'low',
                            'confidence': confidence,
                            'frame_number': frame_number,
                            'location': {
                                'x': x / width,
                                'y': y / height,
                                'width': w / width,
                                'height': h / height
                            },
                            'description': f"Potential structural crack detected (confidence: {int(confidence*100)}%)",
                            'recommendations': [
                                "Monitor crack for expansion over time",
                                "Consider professional structural assessment",
                                "Seal crack to prevent water intrusion"
                            ]
                        }
                        detections.append(detection)
            
            return detections
            
        except Exception as e:
            logger.error(f"Error in crack detection: {e}")
            return []
    
    def _detect_water_damage_cv(self, frame: np.ndarray, frame_number: int):
        """Simple water damage detection using color analysis"""
        try:
            # Convert to HSV for better color analysis
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            
            # Define range for water stain colors (browns, yellows)
            lower_stain = np.array([10, 50, 50])
            upper_stain = np.array([30, 255, 200])
            
            mask = cv2.inRange(hsv, lower_stain, upper_stain)
            
            # Morphological operations to clean up
            kernel = np.ones((5, 5), np.uint8)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            
            # Find contours
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            detections = []
            height, width = frame.shape[:2]
            
            for i, contour in enumerate(contours):
                area = cv2.contourArea(contour)
                if area < 500:  # Too small to be significant
                    continue
                
                x, y, w, h = cv2.boundingRect(contour)
                confidence = min(0.7, area / 5000)  # Simple confidence based on size
                
                if confidence > 0.3:
                    detection = {
                        'id': f"water_{frame_number}_{i}",
                        'type': 'water_leak',
                        'severity': 'high' if confidence > 0.5 else 'medium',
                        'confidence': confidence,
                        'frame_number': frame_number,
                        'location': {
                            'x': x / width,
                            'y': y / height,
                            'width': w / width,
                            'height': h / height
                        },
                        'description': f"Potential water damage or staining detected (confidence: {int(confidence*100)}%)",
                        'recommendations': [
                            "Investigate source of moisture",
                            "Check for active leaks in area",
                            "Consider professional water damage assessment",
                            "Monitor for mold development"
                        ]
                    }
                    detections.append(detection)
            
            return detections
            
        except Exception as e:
            logger.error(f"Error in water damage detection: {e}")
            return []
    
    def _generate_thumbnail(self, frame: np.ndarray, detection: dict, session_id: str):
        """Generate thumbnail image for a detection"""
        try:
            # Extract region of interest
            height, width = frame.shape[:2]
            loc = detection['location']
            
            x1 = int(loc['x'] * width)
            y1 = int(loc['y'] * height)
            x2 = int((loc['x'] + loc['width']) * width)
            y2 = int((loc['y'] + loc['height']) * height)
            
            # Add some padding
            padding = 20
            x1 = max(0, x1 - padding)
            y1 = max(0, y1 - padding)
            x2 = min(width, x2 + padding)
            y2 = min(height, y2 + padding)
            
            roi = frame[y1:y2, x1:x2]
            
            if roi.size > 0:
                # Resize to standard thumbnail size
                thumbnail = cv2.resize(roi, (150, 150))
                
                # Save thumbnail
                thumbnail_filename = f"{session_id}_{detection['id']}.jpg"
                thumbnail_path = os.path.join(app.config['THUMBNAIL_FOLDER'], thumbnail_filename)
                cv2.imwrite(thumbnail_path, thumbnail)
                
                # Update detection with thumbnail path
                detection['thumbnail'] = f"/api/thumbnail/{thumbnail_filename}"
                
        except Exception as e:
            logger.error(f"Error generating thumbnail: {e}")
    
    def _compile_results(self, session_id: str, detections: list, processed_frames: int):
        """Compile final analysis results"""
        session = analysis_sessions[session_id]
        
        # Calculate summary statistics
        total_defects = len(detections)
        critical_defects = len([d for d in detections if d['severity'] == 'critical'])
        high_defects = len([d for d in detections if d['severity'] == 'high'])
        
        # Calculate risk score
        risk_score = self._calculate_risk_score(detections)
        
        return {
            'id': session_id,
            'filename': session['filename'],
            'duration': session.get('duration', 0),
            'total_frames': session.get('total_frames', 0),
            'analyzed_frames': processed_frames,
            'defects': detections,
            'summary': {
                'total_defects': total_defects,
                'critical_defects': critical_defects,
                'high_defects': high_defects,
                'risk_score': risk_score
            },
            'created_at': datetime.now().isoformat()
        }
    
    def _calculate_risk_score(self, detections: list) -> int:
        """Calculate overall risk score based on detections"""
        if not detections:
            return 0
        
        severity_weights = {'low': 1, 'medium': 3, 'high': 7, 'critical': 15}
        
        total_score = sum(
            severity_weights[d['severity']] * d['confidence'] 
            for d in detections
        )
        
        # Normalize to 0-100 scale
        max_possible = len(detections) * 15  # All critical with 100% confidence
        risk_score = min(100, int((total_score / max_possible) * 100)) if max_possible > 0 else 0
        
        return risk_score

# Initialize video analyzer
video_analyzer = VideoAnalyzer()

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": time.time(),
        "models_loaded": mold_detector.is_available(),
        "active_sessions": len([s for s in analysis_sessions.values() if s.get('is_analyzing', False)]),
        "roboflow_available": mold_detector.is_available()
    })

@app.route('/api/upload', methods=['POST'])
def upload_video():
    """Upload video for analysis"""
    try:
        if 'video' not in request.files:
            return jsonify({'error': 'No video file provided'}), 400
        
        file = request.files['video']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Generate session ID
        session_id = str(uuid.uuid4())
        
        # Save uploaded file
        filename = f"{session_id}_{file.filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Initialize session
        analysis_sessions[session_id] = {
            'session_id': session_id,
            'filename': file.filename,
            'filepath': filepath,
            'is_analyzing': False,
            'progress': 0,
            'current_frame': 0,
            'total_frames': 0,
            'processed_frames': 0,
            'created_at': datetime.now(),
            'started_at': None,
            'completed_at': None,
            'results': None,
            'error': None
        }
        
        # Start analysis in background thread
        thread = threading.Thread(
            target=video_analyzer.analyze_video,
            args=(filepath, session_id)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'session_id': session_id,
            'message': 'Analysis started',
            'filename': file.filename
        })
        
    except Exception as e:
        logger.error(f"Upload error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/status/<session_id>', methods=['GET'])
def get_analysis_status(session_id):
    """Get analysis progress status"""
    if session_id not in analysis_sessions:
        return jsonify({'error': 'Session not found'}), 404
    
    session = analysis_sessions[session_id]
    
    # Calculate estimated time remaining
    estimated_time_remaining = 0
    if session['is_analyzing'] and session['progress'] > 0:
        elapsed = (datetime.now() - session['started_at']).total_seconds()
        estimated_total = elapsed / (session['progress'] / 100)
        estimated_time_remaining = max(0, estimated_total - elapsed)
    
    return jsonify({
        'is_analyzing': session['is_analyzing'],
        'progress': session['progress'],
        'current_frame': session['current_frame'],
        'total_frames': session['total_frames'],
        'processed_frames': session.get('processed_frames', 0),
        'estimated_time_remaining': estimated_time_remaining,
        'error': session.get('error')
    })

@app.route('/api/results/<session_id>', methods=['GET'])
def get_analysis_results(session_id):
    """Get analysis results"""
    if session_id not in analysis_sessions:
        return jsonify({'error': 'Session not found'}), 404
    
    session = analysis_sessions[session_id]
    
    if session['is_analyzing']:
        return jsonify({'error': 'Analysis still in progress'}), 202
    
    if session.get('error'):
        return jsonify({'error': session['error']}), 500
    
    if not session.get('results'):
        return jsonify({'error': 'No results available'}), 404
    
    return jsonify(session['results'])

@app.route('/api/thumbnail/<filename>', methods=['GET'])
def get_thumbnail(filename):
    """Get thumbnail image"""
    try:
        thumbnail_path = os.path.join(app.config['THUMBNAIL_FOLDER'], filename)
        if os.path.exists(thumbnail_path):
            return send_file(thumbnail_path, mimetype='image/jpeg')
        else:
            return jsonify({'error': 'Thumbnail not found'}), 404
    except Exception as e:
        logger.error(f"Thumbnail error: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Check if Roboflow API key is configured
    if not mold_detector.is_available():
        logger.warning("Roboflow API key not configured. Mold detection will be limited.")
        logger.info("To enable Roboflow mold detection:")
        logger.info("1. Get API key from https://app.roboflow.com/settings/api")
        logger.info("2. Set ROBOFLOW_API_KEY environment variable")
        logger.info("3. Or add it to your .env file")
    
    app.run(debug=app.config['DEBUG'], port=5000)