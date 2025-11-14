from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"

class RiskFactor(str, Enum):
    SMOKING = "smoking"
    ALCOHOL = "alcohol"
    OBESITY = "obesity"
    SEDENTARY = "sedentary"
    FAMILY_HISTORY = "family_history"

class MedicalCondition(BaseModel):
    condition_id: str
    name: str
    diagnosis_date: Optional[datetime] = None
    severity: Optional[str] = None

class UserProfile(BaseModel):
    user_id: int
    gender: Gender
    age: int = Field(ge=0, le=120)
    risk_factors: List[RiskFactor] = []
    conditions: List[MedicalCondition] = []
    family_history: List[str] = []
    location: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class ScreeningRecommendation(BaseModel):
    id: str
    name: str
    description: str
    frequency_years: int
    start_age: int
    end_age: Optional[int] = None
    gender_specific: Optional[Gender] = None
    risk_factors_required: List[RiskFactor] = []
    conditions_required: List[str] = []

class HealthMetric(BaseModel):
    user_id: int
    metric_type: str
    value: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.now)
    notes: Optional[str] = None

class SymptomSession(BaseModel):
    user_id: int
    body_part: str
    current_question: int = 0
    answers: Dict[str, Any] = {}
    started_at: datetime = Field(default_factory=datetime.now)