/* ── THEME SHARED JS ─────────────────────────────────────── */

/* ── Utility: Toggle Password Visibility ─ */
function togglePassword(inputId, btn) {
  const inp = document.getElementById(inputId);
  if (!inp) return;
  if (inp.type === 'password') {
    inp.type = 'text';
    btn.querySelector('.eye-icon').style.opacity = '0.5';
  } else {
    inp.type = 'password';
    btn.querySelector('.eye-icon').style.opacity = '1';
  }
}

/* ── Spinner ─────────────────────────────── */
function showSpinner(message = 'Processing…') {
  let overlay = document.getElementById('spinner-overlay');
  if (!overlay) {
    overlay = document.createElement('div');
    overlay.id = 'spinner-overlay';
    overlay.className = 'spinner-overlay';
    overlay.innerHTML = `
      <div class="spinner-box">
        <div class="spinner"></div>
        <div id="spinner-msg" style="font-weight:600; color:#0f172a; font-family:'Plus Jakarta Sans',sans-serif;">${message}</div>
      </div>`;
    document.body.appendChild(overlay);
  } else {
    document.getElementById('spinner-msg').textContent = message;
    overlay.classList.remove('hidden');
  }
}

function hideSpinner() {
  const overlay = document.getElementById('spinner-overlay');
  if (overlay) overlay.classList.add('hidden');
}

/* ── Alert Toast ──────────────────────────── */
function showToast(message, type = 'success', duration = 3500) {
  const icons = { success: '✓', error: '✕', info: 'ℹ', warning: '⚠' };
  const toast = document.createElement('div');
  toast.style.cssText = `
    position: fixed; top: 24px; right: 24px; z-index: 9999;
    background: white; border-radius: 12px; padding: 14px 18px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.15); border: 1px solid #e2e8f0;
    display: flex; align-items: center; gap: 10px;
    font-family: 'Plus Jakarta Sans', sans-serif; font-size: 0.88rem;
    max-width: 340px; animation: slideInRight 0.3s ease;
    font-weight: 600; color: #0f172a;
  `;
  const colors = { success: '#10b981', error: '#ef4444', info: '#3b82f6', warning: '#f59e0b' };
  toast.innerHTML = `
    <span style="font-size:1.1rem; color:${colors[type]}">${icons[type]}</span>
    <span>${message}</span>
  `;
  document.body.appendChild(toast);
  setTimeout(() => {
    toast.style.animation = 'fadeOut 0.3s ease forwards';
    setTimeout(() => toast.remove(), 300);
  }, duration);
}

/* ── Format Date ──────────────────────────── */
function formatDate(dateStr) {
  const d = new Date(dateStr);
  return d.toLocaleDateString('en-GB', { day: 'numeric', month: 'long', year: 'numeric' });
}

/* ── Add Animation ────────────────────────── */
function animateIn(el) {
  if (!el) return;
  el.style.opacity = '0';
  el.style.transform = 'translateY(12px)';
  el.style.transition = 'opacity 0.35s ease, transform 0.35s ease';
  requestAnimationFrame(() => {
    el.style.opacity = '1';
    el.style.transform = 'translateY(0)';
  });
}

/* ── Validation Helpers ───────────────────── */
const Validators = {
  /* Password: capital first, 8+ chars, digit, special char */
  password(pw) {
    if (pw.length < 8)              return 'Password must be at least 8 characters.';
    if (!/^[A-Z]/.test(pw))        return 'Password must start with a capital letter.';
    if (!/\d/.test(pw))            return 'Password must contain at least one number.';
    if (!/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(pw))
                                   return 'Password must contain at least one special character.';
    return null;
  },
  email(em) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(em) ? null : 'Enter a valid email address.';
  }
};

/* ── CSS Keyframes injected dynamically ───── */
const styleTag = document.createElement('style');
styleTag.textContent = `
  @keyframes slideInRight {
    from { opacity: 0; transform: translateX(24px); }
    to   { opacity: 1; transform: translateX(0); }
  }
  @keyframes fadeOut {
    to { opacity: 0; transform: translateX(24px); }
  }
`;
document.head.appendChild(styleTag);
