from typing import Dict, Any
from services.max_api import MaxApiService
from services.health_service import HealthService
from services.symptom_checker import SymptomChecker
from services.community_service import CommunityService
from models.health_models import UserProfile, Gender, RiskFactor, SymptomSession


class CallbackHandler:
    def __init__(self):
        self.max_api = MaxApiService()
        self.health_service = HealthService()
        self.symptom_checker = SymptomChecker()
        self.community_service = CommunityService()

        # Временное хранилище сессий
        self.user_sessions = {}
        self.symptom_sessions = {}

    async def handle_callback(self, callback: Dict[str, Any], message: Dict[str, Any] = None):
        """Обработка callback от кнопок"""
        payload = callback.get("payload", "")
        user = callback.get("user", {})
        user_id = user.get("user_id")
        chat_id = callback.get("user", {}).get("user_id")

        if not chat_id and message:
            chat_id = message.get("recipient", {}).get("chat_id")

        # Логирование для отладки
        print(f"Processing callback: {payload} for user {user_id}")

        # Обработка разных типов callback
        if payload == "main_menu":
            await self._handle_main_menu(chat_id, user_id)
        elif payload == "my_screenings":
            await self._handle_my_screenings(chat_id, user_id)
        elif payload == "symptoms":
            await self._handle_symptoms(chat_id)
        elif payload.startswith("symptom_"):
            await self._handle_symptom_selection(chat_id, user_id, payload)
        elif payload.startswith("symptom_answer_"):
            await self._handle_symptom_answer(chat_id, user_id, payload, callback)
        elif payload == "find_clinic":
            await self._handle_find_clinic(chat_id)
        elif payload == "health_diary":
            await self._handle_health_diary(chat_id, user_id)
        elif payload == "communities":
            await self._handle_communities(chat_id, user_id)
        elif payload == "profile":
            await self._handle_profile(chat_id, user_id)
        elif payload == "help":
            await self._handle_help(chat_id)
        elif payload == "create_profile":
            await self._handle_create_profile(chat_id, user_id)
        elif payload == "edit_profile":
            await self._handle_edit_profile(chat_id, user_id)
        elif payload == "add_condition":
            await self._handle_add_condition(chat_id, user_id)
        elif payload == "all_communities":
            await self._handle_all_communities(chat_id)
        else:
            await self._handle_unknown_callback(chat_id)

    async def _handle_main_menu(self, chat_id: int, user_id: int):
        """Главное меню"""
        from handlers.message_handler import MessageHandler
        message_handler = MessageHandler()
        await message_handler._handle_start(chat_id, {"user_id": user_id, "first_name": "Пользователь"})

    async def _handle_my_screenings(self, chat_id: int, user_id: int):
        """Мои обследования"""
        profile = await self.health_service.get_user_profile(user_id)

        if profile:
            from handlers.message_handler import MessageHandler
            message_handler = MessageHandler()
            await message_handler._handle_screening_schedule(chat_id, profile)
        else:
            await self._ask_for_profile(chat_id)

    async def _handle_symptoms(self, chat_id: int):
        """Симптомы"""
        from handlers.message_handler import MessageHandler
        message_handler = MessageHandler()
        await message_handler._handle_symptoms_start(chat_id)

    async def _handle_symptom_selection(self, chat_id: int, user_id: int, payload: str):
        """Выбор симптома"""
        body_part_map = {
            "symptom_head": "headache",
            "symptom_chest": "chest_pain",
            "symptom_abdomen": "abdominal_pain",
            "symptom_back": "back_pain",
            "symptom_limbs": "limb_pain",
            "symptom_general": "general_pain"
        }

        symptom_type = body_part_map.get(payload, "general_pain")

        # Начинаем сессию опроса
        question = await self.symptom_checker.start_symptom_check(symptom_type, user_id)

        if question:
            self.symptom_sessions[user_id] = SymptomSession(
                user_id=user_id,
                body_part=symptom_type,
                current_question=0
            )

            await self._send_symptom_question(chat_id, question)

    async def _handle_symptom_answer(self, chat_id: int, user_id: int, payload: str, callback: Dict[str, Any]):
        """Обработка ответа на вопрос о симптомах"""
        if user_id not in self.symptom_sessions:
            await self.max_api.send_message(chat_id, "❌ Сессия опроса не найдена. Начните заново.")
            return

        # Парсим payload: symptom_answer_0_1 -> question_index=0, answer_index=1
        parts = payload.split("_")
        if len(parts) != 4:
            await self.max_api.send_message(chat_id, "❌ Ошибка формата ответа.")
            return

        question_index = int(parts[2])
        answer_index = int(parts[3])

        session = self.symptom_sessions[user_id]

        # Получаем вопрос и ответ
        rules = self.symptom_checker.symptom_rules[session.body_part]
        question = rules["questions"][question_index]
        answer_text = question["options"][answer_index]

        # Обрабатываем ответ
        session = self.symptom_checker.process_answer(session, question_index, answer_text)
        self.symptom_sessions[user_id] = session

        # Получаем следующий вопрос или рекомендацию
        next_step = self.symptom_checker._get_next_question(session)

        if next_step["type"] == "question":
            await self._send_symptom_question(chat_id, next_step)
        else:
            # Показываем рекомендацию
            await self._show_symptom_recommendation(chat_id, next_step)
            # Очищаем сессию
            del self.symptom_sessions[user_id]

    async def _send_symptom_question(self, chat_id: int, question: Dict[str, Any]):
        """Отправка вопроса о симптомах"""
        buttons = []
        for i, option in enumerate(question["options"]):
            buttons.append([
                {
                    "type": "callback",
                    "text": option,
                    "payload": f"symptom_answer_{question['question_index']}_{i}"
                }
            ])

        await self.max_api.send_message_with_keyboard(chat_id, question["text"], buttons)

    async def _show_symptom_recommendation(self, chat_id: int, recommendation: Dict[str, Any]):
        """Показать рекомендацию по симптомам"""
        text = f"🎯 Рекомендации:\n\n{recommendation['message']}\n\n"
        text += f"👨‍⚕️ Специалисты: {', '.join(recommendation['specialists'])}\n"
        text += f"📋 Обследования: {', '.join(recommendation['examinations'])}\n"
        text += f"🚨 Срочность: {'Высокая' if recommendation['urgency'] == 'high' else 'Средняя'}"

        buttons = [
            [{"type": "callback", "text": "🏥 Найти клинику", "payload": "find_clinic"}],
            [{"type": "callback", "text": "🤕 Новый симптом", "payload": "symptoms"}],
            [{"type": "callback", "text": "↩️ Главное меню", "payload": "main_menu"}]
        ]

        await self.max_api.send_message_with_keyboard(chat_id, text, buttons)

    async def _handle_find_clinic(self, chat_id: int):
        """Поиск клиник"""
        from handlers.message_handler import MessageHandler
        message_handler = MessageHandler()
        await message_handler._handle_find_clinic(chat_id)

    async def _handle_health_diary(self, chat_id: int, user_id: int):
        """Дневник здоровья"""
        profile = await self.health_service.get_user_profile(user_id)

        if not profile:
            await self._ask_for_profile(chat_id)
            return

        health_summary = await self.health_service.get_health_summary(user_id)

        text = "📊 Ваш дневник здоровья:\n\n"
        text += f"• Заболевания: {health_summary['conditions_count']}\n"
        text += f"• Записей показателей: {health_summary['metrics_count']}\n"
        text += f"• Последнее обновление: {health_summary['last_update'].strftime('%d.%m.%Y')}\n\n"

        if health_summary['recent_metrics']:
            text += "📈 Последние показатели:\n"
            for metric in health_summary['recent_metrics'][:3]:
                text += f"• {metric.metric_type}: {metric.value}\n"

        buttons = [
            [
                {"type": "callback", "text": "❤️ Давление", "payload": "add_pressure"},
                {"type": "callback", "text": "💓 Пульс", "payload": "add_pulse"}
            ],
            [
                {"type": "callback", "text": "🌡️ Температура", "payload": "add_temperature"},
                {"type": "callback", "text": "⚖️ Вес", "payload": "add_weight"}
            ],
            [{"type": "callback", "text": "📈 Статистика", "payload": "health_stats"}],
            [{"type": "callback", "text": "↩️ Назад", "payload": "main_menu"}]
        ]

        await self.max_api.send_message_with_keyboard(chat_id, text, buttons)

    async def _handle_communities(self, chat_id: int, user_id: int):
        """Сообщества"""
        profile = await self.health_service.get_user_profile(user_id)

        if profile:
            from handlers.message_handler import MessageHandler
            message_handler = MessageHandler()
            await message_handler._handle_community_suggestions(chat_id, profile)
        else:
            await self._ask_for_profile(chat_id)

    async def _handle_profile(self, chat_id: int, user_id: int):
        """Профиль"""
        from handlers.message_handler import MessageHandler
        message_handler = MessageHandler()
        profile = await self.health_service.get_user_profile(user_id)
        await message_handler._handle_profile_management(chat_id, user_id, profile)

    async def _handle_help(self, chat_id: int):
        """Помощь"""
        from handlers.message_handler import MessageHandler
        message_handler = MessageHandler()
        await message_handler._handle_help(chat_id)

    async def _handle_create_profile(self, chat_id: int, user_id: int):
        """Создание профиля"""
        text = "📝 Создание профиля\n\nДля персонализированных рекомендаций нужна базовая информация."

        buttons = [
            [{"type": "callback", "text": "👨 Мужской", "payload": "profile_gender_male"}],
            [{"type": "callback", "text": "👩 Женский", "payload": "profile_gender_female"}],
            [{"type": "callback", "text": "↩️ Отмена", "payload": "main_menu"}]
        ]

        await self.max_api.send_message_with_keyboard(chat_id, text, buttons)

    async def _handle_edit_profile(self, chat_id: int, user_id: int):
        """Редактирование профиля"""
        text = "✏️ Редактирование профиля\n\nЧто хотите изменить?"

        buttons = [
            [{"type": "callback", "text": "🎂 Возраст", "payload": "edit_age"}],
            [{"type": "callback", "text": "🚬 Факторы риска", "payload": "edit_risks"}],
            [{"type": "callback", "text": "🩺 Заболевания", "payload": "edit_conditions"}],
            [{"type": "callback", "text": "👨‍👩‍👧‍👦 Семейная история", "payload": "edit_family"}],
            [{"type": "callback", "text": "↩️ Назад", "payload": "profile"}]
        ]

        await self.max_api.send_message_with_keyboard(chat_id, text, buttons)

    async def _handle_add_condition(self, chat_id: int, user_id: int):
        """Добавление заболевания"""
        text = "🩺 Добавление заболевания\n\nВыберите заболевание:"

        buttons = [
            [{"type": "callback", "text": "💙 Гипертония", "payload": "condition_hypertension"}],
            [{"type": "callback", "text": "🩸 Диабет", "payload": "condition_diabetes"}],
            [{"type": "callback", "text": "🎨 Витилиго", "payload": "condition_vitiligo"}],
            [{"type": "callback", "text": "🌀 Мигрень", "payload": "condition_migraine"}],
            [{"type": "callback", "text": "📝 Другое", "payload": "condition_other"}],
            [{"type": "callback", "text": "↩️ Назад", "payload": "profile"}]
        ]

        await self.max_api.send_message_with_keyboard(chat_id, text, buttons)

    async def _handle_all_communities(self, chat_id: int):
        """Все сообщества"""
        communities = self.community_service.get_all_communities()

        text = "👥 Все сообщества поддержки:\n\n"

        for condition_id, community in communities.items():
            text += f"• {community['name']}\n"
            text += f"  {community['description']}\n\n"

        buttons = []
        for condition_id, community in communities.items():
            if community.get('max_chat_link'):
                buttons.append([
                    {
                        "type": "link",
                        "text": f"Присоединиться к {community['name']}",
                        "url": community['max_chat_link']
                    }
                ])

        buttons.append([{"type": "callback", "text": "↩️ Назад", "payload": "communities"}])

        await self.max_api.send_message_with_keyboard(chat_id, text, buttons)

    async def _handle_unknown_callback(self, chat_id: int):
        """Неизвестный callback"""
        await self.max_api.send_message(chat_id, "❌ Неизвестная команда. Используйте кнопки меню.")
        await self._handle_main_menu(chat_id, 0)

    async def _ask_for_profile(self, chat_id: int):
        """Запрос на создание профиля"""
        from handlers.message_handler import MessageHandler
        message_handler = MessageHandler()
        await message_handler._ask_for_profile(chat_id)