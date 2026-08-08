from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database.connection import SessionLocal
from backend.database import models
from backend.services.yahoo_finance import service as yf_service


router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/scan", response_model=dict)
def scan_market(db: Session = Depends(get_db)):
    """Trigger a market scan over major ETFs and a starter stock universe.

    This implementation:
    - Loads major ETFs + sample stocks,
    - Fetches recent historical prices,
    - Stores the latest Price per asset,
    - Computes a baseline multi-horizon prediction per asset so that the UI has
      something meaningful to display while the full ML stack evolves.

    All scores are heuristic and must NOT be interpreted as guaranteed
    future returns or financial advice.
    """

    tickers: List[str] = []

    tickers.extend(yf_service.get_major_etfs())
    tickers.extend(yf_service.get_sample_stocks())

    assets_touched = 0
    predictions_created = 0

    for ticker in sorted(set(tickers)):
        ticker = ticker.upper()

        asset = db.query(models.Asset).filter_by(ticker=ticker).first()
        if not asset:
            info = yf_service.get_stock_info(ticker)
            asset = models.Asset(
                ticker=ticker,
                name=(info or {}).get("shortName"),
                asset_type="etf" if (info or {}).get("quoteType") == "ETF" else "stock",
                sector=(info or {}).get("sector"),
                industry=(info or {}).get("industry"),
                exchange=(info or {}).get("exchange"),
                currency=(info or {}).get("currency"),
            )
            db.add(asset)
            db.flush()

        assets_touched += 1

        prices_df = yf_service.get_historical_data(ticker)
        if prices_df is None or prices_df.empty:
            continue

        latest = prices_df.sort_values("Date").iloc[-1]
        latest_date = latest["Date"].date()

        price = (
            db.query(models.Price)
            .filter_by(asset_id=asset.id, date=latest_date)
            .first()
        )
        if not price:
            price = models.Price(
                asset_id=asset.id,
                date=latest_date,
                open=float(latest["Open"]),
                high=float(latest["High"]),
                low=float(latest["Low"]),
                close=float(latest["Close"]),
                volume=float(latest.get("Volume") or 0.0),
            )
            db.add(price)

        # Compute baseline prediction using the new richer schema
        baseline = yf_service.compute_baseline_prediction(prices_df)

        prediction = models.ModelPrediction(
            asset_id=asset.id,
            as_of_date=latest_date,
            model_name="baseline-heuristic-v1",
            forecast_horizon=30,
            expected_return=baseline.get("expected_return_30d"),
            expected_volatility=baseline.get("expected_volatility_30d"),
            expected_low=baseline.get("expected_return_low"),
            expected_high=baseline.get("expected_return_high"),
            probability_positive=baseline.get("positive_30d_prob"),
            probability_5_percent=baseline.get("prob_5_percent"),
            probability_minus5_percent=baseline.get("prob_minus5_percent"),
            trend_score=baseline.get("trend_score"),
            momentum_score=baseline.get("momentum_score"),
            quality_score=baseline.get("quality_score"),
            valuation_score=baseline.get("valuation_score"),
            risk_score=baseline.get("risk_score"),
            volume_score=baseline.get("volume_score"),
            sentiment_score=baseline.get("sentiment_score"),
            confidence_score=baseline.get("confidence"),
            backtest_accuracy=None,
            win_rate=None,
            avg_return=None,
            avg_drawdown=None,
            avg_prediction_error=None,
            ai_score=baseline.get("ai_score"),
            ai_score_explanation=str(baseline.get("ai_score_explanation", "")),
        )
        db.add(prediction)
        predictions_created += 1

    db.commit()

    return {
        "status": "ok",
        "assets_touched": assets_touched,
        "tickers_scanned": len(set(tickers)),
        "predictions_created": predictions_created,
    }


@router.get("/analyze/{ticker}", response_model=dict)
def analyze_ticker(ticker: str, db: Session = Depends(get_db)):
    asset = db.query(models.Asset).filter_by(ticker=ticker.upper()).first()
    if not asset:
        raise HTTPException(
            status_code=404,
            detail="Ticker not found in database. Run /scan first.",
        )

    latest_price = (
        db.query(models.Price)
        .filter_by(asset_id=asset.id)
        .order_by(models.Price.date.desc())
        .first()
    )

    latest_prediction = (
        db.query(models.ModelPrediction)
        .filter_by(asset_id=asset.id)
        .order_by(models.ModelPrediction.as_of_date.desc())
        .first()
    )

    return {
        "ticker": asset.ticker,
        "name": asset.name,
        "asset_type": asset.asset_type,
        "sector": asset.sector,
        "industry": asset.industry,
        "exchange": asset.exchange,
        "currency": asset.currency,
        "latest_price": latest_price.close if latest_price else None,
        "prediction": {
            "model_name": latest_prediction.model_name if latest_prediction else None,
            "forecast_horizon": latest_prediction.forecast_horizon if latest_prediction else None,
            "expected_return": latest_prediction.expected_return if latest_prediction else None,
            "expected_volatility": latest_prediction.expected_volatility if latest_prediction else None,
            "expected_low": latest_prediction.expected_low if latest_prediction else None,
            "expected_high": latest_prediction.expected_high if latest_prediction else None,
            "probability_positive": latest_prediction.probability_positive if latest_prediction else None,
            "probability_5_percent": latest_prediction.probability_5_percent if latest_prediction else None,
            "probability_minus5_percent": latest_prediction.probability_minus5_percent if latest_prediction else None,
            "trend_score": latest_prediction.trend_score if latest_prediction else None,
            "momentum_score": latest_prediction.momentum_score if latest_prediction else None,
            "quality_score": latest_prediction.quality_score if latest_prediction else None,
            "valuation_score": latest_prediction.valuation_score if latest_prediction else None,
            "risk_score": latest_prediction.risk_score if latest_prediction else None,
            "volume_score": latest_prediction.volume_score if latest_prediction else None,
            "sentiment_score": latest_prediction.sentiment_score if latest_prediction else None,
            "confidence_score": latest_prediction.confidence_score if latest_prediction else None,
            "backtest_accuracy": latest_prediction.backtest_accuracy if latest_prediction else None,
            "win_rate": latest_prediction.win_rate if latest_prediction else None,
            "avg_return": latest_prediction.avg_return if latest_prediction else None,
            "avg_drawdown": latest_prediction.avg_drawdown if latest_prediction else None,
            "avg_prediction_error": latest_prediction.avg_prediction_error if latest_prediction else None,
            "ai_score": latest_prediction.ai_score if latest_prediction else None,
            "ai_score_explanation": latest_prediction.ai_score_explanation if latest_prediction else None,
        },
    }


@router.get("/top-stocks", response_model=list[dict])
def top_stocks(limit: int = 10, db: Session = Depends(get_db)):
    qs = (
        db.query(models.ModelPrediction, models.Asset)
        .join(models.Asset, models.ModelPrediction.asset_id == models.Asset.id)
        .order_by(models.ModelPrediction.ai_score.desc().nullslast())
        .limit(limit)
    )

    results = []
    for pred, asset in qs:
        if asset.asset_type != "stock":
            continue
        results.append(
            {
                "ticker": asset.ticker,
                "company": asset.name,
                "ai_score": pred.ai_score,
                "expected_return": pred.expected_return,
                "expected_range": [pred.expected_low, pred.expected_high],
                "probability_positive": pred.probability_positive,
                "confidence": pred.confidence_score,
                "risk": pred.risk_score,
                "sector": asset.sector,
                "reason": pred.ai_score_explanation,
            }
        )

    return results


@router.get("/top-etfs", response_model=list[dict])
def top_etfs(limit: int = 10, db: Session = Depends(get_db)):
    qs = (
        db.query(models.ModelPrediction, models.Asset)
        .join(models.Asset, models.ModelPrediction.asset_id == models.Asset.id)
        .order_by(models.ModelPrediction.ai_score.desc().nullslast())
        .limit(limit)
    )

    results = []
    for pred, asset in qs:
        if asset.asset_type != "etf":
            continue
        results.append(
            {
                "ticker": asset.ticker,
                "company": asset.name,
                "ai_score": pred.ai_score,
                "expected_return": pred.expected_return,
                "expected_range": [pred.expected_low, pred.expected_high],
                "probability_positive": pred.probability_positive,
                "confidence": pred.confidence_score,
                "risk": pred.risk_score,
                "sector": asset.sector,
                "reason": pred.ai_score_explanation,
            }
        )

    return results
