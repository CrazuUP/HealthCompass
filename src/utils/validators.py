# app/utils/validators.py
import re
from typing import Dict, Any, Tuple, Optional
from datetime import datetime


def validate_age(age: int) -> Tuple[bool, Optional[str]]:
    """
    Валидация возраста пользователя

    Args:
        age: Возраст для проверки

    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    if not isinstance(age, int):
        return False, "Возраст должен быть целым числом"

    if age < 0:
        return False, "Возраст не может быть отрицательным"

    if age > 120:
        return False, "Возраст не может превышать 120 лет"

    return True, None


def validate_blood_pressure(systolic: int, diastolic: int) -> Tuple[bool, Optional[str]]:
    """
    Валидация артериального давления

    Args:
        systolic: Систолическое давление (верхнее)
        diastolic: Диастолическое давление (нижнее)

    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    if not isinstance(systolic, int) or not isinstance(diastolic, int):
        return False, "Давление должно быть целым числом"

    if systolic < 60:
        return False, "Систолическое давление слишком низкое"

    if systolic > 250:
        return False, "Систолическое давление слишком высокое"

    if diastolic < 40:
        return False, "Диастолическое давление слишком низкое"

    if diastolic > 150:
        return False, "Диастолическое давление слишком высокое"

    if systolic <= diastolic:
        return False, "Систолическое давление должно быть выше диастолического"

    return True, None


def validate_pulse(pulse: int) -> Tuple[bool, Optional[str]]:
    """
    Валидация пульса

    Args:
        pulse: Пульс (уд/мин)

    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    if not isinstance(pulse, int):
        return False, "Пульс должен быть целым числом"

    if pulse < 30:
        return False, "Пульс слишком низкий"

    if pulse > 200:
        return False, "Пульс слишком высокий"

    return True, None


def validate_temperature(temperature: float) -> Tuple[bool, Optional[str]]:
    """
    Валидация температуры тела

    Args:
        temperature: Температура в °C

    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    if not isinstance(temperature, (int, float)):
        return False, "Температура должна быть числом"

    if temperature < 35.0:
        return False, "Температура слишком низкая"

    if temperature > 42.0:
        return False, "Температура слишком высокая"

    return True, None


def validate_weight(weight: float) -> Tuple[bool, Optional[str]]:
    """
    Валидация веса

    Args:
        weight: Вес в кг

    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    if not isinstance(weight, (int, float)):
        return False, "Вес должен быть числом"

    if weight <= 0:
        return False, "Вес должен быть положительным числом"

    if weight > 300:
        return False, "Вес слишком большой"

    return True, None


def validate_medical_condition(condition_data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    Валидация данных медицинского состояния

    Args:
        condition_data: Данные о заболевании

    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    required_fields = ['condition_id', 'name']

    for field in required_fields:
        if field not in condition_data:
            return False, f"Отсутствует обязательное поле: {field}"

    if not isinstance(condition_data['condition_id'], str):
        return False, "ID заболевания должен быть строкой"

    if not isinstance(condition_data['name'], str):
        return False, "Название заболевания должно быть строкой"

    # Проверка даты диагноза, если указана
    if 'diagnosis_date' in condition_data and condition_data['diagnosis_date']:
        try:
            if isinstance(condition_data['diagnosis_date'], str):
                datetime.fromisoformat(condition_data['diagnosis_date'].replace('Z', '+00:00'))
            elif not isinstance(condition_data['diagnosis_date'], datetime):
                return False, "Неверный формат даты диагноза"
        except ValueError:
            return False, "Неверный формат даты диагноза"

    # Проверка severity, если указан
    if 'severity' in condition_data and condition_data['severity']:
        valid_severities = ['mild', 'moderate', 'severe', 'critical']
        if condition_data['severity'] not in valid_severities:
            return False, f"Степень тяжести должна быть одним из: {', '.join(valid_severities)}"

    return True, None


def validate_user_profile(profile_data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    Валидация данных профиля пользователя

    Args:
        profile_data: Данные профиля пользователя

    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    required_fields = ['user_id', 'gender', 'age']

    for field in required_fields:
        if field not in profile_data:
            return False, f"Отсутствует обязательное поле: {field}"

    # Валидация user_id
    if not isinstance(profile_data['user_id'], int):
        return False, "ID пользователя должен быть целым числом"

    if profile_data['user_id'] <= 0:
        return False, "ID пользователя должен быть положительным числом"

    # Валидация gender
    valid_genders = ['male', 'female']
    if profile_data['gender'] not in valid_genders:
        return False, f"Пол должен быть одним из: {', '.join(valid_genders)}"

    # Валидация age
    age_valid, age_error = validate_age(profile_data['age'])
    if not age_valid:
        return False, age_error

    # Валидация risk_factors
    if 'risk_factors' in profile_data:
        if not isinstance(profile_data['risk_factors'], list):
            return False, "Факторы риска должны быть списком"

        valid_risk_factors = ['smoking', 'alcohol', 'obesity', 'sedentary', 'family_history']
        for factor in profile_data['risk_factors']:
            if factor not in valid_risk_factors:
                return False, f"Неверный фактор риска: {factor}"

    # Валидация conditions
    if 'conditions' in profile_data:
        if not isinstance(profile_data['conditions'], list):
            return False, "Заболевания должны быть списком"

        for condition in profile_data['conditions']:
            condition_valid, condition_error = validate_medical_condition(condition)
            if not condition_valid:
                return False, condition_error

    # Валидация family_history
    if 'family_history' in profile_data:
        if not isinstance(profile_data['family_history'], list):
            return False, "Семейная история должна быть списком"

        for condition in profile_data['family_history']:
            if not isinstance(condition, str):
                return False, "Элементы семейной истории должны быть строками"

    # Валидация location
    if 'location' in profile_data and profile_data['location']:
        if not isinstance(profile_data['location'], str):
            return False, "Локация должна быть строкой"

    return True, None


def validate_blood_pressure_string(pressure_str: str) -> Tuple[bool, Optional[Dict[str, int]]]:
    """
    Валидация строки артериального давления формата "120/80"

    Args:
        pressure_str: Строка давления

    Returns:
        Tuple[bool, Optional[Dict[str, int]]]: (is_valid, parsed_pressure)
    """
    pattern = r'^(\d{2,3})/(\d{2,3})$'
    match = re.match(pattern, pressure_str)

    if not match:
        return False, None

    try:
        systolic = int(match.group(1))
        diastolic = int(match.group(2))

        is_valid, error = validate_blood_pressure(systolic, diastolic)
        if not is_valid:
            return False, None

        return True, {'systolic': systolic, 'diastolic': diastolic}

    except (ValueError, TypeError):
        return False, None


def validate_health_metric(metric_type: str, value: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    Валидация метрики здоровья

    Args:
        metric_type: Тип метрики
        value: Значение метрики

    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    if metric_type == 'pressure':
        if 'systolic' not in value or 'diastolic' not in value:
            return False, "Для давления требуются systolic и diastolic"

        return validate_blood_pressure(value['systolic'], value['diastolic'])

    elif metric_type == 'pulse':
        if 'value' not in value:
            return False, "Для пульса требуется value"

        return validate_pulse(value['value'])

    elif metric_type == 'temperature':
        if 'value' not in value:
            return False, "Для температуры требуется value"

        return validate_temperature(value['value'])

    elif metric_type == 'weight':
        if 'value' not in value:
            return False, "Для веса требуется value"

        return validate_weight(value['value'])

    else:
        return False, f"Неизвестный тип метрики: {metric_type}"


def sanitize_user_input(text: str) -> str:
    """
    Очистка пользовательского ввода от потенциально опасных символов

    Args:
        text: Входной текст

    Returns:
        str: Очищенный текст
    """
    if not text:
        return ""

    # Удаляем потенциально опасные символы
    sanitized = re.sub(r'[<>{}[\]$&|`]', '', text)

    # Ограничиваем длину
    return sanitized[:1000]


def validate_email(email: str) -> bool:
    """
    Валидация email адреса

    Args:
        email: Email для проверки

    Returns:
        bool: Валиден ли email
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_phone(phone: str) -> bool:
    """
    Валидация номера телефона

    Args:
        phone: Номер телефона для проверки

    Returns:
        bool: Валиден ли номер телефона
    """
    # Российские номера: +7XXXXXXXXXX, 8XXXXXXXXXX, +375XXXXXXXXX и т.д.
    pattern = r'^(\+7|8|\+375|\+374|\+994|\+995|\+996|\+998)[0-9]{7,14}$'
    cleaned_phone = re.sub(r'[\s\-\(\)]', '', phone)
    return bool(re.match(pattern, cleaned_phone))