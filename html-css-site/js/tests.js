/**
 * Фильтр категорий на странице tests.html
 */
(function () {
    const filterBtn = document.getElementById('tests-filter-btn');
    const filterMenu = document.getElementById('tests-filter-menu');
    const categoryLabel = document.getElementById('tests-category-label');
    const filterOptions = document.querySelectorAll('.tests-filter__option');
    const panels = document.querySelectorAll('.tests-panel');

    if (!filterBtn || !filterMenu || !filterOptions.length || !panels.length) {
        return;
    }

    function setMenuOpen(isOpen) {
        filterBtn.classList.toggle('is-open', isOpen);
        filterBtn.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
        filterMenu.hidden = !isOpen;
    }

    function activateCategory(tabId, label) {
        filterOptions.forEach((option) => {
            const isActive = option.dataset.tab === tabId;
            option.classList.toggle('is-active', isActive);
            option.setAttribute('aria-selected', isActive ? 'true' : 'false');
        });

        panels.forEach((panel) => {
            const isActive = panel.dataset.panel === tabId;
            panel.classList.toggle('is-active', isActive);
            panel.hidden = !isActive;
        });

        if (categoryLabel && label) {
            categoryLabel.textContent = label;
        }

        setMenuOpen(false);
    }

    filterBtn.addEventListener('click', (event) => {
        event.stopPropagation();
        setMenuOpen(filterMenu.hidden);
    });

    filterOptions.forEach((option) => {
        option.addEventListener('click', () => {
            activateCategory(option.dataset.tab, option.dataset.label);
        });
    });

    document.addEventListener('click', (event) => {
        if (!filterMenu.hidden && !event.target.closest('.tests-filter')) {
            setMenuOpen(false);
        }
    });

    document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape' && !filterMenu.hidden) {
            setMenuOpen(false);
            filterBtn.focus();
        }
    });
})();
