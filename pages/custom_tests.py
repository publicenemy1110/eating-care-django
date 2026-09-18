"""Утилиты для собственных тестов психологов."""

from django.utils.text import slugify

from .models import CustomTest
from .screenings_core import Question, Screening, VALID_RANGES


def generate_unique_slug(title: str) -> str:
    base = slugify(title) or 'test'
    slug = base
    counter = 1
    while CustomTest.objects.filter(slug=slug).exists():
        slug = f'{base}-{counter}'
        counter += 1
    return slug


def custom_test_to_screening(test: CustomTest) -> Screening:
    questions = tuple(
        Question(id=f'q{question.pk}', text=question.text)
        for question in test.questions.all()
    )
    return Screening(
        slug=test.slug,
        title=test.title,
        short_description=test.short_description,
        answer_type=test.answer_type,
        questions=questions,
        instructions=test.instructions,
    )


def parse_custom_answers(test: CustomTest, post_data) -> dict[str, int]:
    screening = custom_test_to_screening(test)
    lo, hi = VALID_RANGES[screening.answer_type]
    answers = {}
    for question in screening.questions:
        raw = post_data.get(question.id)
        if raw is None:
            continue
        try:
            value = int(raw)
        except (TypeError, ValueError):
            continue
        if lo <= value <= hi:
            answers[question.id] = value
    return answers


def validate_custom_answers(test: CustomTest, answers: dict[str, int]) -> bool:
    screening = custom_test_to_screening(test)
    return len(answers) == len(screening.questions)


def score_custom_test(test: CustomTest, answers: dict[str, int]) -> dict:
    screening = custom_test_to_screening(test)
    score = sum(answers.get(question.id, 0) for question in screening.questions)
    max_score = len(screening.questions) * screening.max_raw_value
    return {
        'score': score,
        'max_score': max_score,
        'level': 'custom',
        'summary': (
            'Результаты собственного опросника рассчитаны как сумма баллов по ответам. '
            'Интерпретацию предоставляет автор методики.'
        ),
        'title': test.title,
    }
