from typing import Dict, Any, Optional
from datetime import datetime
from models.health_models import SymptomSession


class SymptomChecker:
    def __init__(self):
        self.symptom_rules = self._load_symptom_rules()

    def _load_symptom_rules(self) -> Dict[str, Any]:
        return {
            "headache": {
                "questions": [
                    {
                        "text": "Опишите боль?",
                        "options": ["Острая", "Тупая/Ноющая", "Пульсирующая", "Давящая"],
                        "key": "pain_type"
                    },
                    {
                        "text": "Как долго длится?",
                        "options": ["Несколько часов", "Несколько дней", "Периодически неделями"],
                        "key": "duration"
                    },
                    {
                        "text": "Есть ли тошнота?",
                        "options": ["Да", "Нет"],
                        "key": "nausea"
                    },
                    {
                        "text": "Нарушено ли зрение?",
                        "options": ["Да", "Нет"],
                        "key": "vision_problems"
                    }
                ],
                "recommendations": {
                    "default": {
                        "specialists": ["Терапевт", "Невролог"],
                        "examinations": ["Общий анализ крови", "Измерение артериального давления"],
                        "urgency": "medium",
                        "message": "Рекомендуем обратиться к специалисту для уточнения диагноза"
                    },
                    "pulsating_nausea_vision": {
                        "specialists": ["Невролог", "Офтальмолог"],
                        "examinations": ["МРТ головного мозга", "Осмотр глазного дна", "Общий анализ крови"],
                        "urgency": "high",
                        "message": "⚠️ Возможна мигрень или повышенное внутричерепное давление"
                    }
                }
            },
            "back_pain": {
                "questions": [
                    {
                        "text": "Локализация боли?",
                        "options": ["Верх спины", "Поясница", "Копчик"],
                        "key": "location"
                    },
                    {
                        "text": "Характер боли?",
                        "options": ["Острая", "Ноющая", "Стреляющая"],
                        "key": "pain_type"
                    },
                    {
                        "text": "Отдает в ноги?",
                        "options": ["Да", "Нет"],
                        "key": "radiates_to_legs"
                    }
                ],
                "recommendations": {
                    "default": {
                        "specialists": ["Терапевт", "Ортопед"],
                        "examinations": ["Рентген позвоночника", "Общий анализ крови"],
                        "urgency": "medium",
                        "message": "Рекомендуем консультацию специалиста"
                    },
                    "shooting_legs": {
                        "specialists": ["Невролог", "Ортопед"],
                        "examinations": ["МРТ позвоночника", "Консультация невролога"],
                        "urgency": "high",
                        "message": "⚠️ Возможны проблемы с межпозвонковыми дисками"
                    }
                }
            }
        }

    async def start_symptom_check(self, body_part: str, user_id: int) -> Optional[Dict[str, Any]]:
        if body_part not in self.symptom_rules:
            return None

        session = SymptomSession(
            user_id=user_id,
            body_part=body_part,
            current_question=0
        )

        return self._get_next_question(session)

    def _get_next_question(self, session: SymptomSession) -> Optional[Dict[str, Any]]:
        rules = self.symptom_rules[session.body_part]
        questions = rules["questions"]

        if session.current_question >= len(questions):
            return self._generate_recommendation(session)

        question_data = questions[session.current_question]
        return {
            "type": "question",
            "text": question_data["text"],
            "options": question_data["options"],
            "question_index": session.current_question,
            "key": question_data["key"]
        }

    def _generate_recommendation(self, session: SymptomSession) -> Dict[str, Any]:
        rules = self.symptom_rules[session.body_part]
        answers_key = self._build_answers_key(session.answers)

        recommendation = rules["recommendations"].get(answers_key, rules["recommendations"]["default"])

        return {
            "type": "recommendation",
            "specialists": recommendation["specialists"],
            "examinations": recommendation["examinations"],
            "urgency": recommendation["urgency"],
            "message": recommendation["message"],
            "find_clinics": True
        }

    def _build_answers_key(self, answers: Dict[str, Any]) -> str:
        key_parts = []
        for answer in answers.values():
            if isinstance(answer, str):
                key_parts.append(answer.lower().replace(" ", "_"))
        return "_".join(key_parts)

    def process_answer(self, session: SymptomSession, question_index: int, answer: str) -> SymptomSession:
        rules = self.symptom_rules[session.body_part]
        question = rules["questions"][question_index]

        session.answers[question["key"]] = answer
        session.current_question += 1

        return session