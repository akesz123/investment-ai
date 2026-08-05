from fastapi import FastAPI
from backend.config.settings import settings
from backend.api.routes import router

app = FastAPI(title=settings.app_name, debug=settings.debug)
app.include_router(router)

@app.get('/health')
def health():
    return {'status': 'ok', 'app': settings.app_name}
