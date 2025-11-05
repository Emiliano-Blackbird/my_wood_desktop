// Quick Pomodoro per-container + active timer + audio alert
(function () {
  function find(parent, selector) { return parent.querySelector(selector); }
  function formatTime(s) {
    const h = Math.floor(s / 3600), m = Math.floor((s % 3600) / 60), sec = s % 60;
    const pad = n => String(n).padStart(2, '0');
    if (h) return `${pad(h)}:${pad(m)}:${pad(sec)}`;
    return `${pad(m)}:${pad(sec)}`;
  }

  // Active session timer
  (function initActiveTimer() {
    const el = document.getElementById('activeTimer');
    if (!el) return;
    const startIso = el.dataset.start;
    let startTs = Date.parse(startIso);
    if (isNaN(startTs)) startTs = Date.now();
    function update() {
      const secs = Math.max(0, Math.floor((Date.now() - startTs) / 1000));
      el.textContent = formatTime(secs);
    }
    update();
    setInterval(update, 1000);
  })();

  // Pomodoro controller for each .quick-pomodoro
  function initPomodoroContainer(container) {
    const inputWork = find(container, '.qp-work');
    const inputBreak = find(container, '.qp-break');
    const inputRounds = find(container, '.qp-rounds');
    const btnStart = find(container, '.qp-start');
    const btnStop = find(container, '.qp-stop');
    const status = find(container, '.qp-status');
    const smallDisplay = document.getElementById('smallPomDisplay'); // under main timer
    const audio = document.getElementById('pomSound');

    let interval = null;
    let state = { remaining: 0, mode: 'idle', round: 1, totalRounds: 1, work: 25 * 60, br: 5 * 60 };

    function updateUI() {
      if (!status) return;
      if (state.mode === 'idle') {
        status.textContent = 'Estado: listo';
        if (smallDisplay) smallDisplay.textContent = 'Pomodoro: listo';
      } else {
        const text = `${state.mode === 'work' ? 'Trabajo' : 'Descanso'} ${state.round}/${state.totalRounds} — ${formatTime(state.remaining)}`;
        status.textContent = text;
        if (smallDisplay) smallDisplay.textContent = `Pomodoro: ${text}`;
      }
    }

    function tick() {
      state.remaining -= 1;
      if (state.remaining <= 0) {
        // play alert
        try { audio && audio.play().catch(()=>{}); } catch (e) {}
        if (state.mode === 'work') {
          state.mode = 'break';
          state.remaining = state.br;
        } else {
          state.round += 1;
          if (state.round > state.totalRounds) {
            stopPom();
            status.textContent = 'Pomodoro completado';
            if (smallDisplay) smallDisplay.textContent = 'Pomodoro: completado';
            return;
          }
          state.mode = 'work';
          state.remaining = state.work;
        }
      }
      updateUI();
    }

    function startPom() {
      const work = parseInt(inputWork?.value, 10) || 25;
      const br = parseInt(inputBreak?.value, 10) || 5;
      const rounds = parseInt(inputRounds?.value, 10) || 4;
      state.work = work * 60;
      state.br = br * 60;
      state.totalRounds = rounds;
      state.round = 1;
      state.mode = 'work';
      state.remaining = state.work;
      btnStart.classList.add('d-none');
      btnStop.classList.remove('d-none');
      updateUI();
      if (interval) clearInterval(interval);
      interval = setInterval(tick, 1000);
      // user gesture already (click) so audio.play allowed later
    }

    function stopPom() {
      if (interval) clearInterval(interval);
      interval = null;
      state.mode = 'idle';
      btnStart.classList.remove('d-none');
      btnStop.classList.add('d-none');
      updateUI();
    }

    btnStart && btnStart.addEventListener('click', function (e) {
      e.preventDefault();
      startPom();
    });
    btnStop && btnStop.addEventListener('click', function (e) {
      e.preventDefault();
      stopPom();
    });

    // initial UI
    updateUI();
  }

  document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.quick-pomodoro').forEach(initPomodoroContainer);
  });

  // export for debugging
  window.Study = { initPomodoroContainer };
})();
