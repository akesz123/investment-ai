import yfinance as yf
from typing import Optional, Dict, List

class YahooFinanceService:
    def get_stock_info(self, ticker: str) -> Optional[Dict]:
        try:
            info = yf.Ticker(ticker).info
            return info or None
        except Exception:
            return None

    def get_historical_data(self, ticker: str, period: str = '2y'):
        try:
            df = yf.Ticker(ticker).history(period=period)
            return df.reset_index() if df is not None and not df.empty else None
        except Exception:
            return None

    def get_major_etfs(self) -> List[str]:
        return ['SPY', 'QQQ', 'IWM', 'DIA', 'VTI', 'VOO', 'XLK', 'XLF', 'XLE', 'XLV']

service = YahooFinanceService()
