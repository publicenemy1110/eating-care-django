from django.test import Client, TestCase
from django.urls import reverse

from accounts.models import PsychologistModerationStatus, PsychologistProfile, User, UserRole

from .models import CustomTest
from .screenings import SCREENINGS, get_screening, parse_answers, score_screening, validate_answers
from .screenings_catalog import TEST_CATEGORIES


class PageViewTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_index_returns_200(self):
        response = self.client.get(reverse('pages:index'))
        self.assertEqual(response.status_code, 200)

    def test_tests_page_lists_all_catalog_slugs(self):
        response = self.client.get(reverse('pages:tests'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'tests-filter-btn')
        for category in TEST_CATEGORIES:
            for item in category['items']:
                self.assertContains(
                    response,
                    reverse('pages:screening_take', kwargs={'slug': item['slug']}),
                )


class ScreeningCatalogTests(TestCase):
    def test_every_catalog_slug_has_screening(self):
        slugs = {item['slug'] for cat in TEST_CATEGORIES for item in cat['items']}
        self.assertEqual(slugs, set(SCREENINGS.keys()))

    def test_all_screenings_have_questions(self):
        for slug, screening in SCREENINGS.items():
            self.assertGreater(screening.question_count, 0, slug)


class ScreeningViewTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_unknown_screening_returns_404(self):
        response = self.client.get(
            reverse('pages:screening_take', kwargs={'slug': 'unknown'}),
        )
        self.assertEqual(response.status_code, 404)

    def test_eat26_take_get(self):
        response = self.client.get(
            reverse('pages:screening_take', kwargs={'slug': 'eat26'}),
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'EAT-26')
        self.assertEqual(response.content.count(b'screening-form__item'), 26)

    def test_scoff_full_flow(self):
        screening = SCREENINGS['scoff']
        post_data = {q.id: '0' for q in screening.questions}
        post_data['s1'] = '1'
        post_data['s2'] = '1'
        url = reverse('pages:screening_take', kwargs={'slug': 'scoff'})
        response = self.client.post(url, post_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Суммарный балл')

    def test_bite_has_33_questions(self):
        response = self.client.get(
            reverse('pages:screening_take', kwargs={'slug': 'bite'}),
        )
        self.assertEqual(response.content.count(b'screening-form__item'), 33)


class ScreeningLogicTests(TestCase):
    def test_scoff_elevated(self):
        screening = SCREENINGS['scoff']
        answers = {q.id: 1 for q in screening.questions}
        result = score_screening('scoff', answers)
        self.assertEqual(result['level'], 'elevated')

    def test_eat26_scoring(self):
        screening = SCREENINGS['eat26']
        answers = {q.id: 5 for q in screening.questions}
        result = score_screening('eat26', answers)
        self.assertGreaterEqual(result['score'], 20)

    def test_validate_requires_all(self):
        screening = SCREENINGS['gad7']
        self.assertFalse(validate_answers('gad7', {'g1': 0}))

    def test_parse_rejects_out_of_range(self):
        class FakePost:
            def get(self, key, default=None):
                return {'g1': '9'}.get(key, default)

        self.assertEqual(parse_answers('gad7', FakePost()), {})


class CustomTestAccessTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.approved_psychologist = User.objects.create_user(
            username='approved_psych',
            password='testpass123456',
            role=UserRole.PSYCHOLOGIST,
        )
        approved_profile = self.approved_psychologist.psychologist_profile
        approved_profile.moderation_status = PsychologistModerationStatus.APPROVED
        approved_profile.save(update_fields=['moderation_status'])
        self.pending_psychologist = User.objects.create_user(
            username='pending_psych',
            password='testpass123456',
            role=UserRole.PSYCHOLOGIST,
        )
        pending_profile = self.pending_psychologist.psychologist_profile
        pending_profile.moderation_status = PsychologistModerationStatus.PENDING
        pending_profile.save(update_fields=['moderation_status'])
        self.patient = User.objects.create_user(
            username='patient_user',
            password='testpass123456',
            role=UserRole.PATIENT,
        )

    def test_anonymous_user_cannot_open_create_form(self):
        response = self.client.get(reverse('pages:custom_test_create'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_patient_cannot_create_custom_test(self):
        self.client.login(username='patient_user', password='testpass123456')
        response = self.client.get(reverse('pages:custom_test_create'))
        self.assertRedirects(response, reverse('pages:tests'))

    def test_pending_psychologist_cannot_create_custom_test(self):
        self.client.login(username='pending_psych', password='testpass123456')
        response = self.client.get(reverse('pages:custom_test_create'))
        self.assertRedirects(response, reverse('pages:tests'))

    def test_approved_psychologist_can_create_custom_test(self):
        self.client.login(username='approved_psych', password='testpass123456')
        response = self.client.post(reverse('pages:custom_test_create'), {
            'title': 'Мой опросник',
            'short_description': 'Описание',
            'instructions': '',
            'answer_type': 'yes_no',
            'is_published': 'on',
            'questions-TOTAL_FORMS': '1',
            'questions-INITIAL_FORMS': '0',
            'questions-MIN_NUM_FORMS': '1',
            'questions-MAX_NUM_FORMS': '1000',
            'questions-0-text': 'Чувствуете ли вы тревогу?',
            'questions-0-id': '',
            'questions-0-DELETE': '',
        })
        self.assertRedirects(response, reverse('pages:tests'))
        test = CustomTest.objects.get(title='Мой опросник')
        self.assertEqual(test.author, self.approved_psychologist)
        self.assertEqual(test.questions.count(), 1)

    def test_approved_psychologist_can_create_custom_test_with_many_questions(self):
        self.client.login(username='approved_psych', password='testpass123456')
        post_data = {
            'title': 'Большой опросник',
            'short_description': 'Описание',
            'instructions': '',
            'answer_type': 'yes_no',
            'is_published': 'on',
            'questions-TOTAL_FORMS': '6',
            'questions-INITIAL_FORMS': '0',
            'questions-MIN_NUM_FORMS': '1',
            'questions-MAX_NUM_FORMS': '1000',
        }
        for index in range(6):
            post_data[f'questions-{index}-text'] = f'Вопрос {index + 1}'
            post_data[f'questions-{index}-id'] = ''
            post_data[f'questions-{index}-DELETE'] = ''

        response = self.client.post(reverse('pages:custom_test_create'), post_data)
        self.assertRedirects(response, reverse('pages:tests'))
        test = CustomTest.objects.get(title='Большой опросник')
        self.assertEqual(test.questions.count(), 6)

    def test_published_custom_test_is_available_to_take(self):
        test = CustomTest.objects.create(
            author=self.approved_psychologist,
            title='Публичный тест',
            slug='public-test',
            answer_type='yes_no',
            is_published=True,
        )
        question = test.questions.create(order=0, text='Вопрос 1')
        response = self.client.get(reverse('pages:custom_test_take', kwargs={'slug': test.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Публичный тест')

        post_data = {f'q{question.pk}': '1'}
        response = self.client.post(reverse('pages:custom_test_take', kwargs={'slug': test.slug}), post_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Суммарный балл')

    def test_unpublished_custom_test_is_hidden(self):
        test = CustomTest.objects.create(
            author=self.approved_psychologist,
            title='Черновик',
            slug='draft-test',
            answer_type='yes_no',
            is_published=False,
        )
        test.questions.create(order=0, text='Вопрос 1')
        response = self.client.get(reverse('pages:custom_test_take', kwargs={'slug': test.slug}))
        self.assertEqual(response.status_code, 404)

    def _create_test_with_question(self, title='Тест для редактирования', slug='edit-test'):
        test = CustomTest.objects.create(
            author=self.approved_psychologist,
            title=title,
            slug=slug,
            answer_type='yes_no',
            is_published=True,
        )
        question = test.questions.create(order=0, text='Исходный вопрос')
        return test, question

    def test_approved_psychologist_can_edit_own_test(self):
        test, question = self._create_test_with_question()
        self.client.login(username='approved_psych', password='testpass123456')
        response = self.client.get(reverse('pages:custom_test_edit', kwargs={'slug': test.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Редактировать тест')

        response = self.client.post(reverse('pages:custom_test_edit', kwargs={'slug': test.slug}), {
            'title': 'Обновлённый опросник',
            'short_description': 'Новое описание',
            'instructions': 'Инструкция',
            'answer_type': 'yes_no',
            'is_published': 'on',
            'questions-TOTAL_FORMS': '2',
            'questions-INITIAL_FORMS': '1',
            'questions-MIN_NUM_FORMS': '1',
            'questions-MAX_NUM_FORMS': '1000',
            'questions-0-id': str(question.pk),
            'questions-0-text': 'Изменённый вопрос',
            'questions-0-DELETE': '',
            'questions-1-id': '',
            'questions-1-text': 'Новый вопрос',
            'questions-1-DELETE': '',
        })
        self.assertRedirects(response, reverse('pages:tests'))
        test.refresh_from_db()
        self.assertEqual(test.title, 'Обновлённый опросник')
        self.assertEqual(test.slug, 'edit-test')
        self.assertEqual(test.questions.count(), 2)
        self.assertEqual(test.questions.first().text, 'Изменённый вопрос')

    def test_approved_psychologist_can_delete_question_via_edit(self):
        test, question = self._create_test_with_question(slug='delete-question-test')
        extra_question = test.questions.create(order=1, text='Второй вопрос')
        self.client.login(username='approved_psych', password='testpass123456')
        response = self.client.post(reverse('pages:custom_test_edit', kwargs={'slug': test.slug}), {
            'title': test.title,
            'short_description': '',
            'instructions': '',
            'answer_type': 'yes_no',
            'is_published': 'on',
            'questions-TOTAL_FORMS': '2',
            'questions-INITIAL_FORMS': '2',
            'questions-MIN_NUM_FORMS': '1',
            'questions-MAX_NUM_FORMS': '1000',
            'questions-0-id': str(question.pk),
            'questions-0-text': question.text,
            'questions-0-DELETE': 'on',
            'questions-1-id': str(extra_question.pk),
            'questions-1-text': extra_question.text,
            'questions-1-DELETE': '',
        })
        self.assertRedirects(response, reverse('pages:tests'))
        test.refresh_from_db()
        self.assertEqual(test.questions.count(), 1)
        self.assertEqual(test.questions.first().text, 'Второй вопрос')

    def test_approved_psychologist_can_delete_own_test(self):
        test, _ = self._create_test_with_question(slug='delete-test')
        self.client.login(username='approved_psych', password='testpass123456')
        response = self.client.post(reverse('pages:custom_test_delete', kwargs={'slug': test.slug}))
        self.assertRedirects(response, reverse('pages:tests'))
        self.assertFalse(CustomTest.objects.filter(pk=test.pk).exists())

    def test_patient_cannot_edit_custom_test(self):
        test, _ = self._create_test_with_question(slug='patient-edit-test')
        self.client.login(username='patient_user', password='testpass123456')
        response = self.client.get(reverse('pages:custom_test_edit', kwargs={'slug': test.slug}))
        self.assertRedirects(response, reverse('pages:tests'))

    def test_pending_psychologist_cannot_edit_custom_test(self):
        test, _ = self._create_test_with_question(slug='pending-edit-test')
        self.client.login(username='pending_psych', password='testpass123456')
        response = self.client.get(reverse('pages:custom_test_edit', kwargs={'slug': test.slug}))
        self.assertRedirects(response, reverse('pages:tests'))

    def test_approved_psychologist_cannot_edit_foreign_test(self):
        test, _ = self._create_test_with_question(slug='foreign-edit-test')
        other_psychologist = User.objects.create_user(
            username='other_psych',
            password='testpass123456',
            role=UserRole.PSYCHOLOGIST,
        )
        other_profile = other_psychologist.psychologist_profile
        other_profile.moderation_status = PsychologistModerationStatus.APPROVED
        other_profile.save(update_fields=['moderation_status'])
        self.client.login(username='other_psych', password='testpass123456')
        response = self.client.get(reverse('pages:custom_test_edit', kwargs={'slug': test.slug}))
        self.assertEqual(response.status_code, 404)

    def test_delete_requires_post(self):
        test, _ = self._create_test_with_question(slug='delete-get-test')
        self.client.login(username='approved_psych', password='testpass123456')
        response = self.client.get(reverse('pages:custom_test_delete', kwargs={'slug': test.slug}))
        self.assertEqual(response.status_code, 405)
        self.assertTrue(CustomTest.objects.filter(pk=test.pk).exists())
