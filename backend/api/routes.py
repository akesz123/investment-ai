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
    - Computes a simple baseline prediction per asset so that the UI has
      something to display before the full ML stack is implemented.

    All scores are heuristic and must NOT be interpreted as guaranteed
    future returns or financial advice.
    """

    tickers: List[str] = []

    # Major ETFs and sample stocks from YahooFinanceService
    tickers.extend(yf_service.get_major_etfs())
    tickers.extend(yf_service.get_sample_stocks())

    assets_touched = 0
    predictions_created = 0

    for ticker in sorted(set(tickers)):
        ticker = ticker.upper()

        # Ensure Asset exists
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

        # Fetch recent history
        prices_df = yf_service.get_historical_data(ticker)
        if prices_df is None or prices_df.empty:
            continue

        # Store latest price row
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

        # Compute baseline prediction & store ModelPrediction
        baseline = yf_service.compute_baseline_prediction(prices_df)
        prediction = models.ModelPrediction(
            asset_id=asset.id,
            as_of_date=latest_date,
            model_name="baseline-heuristic-v0",
            positive_30d_prob=baseline["positive_30d_prob"],
            expected_return_30d=baseline["expected_return_30d"],
            expected_return_low=baseline["expected_return_low"],
            expected_return_high=baseline["expected_return_high"],
            confidence=baseline["confidence"],
            risk_level=str(baseline["risk_level"]),
            ai_score=baseline["ai_score"],
            ai_score_explanation=str(baseline["ai_score_explanation"]),
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
            "positive_30d_prob": latest_prediction.positive_30d_prob if latest_prediction else None,
            "expected_return_30d": latest_prediction.expected_return_30d if latest_prediction else None,
            "expected_return_low": latest_prediction.expected_return_low if latest_prediction else None,
            "expected_return_high": latest_prediction.expected_return_high if latest_prediction else None,
            "confidence": latest_prediction.confidence if latest_prediction else None,
            "risk_level": latest_prediction.risk_level if latest_prediction else None,
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
                "expected_return": pred.expected_return_30d,
                "confidence": pred.confidence,
                "risk": pred.risk_level,
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
                "expected_return": pred.expected_return_30d,
                "confidence": pred.confidence,
                "risk": pred.risk_level,
                "sector": asset.sector,
                "reason": pred.ai_score_explanation,
            }
        )

    return results