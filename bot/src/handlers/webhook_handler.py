from typing import Dict, Any
from models.max_models import Update
from handlers.message_handler import MessageHandler
from handlers.callback_handler import CallbackHandler
from services.health_service import HealthService

class WebhookHandler:
    def __init__(self):
        self.message_handler = MessageHandler()
        self.callback_handler = CallbackHandler()
        self.health_service = HealthService()

    async def handle_update(self, update: Update) -> Dict[str, Any]:
        """Обработка входящего обновления от MAX API"""

        if update.update_type == "message_created" and update.message:
            await self.message_handler.handle_message(update.message.dict())

        elif update.update_type == "message_callback" and update.callback:
            await self.callback_handler.handle_callback(
                update.callback.dict(),
                update.message.dict() if update.message else None
            )

        elif update.update_type == "bot_started":
            await self._handle_bot_started(update)

        elif update.update_type == "bot_stopped":
            await self._handle_bot_stopped(update)

        return {"status": "processed", "update_type": update.update_type}

    async def _handle_bot_started(self, update: Update):
        """Обработка запуска бота"""
        chat_id = update.chat_id
        user = update.user.dict() if update.user else {}
        user_id = user.get("user_id")

        if chat_id and user_id:
            # Проверяем есть ли профиль пользователя
            profile = await self.health_service.get_user_profile(user_id)
            await self.message_handler._handle_start(chat_id, user, profile)

    async def _handle_bot_stopped(self, update: Update):
        """Обработка остановки бота"""
        user = update.user.dict() if update.user else {}
        user_id = user.get("user_id")
        print(f"Bot stopped by user: {user_id}")