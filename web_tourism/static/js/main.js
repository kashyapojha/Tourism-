/**
 * Incredible India — Main JS
 * Shared utilities used across all pages
 */

// ── Theme (Dark/Light) ────────────────────────────────────────────────────────
const Theme = (() => {
  const KEY = 'ii_theme';

  function apply(name) {
    const theme = name === 'dark' ? 'dark' : 'light';
    document.documentElement.setAttribute('data-theme', theme);
    try { localStorage.setItem(KEY, theme); } catch (_) {}
    updateToggleText(theme);
  }

  function getSaved() {
    try { return localStorage.getItem(KEY); } catch (_) { return null; }
  }

  function getPreferred() {
    const saved = getSaved();
    if (saved === 'dark' || saved === 'light') return saved;
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) return 'dark';
    return 'light';
  }

  function updateToggleText(theme) {
    const btn = document.getElementById('theme-toggle');
    if (!btn) return;
    btn.textContent = theme === 'dark' ? '☀️ Light' : '🌙 Dark';
  }

  function toggle() {
    const cur = document.documentElement.getAttribute('data-theme') || 'light';
    apply(cur === 'dark' ? 'light' : 'dark');
  }

  function init() {
    apply(getPreferred());
    const btn = document.getElementById('theme-toggle');
    if (btn) btn.addEventListener('click', toggle);
  }

  return { init, apply, toggle };
})();

// ── Toast Notifications ──────────────────────────────────────────────────────
const Toast = (() => {
  let container = null;

  function getContainer() {
    if (!container) {
      container = document.createElement('div');
      container.style.cssText = `
        position: fixed; bottom: 24px; right: 24px;
        z-index: 9999; display: flex; flex-direction: column; gap: 8px;
      `;
      document.body.appendChild(container);
    }
    return container;
  }

  function show(message, type = 'info', duration = 3000) {
    const el = document.createElement('div');
    const colors = {
      success: { bg: '#d1fae5', color: '#065f46', border: '#6ee7b7' },
      error:   { bg: '#fde8e8', color: '#9b1c1c', border: '#fca5a5' },
      info:    { bg: '#dbeafe', color: '#1e40af', border: '#93c5fd' },
    };
    const c = colors[type] || colors.info;
    el.style.cssText = `
      background: ${c.bg}; color: ${c.color}; border: 1px solid ${c.border};
      padding: 10px 16px; border-radius: 8px; font-size: 0.88rem;
      font-family: 'DM Sans', sans-serif; max-width: 300px;
      box-shadow: 0 4px 16px rgba(0,0,0,0.1);
      animation: slideIn 0.25s ease both;
      transition: opacity 0.3s;
    `;
    el.textContent = message;

    if (!document.getElementById('toast-style')) {
      const s = document.createElement('style');
      s.id = 'toast-style';
      s.textContent = `@keyframes slideIn { from { opacity:0; transform:translateX(20px); } to { opacity:1; transform:translateX(0); } }`;
      document.head.appendChild(s);
    }

    getContainer().appendChild(el);
    setTimeout(() => {
      el.style.opacity = '0';
      setTimeout(() => el.remove(), 300);
    }, duration);
  }

  return { show };
})();

// ── Read Aloud (TTS) via browser SpeechSynthesis ─────────────────────────────
// English-only (en-IN).
function setupReadAloud(readBtn, stopBtn, getText) {
  if (!readBtn || !stopBtn) return;
  const synth = window.speechSynthesis;
  const supported = !!(synth && window.SpeechSynthesisUtterance);

  function getVoices() {
    try { return synth.getVoices ? synth.getVoices() : []; } catch (_) { return []; }
  }

  function setState(isSpeaking) {
    readBtn.disabled = !supported || isSpeaking;
    stopBtn.disabled = !supported || !isSpeaking;
    readBtn.style.opacity = readBtn.disabled ? '0.6' : '1';
    stopBtn.style.opacity = stopBtn.disabled ? '0.6' : '1';
  }

  function stop() {
    try { synth.cancel(); } catch (_) {}
    setState(false);
  }

  function speak() {
    if (!supported) {
      Toast.show('Read aloud is not supported in this browser', 'error');
      return;
    }
    const text = (getText ? String(getText() || '') : '').trim();
    if (!text) {
      Toast.show('Nothing to read on this tab', 'info');
      return;
    }
    stop();

    function buildUtterance(voices) {
      const u = new SpeechSynthesisUtterance(text);
      u.lang = 'en-IN';
      u.rate = 1;
      u.pitch = 1;

      u.onend = () => setState(false);
      u.onerror = (e) => {
        setState(false);
        Toast.show('Text-to-speech failed. Try a different voice or browser.', 'error');
        // eslint-disable-next-line no-console
        console.debug('TTS error', e);
      };
      return u;
    }

    function trySpeak(attempt = 0) {
      const voices = getVoices();

      // Some browsers load voices asynchronously; retry a couple times.
      if (!voices.length && attempt < 3) {
        setTimeout(() => trySpeak(attempt + 1), 250);
        return;
      }

      const u = buildUtterance(voices);
      setState(true);

      // On some browsers, cancel() immediately followed by speak() can noop; schedule speak next tick.
      try { setTimeout(() => synth.speak(u), 0); } catch (_) { setState(false); }
    }

    trySpeak(0);
  }

  readBtn.addEventListener('click', speak);
  stopBtn.addEventListener('click', stop);
  window.addEventListener('beforeunload', stop);

  setState(false);
}

// ── API Helper ───────────────────────────────────────────────────────────────
async function apiPost(url, data) {
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.error || `HTTP ${res.status}`);
  }
  return res.json();
}

// ── Favourite Toggle ─────────────────────────────────────────────────────────
function setupFavButton(btn, stateName) {
  if (!btn) return;
  btn.addEventListener('click', async () => {
    try {
      const data = await apiPost('/api/favourite', { name: stateName });
      if (data.added) {
        btn.textContent = '★ Remove Favourite';
        btn.classList.add('fav-active');
        Toast.show('Added to favourites ⭐', 'success');
      } else {
        btn.textContent = '☆ Add to Favourites';
        btn.classList.remove('fav-active');
        Toast.show('Removed from favourites', 'info');
      }
    } catch (e) {
      Toast.show(e.message === 'HTTP 403' ? 'Please login to save favourites' : e.message, 'error');
    }
  });
}

// ── Visited Toggle ───────────────────────────────────────────────────────────
function setupVisitedButton(btn, stateName) {
  if (!btn) return;
  btn.addEventListener('click', async () => {
    try {
      const data = await apiPost('/api/visited', { name: stateName });
      if (data.added) {
        btn.textContent = '✓ Visited!';
        btn.classList.add('vis-active');
        Toast.show(`${stateName} marked as visited! ✓`, 'success');
      } else {
        btn.textContent = '○ Mark as Visited';
        btn.classList.remove('vis-active');
        Toast.show('Removed from visited', 'info');
      }
    } catch (e) {
      Toast.show(e.message === 'HTTP 403' ? 'Please login to track visits' : e.message, 'error');
    }
  });
}

// ── Random State ─────────────────────────────────────────────────────────────
async function goRandom() {
  try {
    const data = await fetch('/api/random').then(r => r.json());
    window.location.href = '/state/' + encodeURIComponent(data.name);
  } catch (e) {
    Toast.show('Could not load a random state', 'error');
  }
}

// ── State Grid Search ────────────────────────────────────────────────────────
function setupSearch(inputId, cardSelector) {
  const input = document.getElementById(inputId);
  const noResults = document.getElementById('no-results');
  if (!input) return;

  input.addEventListener('input', () => {
    const q = input.value.toLowerCase().trim();
    let visible = 0;
    document.querySelectorAll(cardSelector).forEach(card => {
      const text = [
        card.dataset.name  || '',
        card.dataset.tag   || '',
        card.dataset.food  || '',
        card.dataset.places || '',
      ].join(' ').toLowerCase();

      const match = !q || text.includes(q);
      card.style.display = match ? '' : 'none';
      if (match) visible++;
    });
    if (noResults) noResults.style.display = visible ? 'none' : '';
  });
}

// ── Tab Switcher ─────────────────────────────────────────────────────────────
function setupTabs(tabSelector, panelPrefix) {
  document.querySelectorAll(tabSelector).forEach(tab => {
    tab.addEventListener('click', () => {
      const id = tab.dataset.tab;
      document.querySelectorAll(tabSelector).forEach(t => t.classList.remove('active'));
      document.querySelectorAll(`[id^="${panelPrefix}"]`).forEach(p => p.classList.remove('active'));
      tab.classList.add('active');
      const panel = document.getElementById(panelPrefix + id);
      if (panel) panel.classList.add('active');
    });
  });
}

// ── Quiz countdown timer ─────────────────────────────────────────────────────
function startQuizTimer(seconds, onExpire) {
  const el = document.getElementById('quiz-timer');
  if (!el) return;
  let remaining = seconds;
  el.textContent = remaining;

  const interval = setInterval(() => {
    remaining--;
    el.textContent = remaining;
    if (remaining <= 5) el.style.color = '#c0392b';
    if (remaining <= 0) {
      clearInterval(interval);
      if (onExpire) onExpire();
    }
  }, 1000);

  return interval;
}

// ── Animate numbers (for stats) ───────────────────────────────────────────────
function animateCount(el, target, duration = 800) {
  const start = 0;
  const step = (timestamp) => {
    if (!el._startTime) el._startTime = timestamp;
    const progress = Math.min((timestamp - el._startTime) / duration, 1);
    el.textContent = Math.floor(progress * target);
    if (progress < 1) requestAnimationFrame(step);
    else el.textContent = target;
  };
  requestAnimationFrame(step);
}

// ── On DOM ready ─────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  Theme.init();

  // Animate any stat numbers on the page
  document.querySelectorAll('[data-count]').forEach(el => {
    const target = parseInt(el.dataset.count, 10);
    if (!isNaN(target)) animateCount(el, target);
  });

  // Auto-dismiss flash messages after 4s
  document.querySelectorAll('.flash').forEach(el => {
    setTimeout(() => {
      el.style.transition = 'opacity 0.4s';
      el.style.opacity = '0';
      setTimeout(() => el.remove(), 400);
    }, 4000);
  });
});