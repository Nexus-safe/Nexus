import numpy as np
from typing import Dict, List, Any
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import torch
import torch.nn as nn
import pandas as pd


class HealthPredictor(nn.Module):
    def __init__(self, input_size: int, hidden_size: int, num_classes: int):
        super(HealthPredictor, self).__init__()
        self.layer1 = nn.Linear(input_size, hidden_size)
        self.relu = nn.ReLU()
        self.layer2 = nn.Linear(hidden_size, hidden_size)
        self.layer3 = nn.Linear(hidden_size, num_classes)
        self.softmax = nn.Softmax(dim=1)

    def forward(self, x):
        x = self.layer1(x)
        x = self.relu(x)
        x = self.layer2(x)
        x = self.relu(x)
        x = self.layer3(x)
        x = self.softmax(x)
        return x


class HealthAnalyzer:
    def __init__(self):
        self.scaler = StandardScaler()
        self.risk_classifier = RandomForestClassifier(n_estimators=100)
        self.neural_predictor = None
        self.initialized = False

    def initialize_neural_network(
        self, input_size: int, hidden_size: int = 64, num_classes: int = 5
    ):
        """Initialize the neural network model"""
        self.neural_predictor = HealthPredictor(input_size, hidden_size, num_classes)

    def preprocess_data(self, data: List[Dict[str, Any]]) -> np.ndarray:
        """Preprocess medical data for analysis"""
        df = pd.DataFrame(data)
        numerical_features = df.select_dtypes(include=[np.number]).columns

        if not self.initialized:
            self.scaler.fit(df[numerical_features])
            self.initialized = True

        return self.scaler.transform(df[numerical_features])

    def train_risk_model(self, training_data: List[Dict[str, Any]], labels: List[int]):
        """Train the risk assessment model"""
        X = self.preprocess_data(training_data)
        self.risk_classifier.fit(X, labels)

    def predict_health_risks(self, patient_data: Dict[str, Any]) -> Dict[str, float]:
        """Predict health risks for a patient"""
        processed_data = self.preprocess_data([patient_data])
        risk_probabilities = self.risk_classifier.predict_proba(processed_data)[0]

        return {
            "low_risk": float(risk_probabilities[0]),
            "moderate_risk": float(risk_probabilities[1]),
            "high_risk": float(risk_probabilities[2]),
        }

    def analyze_trends(self, historical_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze health trends from historical data"""
        df = pd.DataFrame(historical_data)

        analysis = {"trends": {}, "anomalies": [], "recommendations": []}

        # Analyze trends for numerical values
        for column in df.select_dtypes(include=[np.number]).columns:
            trend = {
                "mean": float(df[column].mean()),
                "std": float(df[column].std()),
                "min": float(df[column].min()),
                "max": float(df[column].max()),
            }
            analysis["trends"][column] = trend

            # Detect anomalies (values outside 2 standard deviations)
            mean = trend["mean"]
            std = trend["std"]
            anomalies = df[abs(df[column] - mean) > 2 * std]
            if not anomalies.empty:
                analysis["anomalies"].append(
                    {"metric": column, "dates": anomalies.index.tolist()}
                )

        return analysis

    def generate_health_recommendations(
        self, analysis_results: Dict[str, Any]
    ) -> List[str]:
        """Generate personalized health recommendations based on analysis"""
        recommendations = []

        for metric, trend in analysis_results["trends"].items():
            if trend["std"] > trend["mean"] * 0.5:  # High variability
                recommendations.append(
                    f"Monitor {metric} more frequently due to high variability"
                )

            if len(analysis_results["anomalies"]) > 0:
                recommendations.append(
                    "Schedule a check-up to discuss recent anomalies"
                )

        return recommendations

    def predict_future_metrics(
        self,
        historical_data: List[Dict[str, Any]],
        target_metric: str,
        prediction_window: int = 30,
    ) -> List[float]:
        """Predict future health metrics using neural network"""
        if not self.neural_predictor:
            raise ValueError("Neural network not initialized")

        df = pd.DataFrame(historical_data)
        X = torch.FloatTensor(self.preprocess_data(historical_data))

        with torch.no_grad():
            predictions = self.neural_predictor(X)

        return predictions.numpy().tolist()
