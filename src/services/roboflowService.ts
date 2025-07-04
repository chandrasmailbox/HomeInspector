export interface RoboflowDetection {
  id: string;
  type: 'mold';
  severity: 'low' | 'medium' | 'high' | 'critical';
  confidence: number;
  location: {
    x: number;
    y: number;
    width: number;
    height: number;
  };
  description: string;
  recommendations: string[];
  class: string;
  rawPrediction: any;
}

export class RoboflowService {
  private rf: any = null;
  private model: any = null;
  private isInitialized = false;
  private apiKey: string | null = null;

  constructor(apiKey?: string) {
    this.apiKey = apiKey || null;
  }

  async initialize(apiKey: string): Promise<boolean> {
    try {
      // Store the API key
      this.apiKey = apiKey;
      
      // For demo mode, just mark as initialized without actual Roboflow connection
      if (apiKey === 'demo') {
        this.isInitialized = true;
        console.log('Demo mode initialized - Roboflow features disabled');
        return true;
      }

      // Dynamically import roboflow-js to avoid initialization issues
      const { Roboflow } = await import('roboflow-js');
      
      this.rf = new Roboflow({
        publishable_key: apiKey
      });
      
      // Load the mold detection model
      this.model = this.rf.model("research-placement/mouldy-wall-classification/2");
      this.isInitialized = true;
      
      console.log('Roboflow model initialized successfully');
      return true;
    } catch (error) {
      console.error('Failed to initialize Roboflow:', error);
      this.isInitialized = false;
      this.rf = null;
      this.model = null;
      throw new Error(`Roboflow initialization failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  isAvailable(): boolean {
    return this.isInitialized && (this.apiKey === 'demo' || this.model !== null);
  }

  async detectMold(imageElement: HTMLImageElement | HTMLCanvasElement): Promise<RoboflowDetection[]> {
    // If in demo mode, return mock detections
    if (this.apiKey === 'demo') {
      return this.generateMockDetections(imageElement);
    }

    if (!this.isAvailable() || !this.model) {
      throw new Error('Roboflow model not initialized');
    }

    try {
      const predictions = await this.model.detect(imageElement);
      
      if (!predictions || !Array.isArray(predictions) || predictions.length === 0) {
        return [];
      }

      return predictions.map((prediction: any, index: number) => {
        const confidence = prediction.confidence || 0;
        const width = prediction.width || 50;
        const height = prediction.height || 50;
        const x = prediction.x || 0;
        const y = prediction.y || 0;
        
        const area = (width * height) / (imageElement.width * imageElement.height);
        
        return {
          id: `mold_${Date.now()}_${index}`,
          type: 'mold' as const,
          severity: this.determineSeverity(confidence, area),
          confidence,
          location: {
            x: Math.max(0, Math.min(1, (x - width / 2) / imageElement.width)),
            y: Math.max(0, Math.min(1, (y - height / 2) / imageElement.height)),
            width: Math.min(1, width / imageElement.width),
            height: Math.min(1, height / imageElement.height)
          },
          description: this.generateDescription(prediction.class || 'mold', confidence),
          recommendations: this.getMoldRecommendations(this.determineSeverity(confidence, area)),
          class: prediction.class || 'mold',
          rawPrediction: prediction
        };
      });
    } catch (error) {
      console.error('Error during mold detection:', error);
      throw new Error(`Mold detection failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  private generateMockDetections(imageElement: HTMLImageElement | HTMLCanvasElement): RoboflowDetection[] {
    // Generate 0-2 mock detections for demo mode
    const numDetections = Math.floor(Math.random() * 3);
    const detections: RoboflowDetection[] = [];

    for (let i = 0; i < numDetections; i++) {
      const confidence = 0.6 + Math.random() * 0.3; // 60-90% confidence
      const area = 0.01 + Math.random() * 0.05; // 1-6% of image area
      
      detections.push({
        id: `demo_mold_${Date.now()}_${i}`,
        type: 'mold' as const,
        severity: this.determineSeverity(confidence, area),
        confidence,
        location: {
          x: Math.random() * 0.7 + 0.1, // 10-80% from left
          y: Math.random() * 0.7 + 0.1, // 10-80% from top
          width: Math.sqrt(area) + Math.random() * 0.1,
          height: Math.sqrt(area) + Math.random() * 0.1
        },
        description: `Demo: Mold growth detected with ${Math.round(confidence * 100)}% confidence`,
        recommendations: this.getMoldRecommendations(this.determineSeverity(confidence, area)),
        class: 'mold',
        rawPrediction: { demo: true, confidence, area }
      });
    }

    return detections;
  }

  private determineSeverity(confidence: number, area: number): 'low' | 'medium' | 'high' | 'critical' {
    if (confidence > 0.8 && area > 0.1) return 'critical';
    if (confidence > 0.7 || area > 0.05) return 'high';
    if (confidence > 0.6) return 'medium';
    return 'low';
  }

  private generateDescription(className: string, confidence: number): string {
    const confidencePct = Math.round(confidence * 100);
    
    const descriptions: Record<string, string> = {
      'mold': `Mold growth detected with ${confidencePct}% confidence`,
      'mouldy': `Moldy surface identified with ${confidencePct}% confidence`,
      'fungal': `Fungal growth observed with ${confidencePct}% confidence`
    };
    
    return descriptions[className.toLowerCase()] || `Mold-like substance detected with ${confidencePct}% confidence`;
  }

  private getMoldRecommendations(severity: string): string[] {
    const base = [
      "Identify and eliminate moisture source",
      "Improve ventilation in affected area",
      "Monitor for spread to adjacent areas"
    ];

    const specific: Record<string, string[]> = {
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
    };

    return [...base, ...(specific[severity] || [])];
  }
}