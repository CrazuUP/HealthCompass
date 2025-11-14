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
from handlers.webhook_handler import WebhookHandler
from services.max_api import MaxApiService

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Глобальные сервисы
max_api = None
webhook_handler = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global max_api, webhook_handler

    logger.info("🚀 Starting Health Compass MAX Bot...")

    # Инициализация сервисов
    max_api = MaxApiService()
    webhook_handler = WebhookHandler()

    # Установка webhook
    try:
        await max_api.set_webhook(
            url=settings.webhook_url,
            secret=settings.webhook_secret
        )
        logger.info("✅ Webhook set successfully")

        # Получение информации о боте
        bot_info = await max_api.get_my_info()
        logger.info(f"🤖 Bot info: {bot_info.get('first_name', 'Unknown')}")

    except Exception as e:
        logger.error(f"❌ Failed to set webhook: {e}")

    yield  # Здесь приложение работает

    # Shutdown
    logger.info("🛑 Shutting down Health Compass MAX Bot...")


# Определение путей к статическим файлам и шаблонам
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATES_DIR = os.path.join(STATIC_DIR, "templates")

# Создание FastAPI приложения
app = FastAPI(
    title="Health Compass MAX Bot",
    description="Ваш персональный навигатор в мире здоровья",
    version="1.0.0",
    lifespan=lifespan
)

# Подключение статических файлов (CSS, JS, изображения)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Настройка шаблонов Jinja2
templates = Jinja2Templates(directory=TEMPLATES_DIR)


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Главная страница приложения"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api")
async def api_info():
    """API информация"""
    return {
        "message": "🏥 Health Compass MAX Bot is running!",
        "status": "healthy",
        "service": "health-navigation"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }


@app.post("/webhook")
async def webhook(update: Update):
    """Основной webhook endpoint для MAX API"""
    try:
        logger.info(f"📨 Received update: {update.update_type}")

        # Обработка обновления
        result = await webhook_handler.handle_update(update)

        return JSONResponse(content={"status": "ok", "handled": True})

    except Exception as e:
        logger.error(f"💥 Error processing update: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/bot/info")
async def get_bot_info():
    """Получить информацию о боте"""
    try:
        if not max_api:
            raise HTTPException(status_code=503, detail="Service not ready")

        bot_info = await max_api.get_my_info()
        return bot_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=True
    )