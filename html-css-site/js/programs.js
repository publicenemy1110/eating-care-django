/**
 * Оверлей с меню программ питания
 */
(function () {
    const grid = document.querySelector('.programs-grid');
    const overlay = document.getElementById('program-overlay');
    const overlayTitle = document.getElementById('program-overlay-title');
    const overlayMeta = document.getElementById('program-overlay-meta');
    const overlayBody = document.getElementById('program-overlay-body');
    const closeBtn = document.getElementById('program-overlay-close');
    const backdrop = document.querySelector('.program-overlay__backdrop');

    if (!grid || !overlay || !window.PROGRAMS_DATA) {
        return;
    }

    const dataById = Object.fromEntries(
        window.PROGRAMS_DATA.map((p) => [p.id, p])
    );

    function renderMenu(program) {
        const day = program.days[0];
        if (!day) {
            return '<p class="program-overlay__empty">Меню недоступно</p>';
        }

        return day.meals.map((meal) => `
            <section class="program-overlay__meal">
                <h3 class="program-overlay__meal-title">${meal.title}</h3>
                <ul class="program-overlay__dishes">
                    ${meal.dishes.map((d) => `<li>${d}</li>`).join('')}
                </ul>
            </section>
        `).join('');
    }

    function openOverlay(id) {
        const program = dataById[id];
        if (!program) {
            return;
        }

        overlayTitle.textContent = program.title;
        overlayMeta.innerHTML = `
            <span>${program.kcal}</span>
            <span>${program.effect}</span>
            <span>${program.activity}</span>
            <span>${program.period}</span>
        `;
        overlayBody.innerHTML = `
            <p class="program-overlay__desc">${program.desc}</p>
            <p class="program-overlay__day-label">${program.days[0].name}</p>
            <div class="program-overlay__meals">${renderMenu(program)}</div>
        `;

        overlay.hidden = false;
        overlay.setAttribute('aria-hidden', 'false');
        overlay.classList.add('is-open');
        document.body.classList.add('program-overlay-open');
        closeBtn.focus();
    }

    function closeOverlay() {
        overlay.classList.remove('is-open');
        overlay.hidden = true;
        overlay.setAttribute('aria-hidden', 'true');
        document.body.classList.remove('program-overlay-open');
    }

    grid.addEventListener('click', (e) => {
        const btn = e.target.closest('[data-program-id]');
        if (btn) {
            openOverlay(btn.dataset.programId);
        }
    });

    closeBtn.addEventListener('click', closeOverlay);
    backdrop.addEventListener('click', closeOverlay);

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && overlay.classList.contains('is-open')) {
            closeOverlay();
        }
    });
})();
