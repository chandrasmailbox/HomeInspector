import { Roboflow } from 'roboflow-js';

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

  constructor(private apiKey?: string) {
    if (apiKey) {
      this.initialize(apiKey);
    }
  }

  async initialize(apiKey: string): Promise<boolean> {
    try {
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
      return false;
    }
  }

  isAvailable(): boolean {
    return this.isInitialized && this.model !== null;
  }

  async detectMold(imageElement: HTMLImageElement | HTMLCanvasElement): Promise<RoboflowDetection[]> {
    if (!this.isAvailable()) {
      throw new Error('Roboflow model not initialized');
    }

    try {
      const predictions = await this.model.detect(imageElement);
      
      if (!predictions || !predictions.length) {
        return [];
      }

      return predictions.map((prediction: any, index: number) => {
        const confidence = prediction.confidence;
        const area = (prediction.width * prediction.height) / (imageElement.width * imageElement.height);
        
        return {
          id: `mold_${Date.now()}_${index}`,
          type: 'mold' as const,
          severity: this.determineSeverity(confidence, area),
          confidence,
          location: {
            x: (prediction.x - prediction.width / 2) / imageElement.width,
            y: (prediction.y - prediction.height / 2) / imageElement.height,
            width: prediction.width / imageElement.width,
            height: prediction.height / imageElement.height
          },
          description: this.generateDescription(prediction.class, confidence),
          recommendations: this.getMoldRecommendations(this.determineSeverity(confidence, area)),
          class: prediction.class,
          rawPrediction: prediction
        };
      });
    } catch (error) {
      console.error('Error during mold detection:', error);
      throw error;
    }
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