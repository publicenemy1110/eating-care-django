from django.contrib import messages
from django.db import transaction
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from accounts.models import PsychologistModerationStatus

from .custom_tests import (
    custom_test_to_screening,
    generate_unique_slug,
    parse_custom_answers,
    score_custom_test,
    validate_custom_answers,
)
from .decorators import approved_psychologist_required
from .forms import CustomQuestionFormSet, CustomTestForm
from .models import CustomTest
from .screenings import DISCLAIMER
from .screenings_catalog import TEST_CATEGORIES


def _page(request, template_name, active_page, extra_context=None):
    context = {'active_page': active_page}
    if extra_context:
        context.update(extra_context)
    return render(request, template_name, context)


def index(request):
    return _page(request, 'pages/index.html', '')


def rpp(request):
    return _page(request, 'pages/rpp.html', 'rpp')


def _published_custom_tests_queryset():
    return CustomTest.objects.filter(
        is_published=True,
        author__psychologist_profile__moderation_status=PsychologistModerationStatus.APPROVED,
    ).select_related('author', 'author__psychologist_profile').prefetch_related('questions')


def tests(request):
    custom_tests = _published_custom_tests_queryset()
    can_create_custom_tests = (
        request.user.is_authenticated and request.user.is_approved_psychologist
    )
    my_custom_tests = []
    if can_create_custom_tests:
        my_custom_tests = (
            CustomTest.objects.filter(author=request.user)
            .prefetch_related('questions')
        )
        custom_tests = custom_tests.exclude(author=request.user)

    return _page(
        request,
        'pages/tests.html',
        'tests',
        {
            'test_categories': TEST_CATEGORIES,
            'custom_tests': custom_tests,
            'my_custom_tests': my_custom_tests,
            'can_create_custom_tests': can_create_custom_tests,
        },
    )


def parents(request):
    return _page(request, 'pages/parents.html', 'parents')


def programs(request):
    return _page(request, 'pages/programs.html', 'programs')


def about(request):
    return _page(request, 'pages/about.html', 'about')


def _get_owned_custom_test(user, slug):
    return get_object_or_404(CustomTest, slug=slug, author=user)


def _save_custom_test(request, test_instance, *, is_new):
    form = CustomTestForm(request.POST, instance=test_instance)
    formset = CustomQuestionFormSet(request.POST, instance=test_instance)
    if not (form.is_valid() and formset.is_valid()):
        return None, form, formset

    with transaction.atomic():
        test = form.save(commit=False)
        if is_new:
            test.author = request.user
            test.slug = generate_unique_slug(test.title)
        test.save()
        formset.instance = test
        questions = formset.save(commit=False)
        for index, question in enumerate(questions):
            question.order = index
            question.save()
        for question in formset.deleted_objects:
            question.delete()

    return test, form, formset


def _render_custom_test_form(request, test_instance, *, is_edit):
    form = CustomTestForm(instance=test_instance)
    formset = CustomQuestionFormSet(instance=test_instance)
    return _page(
        request,
        'pages/custom_test_form.html',
        'tests',
        {
            'form': form,
            'formset': formset,
            'is_edit': is_edit,
            'test': test_instance if is_edit else None,
        },
    )


@approved_psychologist_required
def custom_test_create(request):
    test_instance = CustomTest(author=request.user)

    if request.method == 'POST':
        test, form, formset = _save_custom_test(request, test_instance, is_new=True)
        if test:
            messages.success(request, 'Тест успешно создан.')
            return redirect('pages:tests')
        return _page(
            request,
            'pages/custom_test_form.html',
            'tests',
            {
                'form': form,
                'formset': formset,
                'is_edit': False,
                'test': None,
            },
        )

    return _render_custom_test_form(request, test_instance, is_edit=False)


@approved_psychologist_required
def custom_test_edit(request, slug):
    test = _get_owned_custom_test(request.user, slug)

    if request.method == 'POST':
        saved_test, form, formset = _save_custom_test(request, test, is_new=False)
        if saved_test:
            messages.success(request, 'Тест успешно обновлён.')
            return redirect('pages:tests')
        return _page(
            request,
            'pages/custom_test_form.html',
            'tests',
            {
                'form': form,
                'formset': formset,
                'is_edit': True,
                'test': test,
            },
        )

    return _render_custom_test_form(request, test, is_edit=True)


@approved_psychologist_required
@require_POST
def custom_test_delete(request, slug):
    test = _get_owned_custom_test(request.user, slug)
    title = test.title
    test.delete()
    messages.success(request, f'Тест «{title}» удалён.')
    return redirect('pages:tests')


def _get_public_custom_test(slug):
    return get_object_or_404(
        CustomTest.objects.select_related('author', 'author__psychologist_profile').prefetch_related('questions'),
        slug=slug,
        is_published=True,
        author__psychologist_profile__moderation_status=PsychologistModerationStatus.APPROVED,
    )


def custom_test_take(request, slug):
    test = _get_public_custom_test(slug)
    screening = custom_test_to_screening(test)

    if request.method == 'POST':
        answers = parse_custom_answers(test, request.POST)
        if not validate_custom_answers(test, answers):
            return render(
                request,
                'pages/screening_take.html',
                {
                    'active_page': 'tests',
                    'screening': screening,
                    'disclaimer': DISCLAIMER,
                    'form_error': 'Пожалуйста, ответьте на все вопросы.',
                },
            )
        result = score_custom_test(test, answers)
        request.session[f'custom_test_result_{slug}'] = result
        return redirect('pages:custom_test_result', slug=slug)

    return render(
        request,
        'pages/screening_take.html',
        {
            'active_page': 'tests',
            'screening': screening,
            'disclaimer': DISCLAIMER,
        },
    )


def custom_test_result(request, slug):
    test = _get_public_custom_test(slug)
    result = request.session.pop(f'custom_test_result_{slug}', None)
    if not result:
        return redirect('pages:custom_test_take', slug=slug)

    return render(
        request,
        'pages/screening_result.html',
        {
            'active_page': 'tests',
            'screening': custom_test_to_screening(test),
            'result': result,
            'disclaimer': DISCLAIMER,
            'retake_url': reverse('pages:custom_test_take', kwargs={'slug': slug}),
            'tests_url': reverse('pages:tests'),
        },
    )


def screening_take(request, slug):
    from .screenings import get_screening, parse_answers, score_screening, validate_answers

    screening = get_screening(slug)
    if not screening:
        raise Http404('Тест не найден')

    if request.method == 'POST':
        answers = parse_answers(slug, request.POST)
        if not validate_answers(slug, answers):
            return render(
                request,
                'pages/screening_take.html',
                {
                    'active_page': 'tests',
                    'screening': screening,
                    'disclaimer': DISCLAIMER,
                    'form_error': 'Пожалуйста, ответьте на все вопросы.',
                },
            )
        result = score_screening(slug, answers)
        request.session[f'screening_result_{slug}'] = result
        return redirect('pages:screening_result', slug=slug)

    return render(
        request,
        'pages/screening_take.html',
        {
            'active_page': 'tests',
            'screening': screening,
            'disclaimer': DISCLAIMER,
        },
    )


def screening_result(request, slug):
    from .screenings import get_screening

    screening = get_screening(slug)
    if not screening:
        raise Http404('Тест не найден')

    result = request.session.pop(f'screening_result_{slug}', None)
    if not result:
        return redirect('pages:screening_take', slug=slug)

    return render(
        request,
        'pages/screening_result.html',
        {
            'active_page': 'tests',
            'screening': screening,
            'result': result,
            'disclaimer': DISCLAIMER,
            'retake_url': reverse('pages:screening_take', kwargs={'slug': slug}),
            'tests_url': reverse('pages:tests'),
        },
    )
