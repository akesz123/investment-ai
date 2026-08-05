from backend.technicals.technical_analyzer import analyzer as technical_analyzer
from backend.fundamentals.fundamental_analyzer import analyzer as fundamental_analyzer

class RankingEngine:
    def rank(self, technical_df=None, fundamentals=None, news_score=50, analyst_score=50, macro_score=50, risk_score=50):
        tech = technical_analyzer.score(technical_df) if technical_df is not None else 50
        fund = fundamental_analyzer.score(fundamentals or {})
        ai_score = round(0.25 * tech + 0.20 * fund + 0.20 * news_score + 0.15 * analyst_score + 0.10 * macro_score + 0.10 * (100 - risk_score), 2)
        explanation = f'Technical {tech:.1f}, fundamentals {fund:.1f}, news {news_score:.1f}, analyst {analyst_score:.1f}, macro {macro_score:.1f}, risk {risk_score:.1f}'
        return {'ai_score': ai_score, 'technical_score': tech, 'fundamental_score': fund, 'news_score': news_score, 'analyst_score': analyst_score, 'macro_score': macro_score, 'risk_score': risk_score, 'explanation': explanation}

engine = RankingEngine()
