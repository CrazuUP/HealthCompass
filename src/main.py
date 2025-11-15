from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import logging
from contextlib import asynccontextmanager
from datetime import datetime
import os

from config import settings
from models.max_models import Update
from models.health_models import UserProfile, HealthMetric
from handlers.webhook_handler import WebhookHandler
from services.max_api import MaxApiService
from services.health_service import HealthService
from services.screening_service import ScreeningService
from pydantic import BaseModel
from typing import Optional, Dict, Any

# -------------------------------
# Логирование
# -------------------------------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# -------------------------------
# Глобальные сервисы
# -------------------------------
max_api = None
webhook_handler = None
health_service = None
screening_service = None


# -------------------------------
# Lifespan приложения
# -------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    global max_api, webhook_handler, health_service, screening_service

    logger.info("🚀 Starting Health Compass MAX Mini-App...")

    # Инициализация сервисов
    health_service = HealthService()
    screening_service = ScreeningService()

    if settings.max_bot_token:
        max_api = MaxApiService()
        webhook_handler = WebhookHandler()

        if settings.webhook_url:
            try:
                await max_api.set_webhook(
                    url=settings.webhook_url,
                    secret=settings.webhook_secret
                )
                logger.info("✅ Webhook set successfully")
                bot_info = await max_api.get_my_info()
                logger.info(f"🤖 Bot info: {bot_info.get('first_name', 'Unknown')}")
            except Exception as e:
                logger.error(f"❌ Failed to set webhook: {e}")
        else:
            logger.info("ℹ️ Webhook URL not configured, bot component disabled")
    else:
        logger.info("ℹ️ Bot token not configured, running as mini-app only")
        max_api = None
        webhook_handler = None

    yield

    logger.info("🛑 Shutting down Health Compass MAX Mini-App...")


# -------------------------------
# Paths для статических файлов и шаблонов
# -------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATES_DIR = os.path.join(STATIC_DIR, "templates")

# Проверяем и создаем директорию static, если её нет
if not os.path.exists(STATIC_DIR):
    logger.warning(f"⚠️ Static directory does not exist: {STATIC_DIR}, creating it...")
    os.makedirs(STATIC_DIR, exist_ok=True)

print("🗂 BASE_DIR:", BASE_DIR)
print("🗂 STATIC_DIR:", STATIC_DIR, "exists:", os.path.exists(STATIC_DIR))

# -------------------------------
# Создание FastAPI приложения
# -------------------------------
app = FastAPI(
    title="Health Compass — Мини-приложение для MAX",
    description="Ваш персональный навигатор в мире здоровья. Веб-мини-приложение для платформы MAX.",
    version="1.0.0",
    lifespan=lifespan
)

# -------------------------------
# Статика и шаблоны
# -------------------------------
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
    logger.info(f"✅ Static files mounted from: {STATIC_DIR}")
else:
    logger.error(f"❌ Static directory does not exist: {STATIC_DIR}")

try:
    templates = Jinja2Templates(directory=TEMPLATES_DIR)
    logger.info(f"✅ Templates loaded from: {TEMPLATES_DIR}")
except Exception as e:
    logger.error(f"❌ Failed to load templates from {TEMPLATES_DIR}: {e}")
    templates = None


# -------------------------------
# Роуты
# -------------------------------
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    if templates is None:
        raise HTTPException(status_code=500, detail="Templates not available")
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api")
async def api_info():
    return {
        "message": "🏥 Health Compass MAX Mini-App is running!",
        "status": "healthy",
        "service": "health-navigation",
        "type": "mini-app"
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }


@app.post("/webhook")
async def webhook(update: Update):
    if not webhook_handler:
        raise HTTPException(status_code=503, detail="Bot component not configured")
    try:
        logger.info(f"📨 Received update: {update.update_type}")
        result = await webhook_handler.handle_update(update)
        return JSONResponse(content={"status": "ok", "handled": True})
    except Exception as e:
        logger.error(f"💥 Error processing update: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/bot/info")
async def get_bot_info():
    if not max_api:
        raise HTTPException(status_code=503, detail="Service not ready")
    try:
        bot_info = await max_api.get_my_info()
        return bot_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------------
# API для фронтенда
# -------------------------------
class ProfileCreate(BaseModel):
    full_name: str
    birth_year: int
    gender: str
    blood_type: str
    weight: float
    height: int
    emergency_contact: str
    allergies: Optional[str] = None
    vision: Optional[str] = None
    work_type: Optional[str] = None
    medical_history: Optional[str] = None
    current_conditions: Optional[str] = None


class HealthMetricCreate(BaseModel):
    metric_type: str
    value: Dict[str, Any]
    notes: Optional[str] = None


@app.post("/api/profile")
async def create_profile(profile: ProfileCreate, request: Request):
    user_id = request.query_params.get("user_id", 1)
    if isinstance(user_id, str):
        user_id = int(user_id)
    try:
        profile_data = {
            "gender": profile.gender,
            "age": datetime.now().year - profile.birth_year,
            "risk_factors": [],
            "conditions": []
        }
        user_profile = await health_service.create_user_profile(user_id, profile_data)
        return {"status": "ok", "profile": user_profile.model_dump()}
    except Exception as e:
        logger.error(f"Error creating profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/profile/{user_id}")
async def get_profile(user_id: int):
    try:
        profile = await health_service.get_user_profile(user_id)
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        return profile.model_dump()
    except Exception as e:
        logger.error(f"Error getting profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------------
# Остальные эндпоинты health-metrics, screening-schedule
# можно оставить как есть
# -------------------------------

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=True
    )
