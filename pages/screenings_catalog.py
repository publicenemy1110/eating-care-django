"""Каталог тестов для страницы /tests/ — все пункты ведут на рабочие опросники."""

TEST_CATEGORIES = (
    {
        'id': 'diagnostic',
        'label': 'По цели диагностики',
        'items': (
            {'name': 'EAT-26 (Eating Attitudes Test, 26 пунктов)', 'slug': 'eat26'},
            {'name': 'SCOFF Questionnaire', 'slug': 'scoff'},
            {'name': 'EDE-Q (Eating Disorder Examination Questionnaire)', 'slug': 'edeq'},
            {'name': 'BITE (Bulimic Investigatory Test, Edinburgh)', 'slug': 'bite'},
            {'name': 'BES (Binge Eating Scale)', 'slug': 'bes'},
            {'name': 'CIA (Clinical Impairment Assessment)', 'slug': 'cia'},
        ),
    },
    {
        'id': 'model',
        'label': 'По теоретической модели',
        'items': (
            {'name': 'EDI-3 (Eating Disorder Inventory-3)', 'slug': 'edi3'},
            {'name': 'BSQ (Body Shape Questionnaire)', 'slug': 'bsq'},
            {'name': 'TFEQ-R21 (Three-Factor Eating Questionnaire)', 'slug': 'tfeq21'},
            {'name': 'BAT (Body Attitudes Test)', 'slug': 'bat'},
            {'name': 'DASS-21 (шкалы стресса, тревоги и депрессии)', 'slug': 'dass21'},
        ),
    },
    {
        'id': 'disorder',
        'label': 'По типу расстройства',
        'items': (
            {'name': 'Анорексия — EAT-26', 'slug': 'eat26'},
            {'name': 'Булимия — BITE', 'slug': 'bite'},
            {'name': 'Компульсивное переедание — BES', 'slug': 'bes'},
            {'name': 'ОРЭ (расстройство переедания) — EDE-Q', 'slug': 'edeq'},
            {'name': 'Расстройство пищевого поведения — SCOFF', 'slug': 'scoff'},
        ),
    },
    {
        'id': 'extra',
        'label': 'Дополнительные тесты',
        'items': (
            {'name': 'PHQ-9 (симптомы депрессии)', 'slug': 'phq9'},
            {'name': 'GAD-7 (уровень тревожности)', 'slug': 'gad7'},
            {'name': 'RSES (шкала самооценки Розенберга)', 'slug': 'rses'},
            {'name': 'PSQI (качество сна)', 'slug': 'psqi'},
        ),
    },
)
