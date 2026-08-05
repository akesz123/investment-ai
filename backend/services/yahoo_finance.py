import math
from typing import Optional, Dict, List

import yfinance as yf
import pandas as pd


class YahooFinanceService:
    """Wrapper around yfinance used by the scanner.

    Provides helpers for fetching instrument info, historical data, and
    computing a simple baseline prediction and AI score so that the UI has
    something to display before the full ML stack is implemented.

    All outputs are heuristic and MUST NOT be interpreted as guaranteed
    future returns or financial advice.
    """

    def get_stock_info(self, ticker: str) -> Optional[Dict]:
        """Return basic instrument info from Yahoo Finance."""
        try:
            info = yf.Ticker(ticker).info
            return info or None
        except Exception:
            return None

    def get_historical_data(
        self,
        ticker: str,
        period: str = "6mo",
    ) -> Optional[pd.DataFrame]:
        """Return recent OHLCV history for a ticker.

        Data is returned with a 'Date' column and standard OHLCV columns.
        """
        try:
            df = yf.Ticker(ticker).history(period=period)
            if df is None or df.empty:
                return None
            return df.reset_index()
        except Exception:
            return None

    def get_major_etfs(self) -> List[str]:
        """Universe of major US ETFs for initial scanning."""
        return ["SPY", "QQQ", "IWM", "DIA", "VTI", "VOO", "XLK", "XLF", "XLE", "XLV"]

    def get_sample_stocks(self) -> List[str]:
        """Small starter stock universe.

        Later, replace this with full S&P500 / NASDAQ100 / Russell2000
        constituent lists.
        """
        return [
            "AAPL",
            "MSFT",
            "GOOGL",
            "AMZN",
            "META",
            "NVDA",
            "TSLA",
            "JPM",
            "UNH",
            "HD",
        ]

    def compute_baseline_prediction(self, prices: pd.DataFrame) -> Dict[str, float | str]:
        """Compute a naive baseline prediction from recent prices.

        This is NOT a production trading model. It only populates the UI
        and should not be interpreted as financial advice or as a
        guarantee of future returns.
        """
        # Ensure sorted by date
        prices = prices.sort_values("Date")
        prices["return"] = prices["Close"].pct_change()

        # Use last ~30 trading days
        window = prices.tail(30)
        if len(window) > 1:
            recent_return = window["Close"].iloc[-1] / window["Close"].iloc[0] - 1
        else:
            recent_return = 0.0
        vol = float(window["return"].std() or 0.0)

        # Neutral baseline probability around 0.5, nudged by momentum
        positive_prob = 0.5 + 0.2 * math.tanh(recent_return * 10)
        positive_prob = max(0.0, min(1.0, positive_prob))

        # Expected return range from recent return and volatility
        expected_mid = recent_return
        expected_low = expected_mid - 2 * vol
        expected_high = expected_mid + 2 * vol

        # Simple risk buckets
        if vol < 0.01:
            risk_level = "low"
        elif vol < 0.03:
            risk_level = "medium"
        else:
            risk_level = "high"

        # AI score: probability * (1 + return) minus volatility, scaled to 0–100
        score_raw = positive_prob * (1 + expected_mid) - vol
        ai_score = max(0.0, min(1.0, score_raw)) * 100.0

        explanation = (
            "Baseline score from recent ~30-day price behaviour: "
            f"return {recent_return:.2%}, volatility {vol:.2%}. "
            "Heuristic only – not a guarantee. Future versions will "
            "combine technical, fundamental, sentiment, analyst, and "
            "macro data for a more robust AI score."
        )

        return {
            "positive_30d_prob": positive_prob,
            "expected_return_30d": expected_mid,
            "expected_return_low": expected_low,
            "expected_return_high": expected_high,
            "confidence": 0.5,
            "risk_level": risk_level,
            "ai_score": ai_score,
            "ai_score_explanation": explanation,
        }


service = YahooFinanceService()