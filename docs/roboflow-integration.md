# Roboflow Integration Guide

This guide explains how to integrate and use the Roboflow mold detection model in HomeInspector AI.

## Overview

HomeInspector AI now integrates with Roboflow's "mouldy-wall-classification" model to provide professional-grade mold detection capabilities. This replaces the simulated mold detection with real AI-powered analysis.

## Model Information

- **Model**: Mouldy Wall Classification v2
- **Provider**: Roboflow Universe
- **URL**: https://universe.roboflow.com/research-placement/mouldy-wall-classification/model/2
- **Capabilities**: Detects and classifies mold/mildew on wall surfaces

## Setup Instructions

### 1. Get Roboflow API Key

1. Visit [Roboflow](https://app.roboflow.com/)
2. Create an account or sign in
3. Go to [Settings > API](https://app.roboflow.com/settings/api)
4. Copy your API key

### 2. Configure Environment

Create a `.env` file in the `backend` directory:

```env
# Roboflow Configuration
ROBOFLOW_API_KEY=your-api-key-here

# Other settings
CONFIDENCE_THRESHOLD=0.5
FRAME_SKIP_RATIO=10
```

### 3. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

The new requirements include:
- `roboflow==1.1.9` - Roboflow Python SDK
- `python-dotenv==1.0.0` - Environment variable management

### 4. Start the Application

```bash
# Backend
cd backend
python app.py

# Frontend (in another terminal)
npm run dev
```

## Features

### Real-Time Mold Detection

The integration provides:

- **Accurate Detection**: Uses trained AI model for mold identification
- **Confidence Scoring**: Each detection includes confidence percentage
- **Bounding Boxes**: Precise location of mold areas
- **Severity Assessment**: Automatic severity classification based on size and confidence
- **Thumbnail Generation**: Visual thumbnails of detected mold areas

### Detection Capabilities

The model can detect:
- Black mold on walls
- Mildew growth
- Fungal contamination
- Surface mold colonies

### Severity Classification

Detections are automatically classified:

- **Critical**: High confidence (>80%) + Large area (>10%)
- **High**: High confidence (>70%) OR Large area (>5%)
- **Medium**: Medium confidence (>60%)
- **Low**: Lower confidence detections

## Configuration Options

### Confidence Threshold

Adjust detection sensitivity:

```python
# In backend/config.py
CONFIDENCE_THRESHOLD = 0.5  # 50% minimum confidence
```

### Frame Processing

Control analysis speed vs accuracy:

```python
# Process every 10th frame (faster)
FRAME_SKIP_RATIO = 10

# Process every 5th frame (more thorough)
FRAME_SKIP_RATIO = 5
```

## API Integration

### Detection Response Format

```json
{
  "id": "mold_123_0",
  "type": "mold",
  "severity": "high",
  "confidence": 0.87,
  "frame_number": 123,
  "timestamp": 45.2,
  "location": {
    "x": 0.3,
    "y": 0.4,
    "width": 0.15,
    "height": 0.12
  },
  "description": "Mold growth detected with 87% confidence",
  "recommendations": [
    "IMMEDIATE professional mold remediation required",
    "Identify and eliminate moisture source",
    "Improve ventilation in affected area"
  ],
  "thumbnail": "/api/thumbnail/session_mold_123_0.jpg"
}
```

### Health Check

Check if Roboflow integration is working:

```bash
curl http://localhost:5000/api/health
```

Response includes:
```json
{
  "status": "healthy",
  "models_loaded": true,
  "roboflow_available": true,
  "active_sessions": 0
}
```

## Troubleshooting

### Common Issues

#### 1. "Roboflow API key not configured"

**Solution**: Set the `ROBOFLOW_API_KEY` environment variable:

```bash
export ROBOFLOW_API_KEY=your-key-here
# Or add to .env file
```

#### 2. "Failed to initialize Roboflow model"

**Possible causes**:
- Invalid API key
- Network connectivity issues
- Roboflow service unavailable

**Solution**: Check API key and internet connection

#### 3. Slow Analysis

**Optimization options**:
- Increase `FRAME_SKIP_RATIO` (process fewer frames)
- Reduce video resolution before upload
- Lower `CONFIDENCE_THRESHOLD` for fewer detections

### Debug Mode

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Performance Considerations

### Processing Speed

- **Frame Skip Ratio**: Higher values = faster processing
- **Video Resolution**: Lower resolution = faster analysis
- **Confidence Threshold**: Higher threshold = fewer detections to process

### Accuracy vs Speed

| Setting | Speed | Accuracy | Use Case |
|---------|-------|----------|----------|
| Skip=5, Conf=0.3 | Slow | High | Detailed inspection |
| Skip=10, Conf=0.5 | Medium | Good | Standard analysis |
| Skip=20, Conf=0.7 | Fast | Lower | Quick screening |

## Future Enhancements

### Planned Features

1. **Custom Model Training**: Train on your specific mold types
2. **Batch Processing**: Analyze multiple videos simultaneously
3. **Real-time Streaming**: Live video analysis
4. **Advanced Filtering**: Filter by mold type, size, location

### Integration Opportunities

- **Other Roboflow Models**: Integrate additional defect detection models
- **Custom Datasets**: Train models on your specific inspection data
- **Ensemble Methods**: Combine multiple models for better accuracy

## Support

For issues with:
- **Roboflow Integration**: Check Roboflow documentation
- **API Key Issues**: Contact Roboflow support
- **Model Performance**: Review confidence thresholds and frame processing settings

## License and Usage

- **Roboflow Model**: Subject to Roboflow terms of service
- **API Usage**: Check your Roboflow plan limits
- **Commercial Use**: Verify licensing for production deployments