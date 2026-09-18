from django.conf import settings
from django.db import models


class CustomTest(models.Model):
    ANSWER_TYPE_CHOICES = (
        ('yes_no', 'Да / Нет'),
        ('frequency_4', 'Частота (4 варианта)'),
        ('agree_4', 'Согласие (4 варианта)'),
        ('cia_likert', 'Интенсивность (4 варианта)'),
        ('bes_likert', 'Дискомфорт (4 варианта)'),
        ('psqi_likert', 'Частота за месяц (4 варианта)'),
    )

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='custom_tests',
        verbose_name='Автор',
    )
    title = models.CharField('Название', max_length=255)
    slug = models.SlugField('URL-идентификатор', max_length=120, unique=True)
    short_description = models.TextField('Краткое описание', blank=True)
    instructions = models.TextField('Инструкция', blank=True)
    answer_type = models.CharField(
        'Тип ответов',
        max_length=32,
        choices=ANSWER_TYPE_CHOICES,
        default='yes_no',
    )
    is_published = models.BooleanField('Опубликован', default=True)
    created_at = models.DateTimeField('Создан', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлён', auto_now=True)

    class Meta:
        verbose_name = 'Собственный тест'
        verbose_name_plural = 'Собственные тесты'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class CustomQuestion(models.Model):
    test = models.ForeignKey(
        CustomTest,
        on_delete=models.CASCADE,
        related_name='questions',
        verbose_name='Тест',
    )
    order = models.PositiveSmallIntegerField('Порядок', default=0)
    text = models.TextField('Текст вопроса')

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'
        ordering = ['order', 'pk']

    def __str__(self):
        return self.text[:80]
