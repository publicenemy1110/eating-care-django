(function () {
    var form = document.querySelector('.custom-test-form');
    if (!form) {
        return;
    }

    var totalFormsInput = form.querySelector('#id_questions-TOTAL_FORMS');
    var questionsList = form.querySelector('.custom-test-form__questions');
    var addButton = form.querySelector('#custom-test-add-question');
    var emptyTemplate = document.querySelector('#custom-question-empty-form');

    if (!totalFormsInput || !questionsList || !emptyTemplate) {
        return;
    }

    function renumberQuestions() {
        var visibleQuestions = questionsList.querySelectorAll(
            '.custom-test-form__question:not(.is-deleted)'
        );
        visibleQuestions.forEach(function (item, index) {
            var label = item.querySelector('.custom-test-form__question-num');
            if (label) {
                label.textContent = 'Вопрос ' + (index + 1);
            }
        });
    }

    function addQuestion() {
        var formIndex = parseInt(totalFormsInput.value, 10);
        var html = emptyTemplate.innerHTML.replace(/__prefix__/g, String(formIndex));
        var wrapper = document.createElement('div');
        wrapper.innerHTML = html.trim();
        var newItem = wrapper.firstElementChild;
        questionsList.appendChild(newItem);
        totalFormsInput.value = String(formIndex + 1);
        renumberQuestions();

        var textarea = newItem.querySelector('textarea');
        if (textarea) {
            textarea.focus();
        }
    }

    questionsList.addEventListener('change', function (event) {
        var target = event.target;
        if (!(target instanceof HTMLInputElement) || !target.name.endsWith('-DELETE')) {
            return;
        }

        var item = target.closest('.custom-test-form__question');
        if (!item) {
            return;
        }

        item.classList.toggle('is-deleted', target.checked);
        renumberQuestions();
    });

    questionsList.querySelectorAll('.custom-test-form__question').forEach(function (item) {
        var deleteInput = item.querySelector('input[type="checkbox"][name$="-DELETE"]');
        if (deleteInput && deleteInput.checked) {
            item.classList.add('is-deleted');
        }
    });

    if (addButton) {
        addButton.addEventListener('click', addQuestion);
    }

    renumberQuestions();
})();
