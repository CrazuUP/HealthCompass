from typing import Dict, Any
from services.max_api import MaxApiService
from services.screening_service import ScreeningService
from services.health_service import HealthService
from services.community_service import CommunityService
from models.health_models import UserProfile


class MessageHandler:
    def __init__(self):
        self.max_api = MaxApiService()
        self.screening_service = ScreeningService()
        self.health_service = HealthService()
        self.community_service = CommunityService()

    async def handle_message(self, message: Dict[str, Any]):
        """Обработка входящих сообщений"""
        text = message.get("body", {}).get("text", "").lower()
        chat_id = message.get("recipient", {}).get("chat_id")
        user = message.get("sender", {})
        user_id = user.get("user_id")

        if not chat_id:
            return

        # Проверка профиля пользователя
        profile = await self.health_service.get_user_profile(user_id)

        if "/start" in text or "начать" in text:
            await self._handle_start(chat_id, user, profile)
        elif "здоровье" in text or "health" in text:
            await self._handle_health_menu(chat_id)
        elif "обследование" in text or "скрининг" in text:
            if profile:
                await self._handle_screening_schedule(chat_id, profile)
            else:
                await self._ask_for_profile(chat_id)
        elif "симптом" in text or "болит" in text:
            await self._handle_symptoms_start(chat_id)
        elif "клиник" in text or "больниц" in text:
            await self._handle_find_clinic(chat_id)
        elif "сообществ" in text or "поддержк" in text:
            if profile:
                await self._handle_community_suggestions(chat_id, profile)
            else:
                await self._ask_for_profile(chat_id)
        elif "профиль" in text or "profile" in text:
            await self._handle_profile_management(chat_id, user_id, profile)
        elif "помощь" in text or "help" in text:
            await self._handle_help(chat_id)
        else:
            await self._handle_unknown(chat_id)

    async def _handle_start(self, chat_id: int, user: Dict[str, Any], profile: UserProfile = None):
        """Приветственное сообщение"""
        user_name = user.get('first_name', 'друг')

        if profile:
            welcome_text = f"""👋 С возвращением в Health Compass, {user_name}!

Ваш персональный навигатор в мире здоровья готов помочь."""
        else:
            welcome_text = f"""👋 Добро пожаловать в Health Compass, {user_name}!

Я ваш помощник для отслеживания здоровья. Я помогу вам:
• 💉 Создать персональный календарь обследований
• 🤕 Разобраться с симптомами и найти нужного специалиста  
• 🏥 Найти клиники и лаборатории рядом с вами
• 👥 Получить поддержку в сообществах по заболеваниям

Давайте создадим ваш профиль для персонализированных рекомендаций!"""

        buttons = [
            [
                {"type": "callback", "text": "💉 Мои обследования", "payload": "my_screenings"},
                {"type": "callback", "text": "🤕 Симптомы", "payload": "symptoms"}
            ],
            [
                {"type": "callback", "text": "🏥 Найти клинику", "payload": "find_clinic"},
                {"type": "callback", "text": "📊 Дневник здоровья", "payload": "health_diary"}
            ],
            [
                {"type": "callback", "text": "👥 Сообщества", "payload": "communities"},
                {"type": "callback", "text": "👤 Профиль", "payload": "profile"}
            ],
            [
                {"type": "callback", "text": "ℹ️ Помощь", "payload": "help"}
            ]
        ]

        await self.max_api.send_message_with_keyboard(chat_id, welcome_text, buttons)

    async def _handle_health_menu(self, chat_id: int):
        """Меню здоровья"""
        text = """🏥 Health Compass - ваш навигатор в мире здоровья

Выберите раздел:"""

        buttons = [
            [
                {"type": "callback", "text": "💉 Плановые обследования", "payload": "my_screenings"},
                {"type": "callback", "text": "🤕 Анализ симптомов", "payload": "symptoms"}
            ],
            [
                {"type": "callback", "text": "🏥 Поиск клиник", "payload": "find_clinic"},
                {"type": "callback", "text": "📊 Медицинский дневник", "payload": "health_diary"}
            ],
            [
                {"type": "callback", "text": "👥 Сообщества поддержки", "payload": "communities"},
                {"type": "callback", "text": "👤 Управление профилем", "payload": "profile"}
            ]
        ]

        await self.max_api.send_message_with_keyboard(chat_id, text, buttons)

    async def _handle_screening_schedule(self, chat_id: int, profile: UserProfile):
        """Показать персональный календарь обследований"""
        # Заглушка - замените на реальную логику
        schedule_text = f"""💉 Персональный календарь обследований для {profile.age} лет:

• 📅 Ежегодный осмотр: через 2 месяца
• ❤️ Кардиограмма: через 6 месяцев  
• 🩸 Анализ крови: через 3 месяца
• 👁️ Осмотр офтальмолога: через 1 год

Следующее обследование: Общий анализ крови через 3 месяца"""

        buttons = [
            [{"type": "callback", "text": "🏥 Найти клинику для обследований", "payload": "find_clinic_screening"}],
            [{"type": "callback", "text": "📱 Настроить напоминания", "payload": "set_reminders"}],
            [{"type": "callback", "text": "🔄 Обновить профиль", "payload": "update_profile"}]
        ]

        await self.max_api.send_message_with_keyboard(chat_id, schedule_text, buttons)

    async def _handle_symptoms_start(self, chat_id: int):
        """Начало опроса по симптомам"""
        text = "🤕 Где вы чувствуете недомогание?"

        buttons = [
            [
                {"type": "callback", "text": "Голова", "payload": "symptom_head"},
                {"type": "callback", "text": "Грудь", "payload": "symptom_chest"}
            ],
            [
                {"type": "callback", "text": "Живот", "payload": "symptom_abdomen"},
                {"type": "callback", "text": "Спина", "payload": "symptom_back"}
            ],
            [
                {"type": "callback", "text": "Конечности", "payload": "symptom_limbs"},
                {"type": "callback", "text": "Общее недомогание", "payload": "symptom_general"}
            ]
        ]

        await self.max_api.send_message_with_keyboard(chat_id, text, buttons)

    async def _handle_find_clinic(self, chat_id: int):
        """Поиск клиник"""
        text = "🏥 Поиск медицинских учреждений\n\nВыберите тип учреждения:"

        buttons = [
            [
                {"type": "callback", "text": "🩺 Поликлиника", "payload": "clinic_polyclinic"},
                {"type": "callback", "text": "🏥 Больница", "payload": "clinic_hospital"}
            ],
            [
                {"type": "callback", "text": "🧪 Лаборатория", "payload": "clinic_lab"},
                {"type": "callback", "text": "📊 Диагностика", "payload": "clinic_diagnostic"}
            ],
            [
                {"type": "callback", "text": "📍 Рядом со мной", "payload": "clinics_nearby"}
            ]
        ]

        await self.max_api.send_message_with_keyboard(chat_id, text, buttons)

    async def _handle_community_suggestions(self, chat_id: int, profile: UserProfile):
        """Предложить сообщества по заболеваниям пользователя"""
        if not hasattr(profile, 'conditions') or not profile.conditions:
            text = "👥 У вас нет зарегистрированных заболеваний для подключения к сообществам."
            text += "\n\nЕсли у вас есть заболевание, добавьте его в профиль для получения поддержки!"
            buttons = [
                [{"type": "callback", "text": "👤 Добавить заболевание", "payload": "add_condition"}]
            ]
        else:
            text = "👥 Рекомендуемые сообщества поддержки:\n\n"
            text += "• 💙 Сообщество по гипертонии\n"
            text += "• 🩸 Сообщество по диабету\n"
            text += "• 🌀 Сообщество по мигрени\n\n"
            text += "Присоединяйтесь к сообществам для обмена опытом и поддержки!"

            buttons = [
                [{"type": "link", "text": "💙 Присоединиться к сообществу по гипертонии", "url": "https://max.example.com/chat/hypertension"}],
                [{"type": "link", "text": "🩸 Присоединиться к сообществу по диабету", "url": "https://max.example.com/chat/diabetes"}],
                [{"type": "callback", "text": "📋 Все сообщества", "payload": "all_communities"}]
            ]

        await self.max_api.send_message_with_keyboard(chat_id, text, buttons)

    async def _handle_profile_management(self, chat_id: int, user_id: int, profile: UserProfile = None):
        """Управление профилем"""
        if profile:
            text = f"""👤 Ваш профиль:

• Возраст: {getattr(profile, 'age', 'Не указан')} лет
• Пол: {'Мужской' if getattr(profile, 'gender', 'male') == 'male' else 'Женский'}
• Факторы риска: {len(getattr(profile, 'risk_factors', []))}
• Заболевания: {len(getattr(profile, 'conditions', []))}

Обновлено: {getattr(profile, 'updated_at', 'Неизвестно')}"""

            buttons = [
                [
                    {"type": "callback", "text": "✏️ Редактировать", "payload": "edit_profile"},
                    {"type": "callback", "text": "🩺 Добавить заболевание", "payload": "add_condition"}
                ],
                [
                    {"type": "callback", "text": "📊 Добавить показатели", "payload": "add_metrics"},
                    {"type": "callback", "text": "📈 Статистика", "payload": "health_stats"}
                ],
                [{"type": "callback", "text": "↩️ Назад", "payload": "main_menu"}]
            ]
        else:
            text = "👤 Профиль не найден\n\nДавайте создадим ваш персональный профиль для точных рекомендаций!"
            buttons = [
                [{"type": "callback", "text": "📝 Создать профиль", "payload": "create_profile"}],
                [{"type": "callback", "text": "↩️ Назад", "payload": "main_menu"}]
            ]

        await self.max_api.send_message_with_keyboard(chat_id, text, buttons)

    async def _handle_help(self, chat_id: int):
        """Справка"""
        help_text = """ℹ️ Справка по Health Compass:

Основные команды:
• /start - Главное меню
• "Здоровье" - Основное меню
• "Обследования" - Персональный календарь
• "Симптомы" - Анализ симптомов
• "Клиники" - Поиск медицинских учреждений
• "Сообщества" - Группы поддержки
• "Профиль" - Управление профилем
• "Помощь" - Эта справка

💡 Используйте кнопки для удобной навигации!"""

        buttons = [
            [{"type": "callback", "text": "💉 Начать с обследований", "payload": "my_screenings"}],
            [{"type": "callback", "text": "🤕 Проанализировать симптомы", "payload": "symptoms"}],
            [{"type": "callback", "text": "↩️ Главное меню", "payload": "main_menu"}]
        ]

        await self.max_api.send_message_with_keyboard(chat_id, help_text, buttons)

    async def _handle_unknown(self, chat_id: int):
        """Неизвестная команда"""
        text = """🤔 Я не понял вашу команду.

Используйте кнопки ниже или введите:
• "Здоровье" - для основного меню
• "Обследования" - для календаря обследований  
• "Симптомы" - для анализа симптомов
• "Помощь" - для справки"""

        buttons = [
            [
                {"type": "callback", "text": "💉 Обследования", "payload": "my_screenings"},
                {"type": "callback", "text": "🤕 Симптомы", "payload": "symptoms"}
            ],
            [
                {"type": "callback", "text": "🏥 Клиники", "payload": "find_clinic"},
                {"type": "callback", "text": "👤 Профиль", "payload": "profile"}
            ],
            [{"type": "callback", "text": "ℹ️ Помощь", "payload": "help"}]
        ]

        await self.max_api.send_message_with_keyboard(chat_id, text, buttons)

    async def _ask_for_profile(self, chat_id: int):
        """Запрос на создание профиля"""
        text = "📝 Для персонализированных рекомендаций нужен ваш профиль.\n\nДавайте создадим его!"

        buttons = [
            [{"type": "callback", "text": "📝 Создать профиль", "payload": "create_profile"}],
            [{"type": "callback", "text": "🚫 Пропустить", "payload": "skip_profile"}]
        ]

        await self.max_api.send_message_with_keyboard(chat_id, text, buttons)