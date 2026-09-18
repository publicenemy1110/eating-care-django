"""Скрининговые опросники: доступ, парсинг ответов и подсчёт (не диагноз)."""

from .screenings_core import (
    EAT26_SCORE_MAP,
    FREQUENCY_CHOICES,
    Screening,
    VALID_RANGES,
)
from .screenings_data import (
    BAT_POSITIVE,
    BES_REVERSED,
    EAT26_REVERSED,
    RSES_REVERSED,
    SCREENINGS,
)

DISCLAIMER = (
    'Результаты носят исключительно скрининговый характер и не являются '
    'медицинским диагнозом. При тревожных ответах обратитесь к врачу или '
    'психотерапевту.'
)

__all__ = [
    'DISCLAIMER',
    'FREQUENCY_CHOICES',
    'SCREENINGS',
    'Screening',
    'get_screening',
    'parse_answers',
    'score_screening',
    'validate_answers',
]


def get_screening(slug: str) -> Screening | None:
    return SCREENINGS.get(slug)


def _eat26_points(raw: int, one_based_index: int) -> int:
    points = EAT26_SCORE_MAP.get(raw, 0)
    if one_based_index in EAT26_REVERSED:
        return 3 - points
    return points


def _sum_answers(answers: dict[str, int], questions: tuple) -> int:
    return sum(answers.get(q.id, 0) for q in questions)


def score_screening(slug: str, answers: dict[str, int]) -> dict:
    screening = SCREENINGS[slug]
    questions = screening.questions

    if slug == 'scoff':
        score = _sum_answers(answers, questions)
        level = 'elevated' if score >= 2 else 'low'
        summary = (
            'По результатам скрининга возможны признаки расстройства '
            'пищевого поведения. Рекомендуется консультация специалиста.'
            if level == 'elevated'
            else 'Скрининг не выявил выраженных признаков по критериям SCOFF.'
        )
    elif slug == 'eat26':
        score = sum(
            _eat26_points(answers.get(q.id, 0), i)
            for i, q in enumerate(questions, 1)
        )
        if score >= 20:
            level, summary = 'elevated', (
                'Повышенные показатели по EAT-26. Рекомендуется консультация специалиста.'
            )
        elif score >= 10:
            level, summary = 'moderate', (
                'Умеренные показатели. Имеет смысл обсудить результаты с психологом или врачом.'
            )
        else:
            level, summary = 'low', 'Низкие показатели по EAT-26.'
    elif slug == 'gad7':
        score = _sum_answers(answers, questions)
        if score <= 4:
            level, summary = 'minimal', 'Минимальный уровень тревожности по шкале GAD-7.'
        elif score <= 9:
            level, summary = 'mild', 'Лёгкая тревожность. При сохранении симптомов — консультация специалиста.'
        elif score <= 14:
            level, summary = 'moderate', 'Умеренная тревожность. Рекомендуется обсудить результаты со специалистом.'
        else:
            level, summary = 'severe', 'Выраженная тревожность. Рекомендуется обратиться к специалисту.'
    elif slug == 'phq9':
        score = _sum_answers(answers, questions)
        if score <= 4:
            level, summary = 'minimal', 'Минимальные симптомы депрессии по шкале PHQ-9.'
        elif score <= 9:
            level, summary = 'mild', 'Лёгкие симптомы. При сохранении — консультация специалиста.'
        elif score <= 14:
            level, summary = 'moderate', 'Умеренные симптомы. Рекомендуется обсудить результаты со специалистом.'
        else:
            level, summary = 'severe', 'Выраженные симптомы. Рекомендуется обратиться к специалисту.'
        if answers.get('ph9', 0) > 0:
            summary += ' При мыслях о самоповреждении немедленно обратитесь за помощью.'
    elif slug == 'dass21':
        score = _sum_answers(answers, questions)
        if score <= 14:
            level, summary = 'minimal', 'Низкий суммарный показатель по DASS-21.'
        elif score <= 28:
            level, summary = 'mild', 'Умеренные показатели. При сохранении — консультация специалиста.'
        elif score <= 42:
            level, summary = 'moderate', 'Повышенные показатели. Рекомендуется обсудить результаты со специалистом.'
        else:
            level, summary = 'severe', 'Высокие показатели. Рекомендуется обратиться к специалисту.'
    elif slug == 'bite':
        score = _sum_answers(answers, questions)
        if score >= 20:
            level, summary = 'elevated', 'Высокий показатель по BITE. Рекомендуется консультация специалиста.'
        elif score >= 10:
            level, summary = 'moderate', 'Умеренный показатель. Имеет смысл обсудить результаты со специалистом.'
        else:
            level, summary = 'low', 'Низкий показатель по BITE.'
    elif slug == 'bes':
        score = 0
        for i, q in enumerate(questions, 1):
            raw = answers.get(q.id, 0)
            if i in BES_REVERSED:
                score += 3 - raw
            else:
                score += raw
        if score >= 27:
            level, summary = 'elevated', 'Высокая вероятность компульсивного переедания по BES.'
        elif score >= 17:
            level, summary = 'moderate', 'Умеренные показатели по BES. Рекомендуется консультация специалиста.'
        else:
            level, summary = 'low', 'Низкие показатели по BES.'
    elif slug == 'edeq':
        score = _sum_answers(answers, questions)
        if score >= 40:
            level, summary = 'elevated', 'Повышенные показатели по EDE-Q. Рекомендуется консультация специалиста.'
        elif score >= 20:
            level, summary = 'moderate', 'Умеренные показатели. Имеет смысл обсудить результаты со специалистом.'
        else:
            level, summary = 'low', 'Относительно низкие показатели по EDE-Q.'
    elif slug == 'cia':
        score = _sum_answers(answers, questions)
        if score >= 32:
            level, summary = 'elevated', 'Выраженное влияние РПП на жизнь по CIA.'
        elif score >= 16:
            level, summary = 'moderate', 'Умеренное влияние. Рекомендуется обсудить результаты со специалистом.'
        else:
            level, summary = 'low', 'Относительно низкое влияние по CIA.'
    elif slug == 'rses':
        score = 0
        for i, q in enumerate(questions, 1):
            raw = answers.get(q.id, 0)
            if i in RSES_REVERSED:
                score += 3 - raw
            else:
                score += raw
        if score >= 25:
            level, summary = 'low', 'Высокая самооценка по RSES.'
        elif score >= 15:
            level, summary = 'moderate', 'Средний уровень самооценки по RSES.'
        else:
            level, summary = 'elevated', 'Низкая самооценка. Рекомендуется обсудить результаты со специалистом.'
    elif slug == 'psqi':
        score = _sum_answers(answers, questions)
        # пункт 7 — хороший сон (обратный)
        if 'p7' in answers:
            score = score - answers['p7'] + (3 - answers['p7'])
        if score >= 12:
            level, summary = 'elevated', 'Возможны нарушения сна. Рекомендуется обсудить с врачом.'
        elif score >= 6:
            level, summary = 'moderate', 'Умеренные проблемы со сном.'
        else:
            level, summary = 'low', 'Относительно хорошее качество сна по скринингу.'
    elif slug in ('edi3', 'bsq', 'tfeq21'):
        score = sum(
            _eat26_points(answers.get(q.id, 0), i)
            for i, q in enumerate(questions, 1)
        )
        if score >= 20:
            level, summary = 'elevated', 'Повышенные показатели. Рекомендуется консультация специалиста.'
        elif score >= 10:
            level, summary = 'moderate', 'Умеренные показатели. Имеет смысл обсудить результаты со специалистом.'
        else:
            level, summary = 'low', 'Низкие показатели по скринингу.'
    elif slug == 'bat':
        score = 0
        for i, q in enumerate(questions, 1):
            raw = answers.get(q.id, 0)
            if i in BAT_POSITIVE:
                score += 3 - raw
            else:
                score += raw
        if score >= 30:
            level, summary = 'elevated', 'Выраженное диссонированное отношение к телу. Рекомендуется консультация.'
        elif score >= 15:
            level, summary = 'moderate', 'Умеренные показатели. Имеет смысл обсудить со специалистом.'
        else:
            level, summary = 'low', 'Относительно низкие показатели по BAT.'
    else:
        score = _sum_answers(answers, questions)
        level, summary = 'unknown', 'Результат рассчитан.'

    return {
        'score': score,
        'max_score': _max_score(screening),
        'level': level,
        'summary': summary,
        'title': screening.title,
    }


def _max_score(screening: Screening) -> int:
    n = len(screening.questions)
    at = screening.answer_type
    if at == 'yes_no':
        return n
    if at == 'eat26_likert':
        return n * 3
    if at == 'bes_likert':
        return n * 3
    if at == 'edeq_frequency':
        return n * 6
    if at == 'frequency_4':
        return n * 3
    if at in ('agree_4', 'cia_likert', 'psqi_likert'):
        return n * 3
    return n * 3


def parse_answers(slug: str, post_data) -> dict[str, int]:
    screening = SCREENINGS[slug]
    lo, hi = VALID_RANGES[screening.answer_type]
    answers = {}
    for q in screening.questions:
        raw = post_data.get(q.id)
        if raw is None:
            continue
        try:
            value = int(raw)
        except (TypeError, ValueError):
            continue
        if lo <= value <= hi:
            answers[q.id] = value
    return answers


def validate_answers(slug: str, answers: dict[str, int]) -> bool:
    screening = SCREENINGS[slug]
    return len(answers) == len(screening.questions)
