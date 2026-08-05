from fastapi import APIRouter

router = APIRouter()

@router.get('/scan')
def scan():
    return {'status': 'ok', 'message': 'scan endpoint'}

@router.get('/top-stocks')
def top_stocks():
    return {'items': []}

@router.get('/top-etfs')
def top_etfs():
    return {'items': []}

@router.get('/analyze/{ticker}')
def analyze_ticker(ticker: str):
    return {'ticker': ticker, 'analysis': {}}

@router.get('/portfolio')
def portfolio():
    return {'portfolio': {}}

@router.get('/backtest')
def backtest():
    return {'results': {}}

@router.get('/news')
def news():
    return {'items': []}

@router.get('/settings')
def settings():
    return {'settings': {}}
