from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from backend.database.base import Base


class Asset(Base):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(20), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=True)
    asset_type = Column(String(20), nullable=False)  # stock or etf
    sector = Column(String(100), nullable=True)
    industry = Column(String(255), nullable=True)
    exchange = Column(String(50), nullable=True)
    currency = Column(String(10), nullable=True)

    prices = relationship("Price", back_populates="asset")
    fundamentals = relationship("FundamentalsSnapshot", back_populates="asset")
    analyst_ratings = relationship("AnalystRating", back_populates="asset")
    news_items = relationship("NewsItem", back_populates="asset")
    predictions = relationship("ModelPrediction", back_populates="asset")


class Price(Base):
    __tablename__ = "prices"

    id = Column(Integer, primary_key=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), index=True, nullable=False)
    date = Column(Date, index=True, nullable=False)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Float, nullable=True)
    dividend = Column(Float, nullable=True)
    split = Column(Float, nullable=True)

    asset = relationship("Asset", back_populates="prices")
    technicals = relationship("TechnicalIndicator", back_populates="price")


class TechnicalIndicator(Base):
    __tablename__ = "technical_indicators"

    id = Column(Integer, primary_key=True)
    price_id = Column(Integer, ForeignKey("prices.id"), index=True, nullable=False)

    # Core oscillators and trend indicators
    rsi = Column(Float, nullable=True)
    macd = Column(Float, nullable=True)
    macd_signal = Column(Float, nullable=True)
    macd_hist = Column(Float, nullable=True)
    ema20 = Column(Float, nullable=True)
    ema50 = Column(Float, nullable=True)
    ema100 = Column(Float, nullable=True)
    ema200 = Column(Float, nullable=True)
    sma20 = Column(Float, nullable=True)
    sma50 = Column(Float, nullable=True)
    sma200 = Column(Float, nullable=True)
    vwap = Column(Float, nullable=True)
    adx = Column(Float, nullable=True)
    atr = Column(Float, nullable=True)
    obv = Column(Float, nullable=True)
    roc = Column(Float, nullable=True)
    momentum = Column(Float, nullable=True)
    stochastic_k = Column(Float, nullable=True)
    stochastic_d = Column(Float, nullable=True)
    williams_r = Column(Float, nullable=True)
    cci = Column(Float, nullable=True)

    # Trend and regime features
    golden_cross = Column(Boolean, nullable=True)  # SMA50 crosses above SMA200
    death_cross = Column(Boolean, nullable=True)   # SMA50 crosses below SMA200
    trend_slope_20d = Column(Float, nullable=True)
    trend_slope_60d = Column(Float, nullable=True)
    trend_slope_120d = Column(Float, nullable=True)
    distance_from_52w_high = Column(Float, nullable=True)
    distance_from_52w_low = Column(Float, nullable=True)

    # Volatility features
    rolling_vol_10d = Column(Float, nullable=True)
    rolling_vol_30d = Column(Float, nullable=True)
    rolling_vol_90d = Column(Float, nullable=True)
    max_drawdown_90d = Column(Float, nullable=True)
    downside_dev_30d = Column(Float, nullable=True)
    sharpe_90d = Column(Float, nullable=True)
    sortino_90d = Column(Float, nullable=True)
    beta_vs_spy_252d = Column(Float, nullable=True)

    # Volume and liquidity features
    avg_volume_20d = Column(Float, nullable=True)
    rel_volume = Column(Float, nullable=True)
    mfi = Column(Float, nullable=True)
    acc_dist = Column(Float, nullable=True)
    vwap_deviation = Column(Float, nullable=True)

    price = relationship("Price", back_populates="technicals")


class FundamentalsSnapshot(Base):
    __tablename__ = "fundamentals_snapshots"

    id = Column(Integer, primary_key=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), index=True, nullable=False)
    as_of_date = Column(Date, index=True, nullable=False)

    # Valuation
    pe = Column(Float, nullable=True)
    forward_pe = Column(Float, nullable=True)
    peg = Column(Float, nullable=True)
    pb = Column(Float, nullable=True)
    ps = Column(Float, nullable=True)
    ev_ebitda = Column(Float, nullable=True)

    # Profitability and quality
    roe = Column(Float, nullable=True)
    roa = Column(Float, nullable=True)
    roic = Column(Float, nullable=True)
    gross_margin = Column(Float, nullable=True)
    operating_margin = Column(Float, nullable=True)
    net_margin = Column(Float, nullable=True)

    # Growth and cash flow
    revenue_growth = Column(Float, nullable=True)
    eps_growth = Column(Float, nullable=True)
    free_cash_flow = Column(Float, nullable=True)

    # Balance sheet and risk
    debt_to_equity = Column(Float, nullable=True)
    current_ratio = Column(Float, nullable=True)

    # Ownership and dividends
    institutional_ownership = Column(Float, nullable=True)
    insider_ownership = Column(Float, nullable=True)
    dividend_yield = Column(Float, nullable=True)

    market_cap = Column(Float, nullable=True)

    source = Column(String(50), nullable=True)

    asset = relationship("Asset", back_populates="fundamentals")


class AnalystRating(Base):
    __tablename__ = "analyst_ratings"

    id = Column(Integer, primary_key=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), index=True, nullable=False)
    as_of_date = Column(Date, index=True, nullable=False)

    buy = Column(Integer, nullable=True)
    hold = Column(Integer, nullable=True)
    sell = Column(Integer, nullable=True)
    avg_price_target = Column(Float, nullable=True)
    upside_pct = Column(Float, nullable=True)
    consensus = Column(String(20), nullable=True)
    confidence = Column(Float, nullable=True)

    source = Column(String(50), nullable=True)

    asset = relationship("Asset", back_populates="analyst_ratings")


class NewsItem(Base):
    __tablename__ = "news_items"

    id = Column(Integer, primary_key=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), index=True, nullable=True)
    published_at = Column(DateTime, index=True, nullable=False)
    source = Column(String(255), nullable=True)
    title = Column(String(500), nullable=False)
    url = Column(String(1000), nullable=False)
    summary = Column(String(2000), nullable=True)

    sentiment_score = Column(Float, nullable=True)  # -1..1
    sentiment_label = Column(String(20), nullable=True)  # bullish/neutral/bearish

    asset = relationship("Asset", back_populates="news_items")


class MacroSnapshot(Base):
    __tablename__ = "macro_snapshots"

    id = Column(Integer, primary_key=True)
    as_of_date = Column(Date, index=True, nullable=False)

    # Market regime & macro
    interest_rate = Column(Float, nullable=True)
    inflation = Column(Float, nullable=True)
    gdp_growth = Column(Float, nullable=True)
    cpi = Column(Float, nullable=True)
    ppi = Column(Float, nullable=True)
    treasury_yield_10y = Column(Float, nullable=True)
    vix = Column(Float, nullable=True)
    fear_greed_index = Column(Float, nullable=True)
    dollar_index = Column(Float, nullable=True)

    spy_trend_score = Column(Float, nullable=True)
    sector_trend_score = Column(Float, nullable=True)
    market_breadth_score = Column(Float, nullable=True)
    macro_score = Column(Float, nullable=True)


class ModelPrediction(Base):
    __tablename__ = "model_predictions"

    id = Column(Integer, primary_key=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), index=True, nullable=False)
    as_of_date = Column(Date, index=True, nullable=False)

    model_name = Column(String(100), nullable=False)
    forecast_horizon = Column(Integer, nullable=False)  # days

    # Prediction outputs
    expected_return = Column(Float, nullable=True)
    expected_volatility = Column(Float, nullable=True)
    expected_low = Column(Float, nullable=True)
    expected_high = Column(Float, nullable=True)

    probability_positive = Column(Float, nullable=True)
    probability_5_percent = Column(Float, nullable=True)
    probability_minus5_percent = Column(Float, nullable=True)

    # Decomposed scores
    trend_score = Column(Float, nullable=True)
    momentum_score = Column(Float, nullable=True)
    quality_score = Column(Float, nullable=True)
    valuation_score = Column(Float, nullable=True)
    risk_score = Column(Float, nullable=True)
    volume_score = Column(Float, nullable=True)
    sentiment_score = Column(Float, nullable=True)
    confidence_score = Column(Float, nullable=True)

    # Backtesting and accuracy
    backtest_accuracy = Column(Float, nullable=True)
    win_rate = Column(Float, nullable=True)
    avg_return = Column(Float, nullable=True)
    avg_drawdown = Column(Float, nullable=True)
    avg_prediction_error = Column(Float, nullable=True)

    # Aggregate AI Score
    ai_score = Column(Float, nullable=True)
    ai_score_explanation = Column(String(4000), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    asset = relationship("Asset", back_populates="predictions")


class Portfolio(Base):
    __tablename__ = "portfolios"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    positions = relationship("PortfolioPosition", back_populates="portfolio")


class PortfolioPosition(Base):
    __tablename__ = "portfolio_positions"

    id = Column(Integer, primary_key=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), index=True, nullable=False)
    ticker = Column(String(20), nullable=False)
    quantity = Column(Float, nullable=False)
    average_cost = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    portfolio = relationship("Portfolio", back_populates="positions")
