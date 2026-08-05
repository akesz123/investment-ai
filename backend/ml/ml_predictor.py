class MLPredictor:
    def predict(self, features):
        return {'probability_positive': 0.55, 'expected_return_range': (-0.05, 0.08), 'confidence': 0.6, 'risk_level': 'MEDIUM'}

predictor = MLPredictor()
