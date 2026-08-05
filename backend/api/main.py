from fastapi import FastAPI
from backend.config.settings import settings

app = FastAPI(title=settings.app_name, debug=settings.debug)

@app.get('/health')
def health():
    return {'status': 'ok', 'app': settings.app_name}
