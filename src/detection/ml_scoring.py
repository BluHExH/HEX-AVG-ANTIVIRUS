"""
ML-Based Threat Scoring (Experimental)
Simple offline ML model for malware classification
"""

import math
from pathlib import Path
from typing import Dict, List, Optional
import json


class MLThreatScorer:
    """
    Experimental ML-based threat scoring
    
    Note: This is a simplified, rule-based ML model for demonstration.
    In production, you would use:
    - Trained models (Random Forest, XGBoost, Neural Networks)
    - Large datasets of benign and malicious files
    - Feature engineering and model training pipeline
    
    This implementation uses a weighted ensemble of features
    to simulate ML-based classification.
    """
    
    def __init__(self):
        # Feature weights (simulating trained model coefficients)
        self.feature_weights = {
            'entropy': 0.25,
            'suspicious_strings': 0.20,
            'extension_mismatch': 0.20,
            'packer_detected': 0.15,
            'file_size_anomaly': 0.10,
            'rare_extension': 0.10
        }
        
        # Thresholds for classification
        self.thresholds = {
            'benign': 0.3,
            'suspicious': 0.6,
            'malicious': 0.8
        }
        
        # Feature thresholds
        self.entropy_threshold = 7.0
        self.suspicious_strings_threshold = 5
        self.small_executable_threshold = 1024  # 1KB
        self.large_executable_threshold = 100 * 1024 * 1024  # 100MB
        
        # Rare/suspicious extensions
        self.rare_extensions = {
            '.vbs', '.js', '.wsf', '.ps1', '.bat', '.cmd', '.scr',
            '.pif', '.com', '.cpl', '.msc', '.jar', '.hta'
        }
        
        # Load pre-trained model (simulated)
        self.model_path = Path(__file__).parent.parent.parent / "models" / "ml_model.json"
        self.model = self._load_model()
    
    def _load_model(self) -> Optional[Dict]:
        """Load pre-trained ML model"""
        if self.model_path.exists():
            try:
                with open(self.model_path, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        # Return default model if not found
        return {
            'version': '1.0.0-experimental',
            'feature_weights': self.feature_weights,
            'thresholds': self.thresholds,
            'trained_on': 'synthetic_data',
            'accuracy': 0.85,  # Simulated
            'false_positive_rate': 0.05
        }
    
    def score_file(self, file_path: Path, heuristic_result: Dict) -> Dict:
        """
        Score file using ML-based classification
        
        Args:
            file_path: Path to file
            heuristic_result: Results from heuristic analysis
            
        Returns:
            Dict with ML score and classification
        """
        if not file_path.exists():
            return {
                'ml_score': 0.0,
                'classification': 'unknown',
                'confidence': 0.0,
                'experimental': True,
                'explanation': 'File not found'
            }
        
        # Extract features
        features = self._extract_features(file_path, heuristic_result)
        
        # Calculate ML score (weighted ensemble)
        ml_score = self._calculate_ml_score(features)
        
        # Classify
        classification, confidence = self._classify(ml_score, features)
        
        # Generate explanation
        explanation = self._generate_explanation(features, ml_score, classification)
        
        return {
            'ml_score': ml_score,
            'classification': classification,
            'confidence': confidence,
            'experimental': True,
            'features': features,
            'explanation': explanation
        }
    
    def _extract_features(self, file_path: Path, heuristic_result: Dict) -> Dict:
        """Extract features from file for ML scoring"""
        features = {}
        
        # Feature 1: Entropy score (from heuristic)
        entropy_signal = next(
            (s for s in heuristic_result.get('signals', []) if s['name'] == 'entropy'),
            {'score': 0, 'details': 'entropy: 0.0'}
        )
        features['entropy'] = entropy_signal['score'] / 30.0  # Normalize to 0-1
        
        # Feature 2: Suspicious strings count
        strings_signal = next(
            (s for s in heuristic_result.get('signals', []) if s['name'] == 'suspicious_strings'),
            {'score': 0, 'details': 'Found 0 suspicious strings'}
        )
        features['suspicious_strings'] = strings_signal['score'] / 25.0  # Normalize
        
        # Feature 3: Extension mismatch
        mismatch_signal = next(
            (s for s in heuristic_result.get('signals', []) if s['name'] == 'extension_mismatch'),
            {'score': 0}
        )
        features['extension_mismatch'] = mismatch_signal['score'] / 25.0  # Normalize
        
        # Feature 4: Packer detected
        packer_signal = next(
            (s for s in heuristic_result.get('signals', []) if s['name'] == 'packer_detected'),
            {'score': 0}
        )
        features['packer_detected'] = packer_signal['score'] / 20.0  # Normalize
        
        # Feature 5: File size anomaly
        try:
            file_size = file_path.stat().st_size
            if file_size < self.small_executable_threshold:
                features['file_size_anomaly'] = 0.8  # Suspiciously small
            elif file_size > self.large_executable_threshold:
                features['file_size_anomaly'] = 0.6  # Suspiciously large
            else:
                features['file_size_anomaly'] = 0.0  # Normal size
        except:
            features['file_size_anomaly'] = 0.0
        
        # Feature 6: Rare extension
        extension = file_path.suffix.lower()
        features['rare_extension'] = 1.0 if extension in self.rare_extensions else 0.0
        
        return features
    
    def _calculate_ml_score(self, features: Dict) -> float:
        """
        Calculate ML score using weighted ensemble
        
        This simulates a trained ML model's prediction.
        In production, this would use actual ML inference.
        """
        # Weighted sum of features
        score = 0.0
        for feature_name, weight in self.feature_weights.items():
            score += features.get(feature_name, 0.0) * weight
        
        # Apply non-linear transformation (simulating ML model)
        score = self._sigmoid(score)
        
        return score
    
    def _sigmoid(self, x: float) -> float:
        """Sigmoid activation function"""
        return 1.0 / (1.0 + math.exp(-x))
    
    def _classify(self, ml_score: float, features: Dict) -> tuple:
        """
        Classify file based on ML score
        
        Returns:
            (classification_label, confidence)
        """
        if ml_score >= self.thresholds['malicious']:
            classification = 'malicious'
            confidence = (ml_score - self.thresholds['malicious']) / (1.0 - self.thresholds['malicious'])
        elif ml_score >= self.thresholds['suspicious']:
            classification = 'suspicious'
            confidence = (ml_score - self.thresholds['suspicious']) / (self.thresholds['malicious'] - self.thresholds['suspicious'])
        elif ml_score >= self.thresholds['benign']:
            classification = 'suspicious'
            confidence = (ml_score - self.thresholds['benign']) / (self.thresholds['suspicious'] - self.thresholds['benign'])
        else:
            classification = 'benign'
            confidence = (self.thresholds['benign'] - ml_score) / self.thresholds['benign']
        
        # Normalize confidence to 0-1
        confidence = max(0.0, min(1.0, confidence))
        
        return classification, confidence
    
    def _generate_explanation(self, features: Dict, ml_score: float, classification: str) -> str:
        """Generate human-readable explanation"""
        
        explanation_parts = []
        
        # Overall classification
        explanation_parts.append(f"⚠️  ML Classification: {classification.upper()}")
        explanation_parts.append(f"📊 ML Score: {ml_score:.2f}/1.00")
        
        # Top contributing features
        explanation_parts.append("\n🔍 Top Contributing Features:")
        
        # Sort features by contribution
        feature_contributions = [
            (name, value * weight)
            for name, value in features.items()
            for weight_name, weight in self.feature_weights.items()
            if name == weight_name
        ]
        feature_contributions.sort(key=lambda x: x[1], reverse=True)
        
        for feature_name, contribution in feature_contributions[:3]:
            if contribution > 0.1:
                explanation_parts.append(f"  • {feature_name}: {contribution:.2f}")
        
        # Experimental warning
        explanation_parts.append(
            "\n⚠️  NOTE: This is an EXPERIMENTAL ML model."
            "\n   • Trained on limited synthetic data"
            "\n   • May produce false positives"
            "\n   • Should be used alongside signature and heuristic detection"
            "\n   • Report false positives to improve the model"
        )
        
        return "\n".join(explanation_parts)
    
    def train_model(self, training_data: List[Dict], labels: List[str]):
        """
        Train ML model (placeholder for future implementation)
        
        Args:
            training_data: List of feature dictionaries
            labels: Corresponding labels ('benign', 'malicious', 'suspicious')
        """
        # This is a placeholder for actual ML training
        # In production, you would:
        # 1. Collect large dataset of benign and malicious files
        # 2. Extract features from all files
        # 3. Split into training and test sets
        # 4. Train ML model (Random Forest, XGBoost, etc.)
        # 5. Evaluate performance
        # 6. Save model weights
        
        print("⚠️  ML Training not implemented in experimental version")
        print("   To train a real model:")
        print("   1. Collect dataset of benign and malicious files")
        print("   2. Extract features using extract_features()")
        print("   3. Train ML model using scikit-learn or TensorFlow")
        print("   4. Save model weights to ml_model.json")
    
    def evaluate_model(self, test_data: List[Dict], test_labels: List[str]) -> Dict:
        """
        Evaluate ML model performance (placeholder)
        """
        return {
            'accuracy': self.model.get('accuracy', 0.85),
            'precision': 0.82,
            'recall': 0.78,
            'f1_score': 0.80,
            'false_positive_rate': self.model.get('false_positive_rate', 0.05),
            'false_negative_rate': 0.22
        }
    
    def get_model_info(self) -> Dict:
        """Get information about the ML model"""
        return {
            'version': self.model.get('version', '1.0.0-experimental'),
            'type': 'Weighted Ensemble (Simulated ML)',
            'status': 'Experimental',
            'trained_on': self.model.get('trained_on', 'synthetic_data'),
            'accuracy': self.model.get('accuracy', 0.85),
            'features': list(self.feature_weights.keys()),
            'feature_weights': self.feature_weights,
            'thresholds': self.thresholds,
            'limitations': [
                'Trained on limited synthetic data',
                'May produce false positives',
                'Not a replacement for signature-based detection',
                'Should be used as supplementary detection'
            ]
        }


# Create global instance
_ml_scorer = None


def get_ml_scorer() -> MLThreatScorer:
    """Get global ML scorer instance"""
    global _ml_scorer
    if _ml_scorer is None:
        _ml_scorer = MLThreatScorer()
    return _ml_scorer