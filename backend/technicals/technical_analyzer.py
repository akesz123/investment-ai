import pandas as pd
import numpy as np

class TechnicalAnalyzer:
    def add_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        if df is None or df.empty:
            return df
        df = df.copy()
        df['ema_20'] = df['Close'].ewm(span=20, adjust=False).mean()
        df['ema_50'] = df['Close'].ewm(span=50, adjust=False).mean()
        delta = df['Close'].diff()
        gain = delta.clip(lower=0).rolling(14).mean()
        loss = (-delta.clip(upper=0)).rolling(14).mean()
        rs = gain / loss.replace(0, np.nan)
        df['rsi'] = 100 - (100 / (1 + rs))
        return df

    def score(self, df: pd.DataFrame) -> float:
        if df is None or df.empty:
            return 50.0
        latest = df.iloc[-1]
        score = 50.0
        if latest.get('Close', 0) > latest.get('ema_20', 0): score += 10
        if latest.get('Close', 0) > latest.get('ema_50', 0): score += 10
        rsi = latest.get('rsi', 50)
        if 45 <= rsi <= 65: score += 10
        elif rsi > 70: score -= 10
        elif rsi < 30: score -= 10
        return max(0, min(100, score))

analyzer = TechnicalAnalyzer()
