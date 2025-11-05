// Simple Pomodoro client and small helpers
(function () {
  function $(id) { return document.getElementById(id); }
  function formatTime(s) {
    const h = Math.floor(s / 3600), m = Math.floor((s % 3600) / 60), sec = s % 60;
    if (h) return `${String(h).padStart(2,'0')}:${String(m).padStart(2,'0')}:${String(sec).padStart(2,'0')}`;
    return `${String(m).padStart(2,'0')}:${String(sec).padStart(2,'0')}`;
  }

  function getCookie(name) {
    const match = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
    return match ? match.pop() : '';
  }

  // Pomodoro logic
  let pomInterval = null;
  let remaining = 0;
  let state = 'idle'; // work | break | idle
  let round = 1;
  let totalRounds = 1;
  let workSeconds = 25 * 60;
  let breakSeconds = 5 * 60;

  function updateDisplay() {
    const display = $('pomDisplay');
    const bar = $('pomBar');
    if (!display) return;
    if (state === 'idle') {
      display.textContent = 'Listo';
      bar.style.width = '0%';
      return;
    }
    display.textContent = `${state === 'work' ? 'Trabajo' : 'Descanso'} — Ronda ${round}/${totalRounds} — ${formatTime(remaining)}`;
    const total = (state === 'work' ? workSeconds : breakSeconds);
    const pct = Math.max(0, Math.min(100, Math.round((1 - (remaining / total)) * 100)));
    bar.style.width = pct + '%';
  }

  function tick() {
    remaining -= 1;
    if (remaining <= 0) {
      if (state === 'work') {
        state = 'break';
        remaining = breakSeconds;
      } else {
        round += 1;
        if (round > totalRounds) {
          stopPomodoro();
          $('pomDisplay').textContent = 'Pomodoro completado';
          return;
        }
        state = 'work';
        remaining = workSeconds;
      }
    }
    updateDisplay();
  }

  function startPomodoro(cfg) {
    workSeconds = (parseInt(cfg.workMinutes, 10) || 25) * 60;
    breakSeconds = (parseInt(cfg.breakMinutes, 10) || 5) * 60;
    totalRounds = parseInt(cfg.rounds, 10) || 4;
    round = 1;
    state = 'work';
    remaining = workSeconds;
    $('pomStart').classList.add('d-none');
    $('pomStop').classList.remove('d-none');
    updateDisplay();
    pomInterval = setInterval(tick, 1000);
  }

  function stopPomodoro() {
    if (pomInterval) clearInterval(pomInterval);
    pomInterval = null;
    state = 'idle';
    $('pomStart').classList.remove('d-none');
    $('pomStop').classList.add('d-none');
    updateDisplay();
  }

  document.addEventListener('DOMContentLoaded', function () {
    const startBtn = $('pomStart'), stopBtn = $('pomStop');
    if (!startBtn) return;
    startBtn.addEventListener('click', function () {
      const cfg = {
        workMinutes: $('pomWork').value,
        breakMinutes: $('pomBreak').value,
        rounds: $('pomRounds').value
      };
      startPomodoro(cfg);
    });
    stopBtn.addEventListener('click', function () { stopPomodoro(); });
    updateDisplay();
  });

  // expose small API if needed
  window.Pomodoro = {
    start: startPomodoro,
    stop: stopPomodoro
  };
})();
