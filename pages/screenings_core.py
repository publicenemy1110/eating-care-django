"""Базовые типы и шкалы ответов для скринингов."""

from dataclasses import dataclass
from typing import Literal

AnswerType = Literal[
    'yes_no',
    'frequency_4',
    'eat26_likert',
    'bes_likert',
    'agree_4',
    'cia_likert',
    'edeq_frequency',
    'psqi_likert',
]

FREQUENCY_CHOICES = (
    (0, 'Совсем не беспокоило'),
    (1, 'Несколько дней'),
    (2, 'Более половины дней'),
    (3, 'Почти каждый день'),
)

YES_NO_CHOICES = (
    (0, 'Нет'),
    (1, 'Да'),
)

CHOICE_SETS: dict[AnswerType, tuple[tuple[int, str], ...]] = {
    'yes_no': YES_NO_CHOICES,
    'frequency_4': FREQUENCY_CHOICES,
    'eat26_likert': (
        (0, 'Никогда'),
        (1, 'Редко'),
        (2, 'Иногда'),
        (3, 'Часто'),
        (4, 'Обычно'),
        (5, 'Всегда'),
    ),
    'bes_likert': (
        (0, 'Нет дискомфорта'),
        (1, 'Лёгкий дискомфорт'),
        (2, 'Умеренный дискомфорт'),
        (3, 'Серьёзный или крайний дискомфорт'),
    ),
    'agree_4': (
        (0, 'Полностью не согласен(на)'),
        (1, 'Не согласен(на)'),
        (2, 'Согласен(на)'),
        (3, 'Полностью согласен(на)'),
    ),
    'cia_likert': (
        (0, 'Совсем не'),
        (1, 'Немного'),
        (2, 'Умеренно'),
        (3, 'Сильно'),
    ),
    'edeq_frequency': (
        (0, 'Ни одного дня'),
        (1, '1–5 дней'),
        (2, '6–12 дней'),
        (3, '13–15 дней'),
        (4, '16–22 дня'),
        (5, '23–27 дней'),
        (6, 'Каждый день'),
    ),
    'psqi_likert': (
        (0, 'Никогда за последний месяц'),
        (1, 'Реже одного раза в неделю'),
        (2, '1–2 раза в неделю'),
        (3, '3 и более раз в неделю'),
    ),
}

# EAT-26: сырой ответ 0–5 → баллы 0–3
EAT26_SCORE_MAP = {0: 0, 1: 0, 2: 0, 3: 1, 4: 2, 5: 3}

VALID_RANGES: dict[AnswerType, tuple[int, int]] = {
    'yes_no': (0, 1),
    'frequency_4': (0, 3),
    'eat26_likert': (0, 5),
    'bes_likert': (0, 3),
    'agree_4': (0, 3),
    'cia_likert': (0, 3),
    'edeq_frequency': (0, 6),
    'psqi_likert': (0, 3),
}


@dataclass(frozen=True)
class Question:
    id: str
    text: str


@dataclass(frozen=True)
class Screening:
    slug: str
    title: str
    short_description: str
    answer_type: AnswerType
    questions: tuple[Question, ...]
    instructions: str = ''

    @property
    def question_count(self) -> int:
        return len(self.questions)

    @property
    def answer_choices(self) -> tuple[tuple[int, str], ...]:
        return CHOICE_SETS[self.answer_type]

    @property
    def max_raw_value(self) -> int:
        return VALID_RANGES[self.answer_type][1]
