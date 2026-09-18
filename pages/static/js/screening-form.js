(function () {
    function syncSelected(group) {
        var name = group.getAttribute('name');
        if (!name) return;
        var radios = document.querySelectorAll('input.screening-form__input[name="' + name + '"]');
        radios.forEach(function (radio) {
            var label = radio.closest('.screening-form__pill, .screening-form__choice');
            if (label) {
                label.classList.toggle('is-selected', radio.checked);
            }
        });
    }

    document.querySelectorAll('.screening-form__input').forEach(function (input) {
        syncSelected(input);
        input.addEventListener('change', function () {
            syncSelected(input);
        });
    });
})();
