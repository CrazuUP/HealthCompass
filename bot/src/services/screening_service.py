from datetime import datetime
from typing import List, Dict, Any
from models.health_models import UserProfile, ScreeningRecommendation, Gender, RiskFactor


class ScreeningService:
    def __init__(self):
        self.recommendations = self._load_recommendations()

    def _load_recommendations(self) -> List[ScreeningRecommendation]:
        return [
            ScreeningRecommendation(
                id="blood_pressure",
                name="Измерение артериального давления",
                description="Контроль артериального давления",
                frequency_years=1,
                start_age=18
            ),
            ScreeningRecommendation(
                id="blood_sugar_40",
                name="Анализ крови на сахар",
                description="Контроль уровня глюкозы для выявления диабета",
                frequency_years=3,
                start_age=40,
                risk_factors_required=[RiskFactor.OBESITY, RiskFactor.FAMILY_HISTORY]
            ),
            ScreeningRecommendation(
                id="cholesterol_35",
                name="Анализ на холестерин",
                description="Контроль липидного профиля",
                frequency_years=5,
                start_age=35
            ),
            ScreeningRecommendation(
                id="psa_men_45",
                name="Анализ ПСА",
                description="Скрининг рака простаты",
                frequency_years=2,
                start_age=45,
                gender_specific=Gender.MALE
            ),
            ScreeningRecommendation(
                id="mammography_40",
                name="Маммография",
                description="Скрининг рака молочной железы",
                frequency_years=2,
                start_age=40,
                gender_specific=Gender.FEMALE
            ),
            ScreeningRecommendation(
                id="ct_lungs_smokers",
                name="Низкодозовая КТ легких",
                description="Скрининг рака легких для курильщиков",
                frequency_years=1,
                start_age=40,
                risk_factors_required=[RiskFactor.SMOKING]
            ),
            ScreeningRecommendation(
                id="colonoscopy_50",
                name="Колоноскопия",
                description="Скрининг рака толстой кишки",
                frequency_years=10,
                start_age=50
            )
        ]

    def get_personalized_schedule(self, profile: UserProfile) -> List[Dict[str, Any]]:
        schedule = []
        current_year = datetime.now().year

        for rec in self.recommendations:
            if profile.age < rec.start_age or (rec.end_age and profile.age > rec.end_age):
                continue

            if rec.gender_specific and rec.gender_specific != profile.gender:
                continue

            if rec.risk_factors_required and not any(
                    factor in profile.risk_factors for factor in rec.risk_factors_required
            ):
                continue

            if rec.conditions_required and not any(
                    cond.condition_id in rec.conditions_required for cond in profile.conditions
            ):
                continue

            schedule.append({
                "recommendation": rec,
                "next_due": current_year,
                "priority": "high" if rec.frequency_years <= 2 else "medium"
            })

        return sorted(schedule, key=lambda x: x["priority"])

    def format_schedule_message(self, profile: UserProfile) -> str:
        schedule = self.get_personalized_schedule(profile)

        if not schedule:
            return "🎉 Отлично! По вашим данным все плановые обследования пройдены."

        message = "📅 Ваш персональный календарь обследований:\n\n"

        for item in schedule:
            rec = item["recommendation"]
            message += f"• {rec.name}\n"
            message += f"  📋 {rec.description}\n"
            message += f"  🗓️ Каждые {rec.frequency_years} лет\n"
            message += f"  🚨 {item['priority'].upper()}\n\n"

        message += "💡 Нажмите на обследование, чтобы найти клинику"
        return message