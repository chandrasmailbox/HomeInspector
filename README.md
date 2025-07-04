# HomeInspector AI

A comprehensive AI-powered house inspection application that uses computer vision to detect defects in house inspection videos.

## 🚀 Features

- **Real-time AI Analysis**: Uses computer vision models to detect defects in uploaded videos
- **Roboflow Integration**: Professional mold detection using Roboflow's trained AI model
- **Multiple Defect Types**: Detects mold, cracks, water damage, paint issues, and more
- **Interactive Video Player**: View detected defects with timestamp markers and thumbnails
- **Detailed Reports**: Generate comprehensive inspection reports with recommendations
- **Professional UI**: Modern, responsive interface designed for professional use

## 🏗️ Architecture

### Frontend (React + TypeScript)
- Modern React application with TypeScript
- Tailwind CSS for styling
- Real-time progress tracking
- Interactive video player with defect overlays
- Comprehensive reporting dashboard

### Backend (Python + Flask)
- Flask REST API for video processing
- **Roboflow Integration** for professional mold detection
- Computer vision using OpenCV
- Real-time defect detection algorithms
- Thumbnail extraction for detected defects
- Background processing with threading

## 🛠️ Setup Instructions

### Prerequisites
- Node.js 18+ and npm
- Python 3.8+
- Roboflow API key (for mold detection)

### 1. Get Roboflow API Key
1. Visit [Roboflow](https://app.roboflow.com/)
2. Create account and go to [Settings > API](https://app.roboflow.com/settings/api)
3. Copy your API key

### 2. Backend Setup
```bash
# Navigate to backend directory
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env

# Edit .env and add your Roboflow API key:
# ROBOFLOW_API_KEY=your-api-key-here

# Start the backend server
python app.py
```

### 3. Frontend Setup
```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

### 4. Access Application
- Frontend: http://localhost:5173
- Backend API: http://localhost:5000

## 🤖 AI Models Used

### Roboflow Mold Detection
- **Model**: Mouldy Wall Classification v2
- **Provider**: Roboflow Universe
- **Capabilities**: Professional-grade mold and mildew detection
- **URL**: https://universe.roboflow.com/research-placement/mouldy-wall-classification/model/2

### Computer Vision Techniques
- **Crack Detection**: Edge detection with Canny algorithm and morphological operations
- **Water Damage**: Color space analysis and texture detection
- **Paint Issues**: Surface analysis and color variance detection

## 🔍 Defect Types Detected

1. **Mold/Mildew** (Roboflow AI): Black mold, surface mold, fungal growth
2. **Structural Cracks**: Foundation cracks, wall cracks, ceiling cracks
3. **Water Damage**: Stains, leaks, moisture damage
4. **Paint Issues**: Peeling, blistering, adhesion failure
5. **Structural Damage**: Beam deflection, support issues
6. **Electrical Hazards**: Exposed wiring, panel issues

## 📊 API Endpoints

- `POST /api/upload` - Upload video for analysis
- `GET /api/status/<session_id>` - Get analysis progress
- `GET /api/results/<session_id>` - Get analysis results
- `GET /api/thumbnail/<filename>` - Get defect thumbnails
- `GET /api/health` - Backend health check (includes Roboflow status)

## ⚙️ Configuration

### Environment Variables (.env)
```env
# Roboflow API Configuration
ROBOFLOW_API_KEY=your-roboflow-api-key

# Analysis Settings
CONFIDENCE_THRESHOLD=0.5
FRAME_SKIP_RATIO=10

# Flask Settings
SECRET_KEY=your-secret-key
FLASK_DEBUG=true
```

### Performance Tuning
- **FRAME_SKIP_RATIO**: Process every Nth frame (higher = faster)
- **CONFIDENCE_THRESHOLD**: Minimum detection confidence (higher = fewer false positives)

## 🚀 Production Deployment

### Backend
- Use production WSGI server (Gunicorn)
- Configure proper logging
- Set up model caching
- Implement rate limiting

### Frontend
- Build for production: `npm run build`
- Deploy to CDN or static hosting
- Configure API endpoints for production

## 📚 Documentation

Complete documentation available in the `docs/` folder:

- [Installation Guide](./docs/installation-guide.md)
- [User Guide](./docs/user-guide.md)
- [API Documentation](./docs/api-documentation.md)
- [Roboflow Integration](./docs/roboflow-integration.md)
- [Windows Setup Guide](./docs/windows-setup.md)
- [Troubleshooting](./docs/troubleshooting.md)

## 🔧 Development

### Adding New Defect Types
1. Add detection algorithm in `backend/models/`
2. Update defect type definitions in `src/types/index.ts`
3. Add UI components for new defect type

### Improving Detection Accuracy
- Fine-tune existing algorithms
- Add custom trained models
- Implement ensemble methods
- Add preprocessing steps

## 🤝 Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines on:
- Code style and standards
- Pull request process
- Issue reporting
- Development setup

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

- **Documentation**: Check the `docs/` folder
- **Issues**: Create GitHub issues for bugs
- **Roboflow**: Visit [Roboflow documentation](https://docs.roboflow.com/) for model-specific help

---

**Note**: This application requires a Roboflow API key for full mold detection capabilities. Without it, the system will fall back to basic computer vision techniques.