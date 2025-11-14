from typing import Dict, Any, Optional


class CommunityService:
    def __init__(self):
        self.condition_communities = {
            "vitiligo": {
                "name": "Витилиго: поддержка и лечение",
                "description": "Сообщество людей с витилиго. Обсуждаем лечение, психологическую поддержку, истории успеха.",
                "max_chat_link": "https://max.ru/vitiligo_support",
                "success_stories": [
                    "Мария: Нашла эффективную схему лечения после 5 лет поисков",
                    "Алексей: Принял свою особенность и помогает другим"
                ]
            },
            "diabetes": {
                "name": "Сахарный диабет: жизнь без ограничений",
                "description": "Поддержка, обмен опытом, новости в лечении диабета.",
                "max_chat_link": "https://max.ru/diabetes_support",
                "success_stories": [
                    "Дмитрий: Сбросил 25 кг и контролирую диабет без лекарств",
                    "Ольга: Научилась жить полноценной жизнью с диабетом 1 типа"
                ]
            },
            "hypertension": {
                "name": "Гипертония под контролем",
                "description": "Обсуждаем контроль давления, питание, физические нагрузки.",
                "max_chat_link": "https://max.ru/hypertension_support",
                "success_stories": [
                    "Сергей: Нормализовал давление без таблеток через изменение образа жизни"
                ]
            },
            "migraine": {
                "name": "Мигрень и головные боли",
                "description": "Поиск триггеров, эффективные методы лечения, поддержка.",
                "max_chat_link": "https://max.ru/migraine_support"
            }
        }

    def get_community_for_condition(self, condition_id: str) -> Optional[Dict[str, Any]]:
        return self.condition_communities.get(condition_id)

    def format_community_message(self, condition_id: str) -> str:
        community = self.get_community_for_condition(condition_id)
        if not community:
            return "❌ Сообщество для вашего заболевания пока не создано"

        message = f"👥 {community['name']}\n\n"
        message += f"{community['description']}\n\n"

        if community.get('success_stories'):
            message += "✨ Истории успеха:\n"
            for story in community['success_stories'][:2]:
                message += f"• {story}\n"
            message += "\n"

        message += "💬 Присоединяйтесь к нашему сообществу!"
        return message

    def get_all_communities(self) -> Dict[str, Any]:
        return self.condition_communities