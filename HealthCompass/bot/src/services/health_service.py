from typing import List, Dict, Any, Optional
from datetime import datetime
from models.health_models import UserProfile, HealthMetric, MedicalCondition


class HealthService:
    def __init__(self):
        # Временное хранилище (в продакшене заменить на БД)
        self.user_profiles = {}
        self.health_metrics = {}

    async def create_user_profile(self, user_id: int, profile_data: Dict[str, Any]) -> UserProfile:
        profile = UserProfile(
            user_id=user_id,
            **profile_data
        )
        self.user_profiles[user_id] = profile
        return profile

    async def get_user_profile(self, user_id: int) -> Optional[UserProfile]:
        return self.user_profiles.get(user_id)

    async def update_user_profile(self, user_id: int, updates: Dict[str, Any]) -> Optional[UserProfile]:
        if user_id not in self.user_profiles:
            return None

        profile = self.user_profiles[user_id]

        # Обновляем поля
        for key, value in updates.items():
            if hasattr(profile, key):
                setattr(profile, key, value)

        profile.updated_at = datetime.now()
        return profile

    async def add_health_metric(self, user_id: int, metric_type: str, value: Dict[str, Any],
                                notes: str = None) -> HealthMetric:
        metric = HealthMetric(
            user_id=user_id,
            metric_type=metric_type,
            value=value,
            notes=notes
        )

        if user_id not in self.health_metrics:
            self.health_metrics[user_id] = []

        self.health_metrics[user_id].append(metric)
        return metric

    async def get_user_metrics(self, user_id: int, metric_type: str = None, limit: int = 10) -> List[HealthMetric]:
        if user_id not in self.health_metrics:
            return []

        metrics = self.health_metrics[user_id]

        if metric_type:
            metrics = [m for m in metrics if m.metric_type == metric_type]

        return sorted(metrics, key=lambda x: x.timestamp, reverse=True)[:limit]

    async def add_medical_condition(self, user_id: int, condition_data: Dict[str, Any]) -> Optional[UserProfile]:
        profile = await self.get_user_profile(user_id)
        if not profile:
            return None

        condition = MedicalCondition(**condition_data)
        profile.conditions.append(condition)
        profile.updated_at = datetime.now()

        return profile

    async def get_health_summary(self, user_id: int) -> Dict[str, Any]:
        profile = await self.get_user_profile(user_id)
        if not profile:
            return {"error": "Profile not found"}

        metrics = await self.get_user_metrics(user_id, limit=5)

        return {
            "profile": profile,
            "recent_metrics": metrics,
            "conditions_count": len(profile.conditions),
            "metrics_count": len(metrics),
            "last_update": profile.updated_at
        }

    async def analyze_health_trends(self, user_id: int, metric_type: str) -> Dict[str, Any]:
        metrics = await self.get_user_metrics(user_id, metric_type, limit=20)

        if len(metrics) < 2:
            return {"message": "Недостаточно данных для анализа"}

        # Простой анализ трендов
        values = [m.value.get('value', 0) for m in metrics if 'value' in m.value]

        if not values:
            return {"message": "Нет числовых данных для анализа"}

        avg_value = sum(values) / len(values)
        trend = "стабильный"

        if len(values) >= 3:
            recent_avg = sum(values[:3]) / 3
            older_avg = sum(values[-3:]) / 3
            if recent_avg > older_avg * 1.1:
                trend = "растущий"
            elif recent_avg < older_avg * 0.9:
                trend = "снижающийся"

        return {
            "average": round(avg_value, 2),
            "trend": trend,
            "data_points": len(values),
            "latest_value": values[0] if values else None
        }