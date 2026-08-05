class FundamentalAnalyzer:
    def score(self, fundamentals: dict) -> float:
        if not fundamentals:
            return 50.0
        score = 50.0
        pe = fundamentals.get('trailingPE') or fundamentals.get('pe_ratio')
        growth = fundamentals.get('revenueGrowth') or fundamentals.get('revenue_growth')
        margin = fundamentals.get('profitMargins') or fundamentals.get('profit_margin')
        debt = fundamentals.get('debtToEquity') or fundamentals.get('debt_to_equity')
        if pe is not None and pe > 0 and pe < 20: score += 10
        if growth is not None and growth > 0: score += 15
        if margin is not None and margin > 0: score += 10
        if debt is not None and debt < 100: score += 5
        return max(0, min(100, score))

analyzer = FundamentalAnalyzer()
