(function () {
    const form = document.getElementById('bmi-form');
    if (!form) return;

    const weightInput = document.getElementById('bmi-weight');
    const heightInput = document.getElementById('bmi-height');
    const resultBlock = document.getElementById('bmi-result');
    const valueEl = document.getElementById('bmi-value');
    const categoryEl = document.getElementById('bmi-category');

    function getCategory(bmi) {
        if (bmi < 16) {
            return {
                text: 'Выраженный дефицит массы тела. Низкий ИМТ может указывать на тяжёлое течение РПП — обратитесь к специалисту.',
                modifier: 'severe',
            };
        }
        if (bmi < 17) {
            return {
                text: 'Недостаточная масса тела. Рекомендуется консультация врача или психолога.',
                modifier: 'low',
            };
        }
        if (bmi < 18.5) {
            return {
                text: 'Недостаточная масса тела (ниже нормы). Стоит обсудить питание и самочувствие со специалистом.',
                modifier: 'low',
            };
        }
        if (bmi < 25) {
            return {
                text: 'Нормальная масса тела. ИМТ — лишь один из показателей; для диагноза нужна оценка специалиста.',
                modifier: 'normal',
            };
        }
        if (bmi < 30) {
            return {
                text: 'Избыточная масса тела. При нарушениях пищевого поведения также важны другие симптомы, не только вес.',
                modifier: 'high',
            };
        }
        return {
            text: 'Ожирение по показателю ИМТ. Точный диагноз и план помощи может определить только врач.',
            modifier: 'high',
        };
    }

    form.addEventListener('submit', (e) => {
        e.preventDefault();

        const weight = parseFloat(weightInput.value, 10);
        const heightCm = parseFloat(heightInput.value, 10);

        if (!weight || !heightCm || weight <= 0 || heightCm <= 0) {
            return;
        }

        const heightM = heightCm / 100;
        const bmi = weight / (heightM * heightM);
        const rounded = Math.round(bmi * 10) / 10;
        const category = getCategory(rounded);

        valueEl.textContent = String(rounded).replace('.', ',');
        categoryEl.textContent = category.text;
        categoryEl.className = 'rpp-bmi__result-category rpp-bmi__result-category--' + category.modifier;

        resultBlock.hidden = false;
    });
})();
