/* ── SHARED SIDEBAR / DASHBOARD JS ──────────────────────── */


/* =========================================================
   SESSION GUARD
   ========================================================= */

function guardRoute(requiredRole) {

  const localRole =
    window.Auth && typeof window.Auth.getRole === 'function'
      ? window.Auth.getRole()
      : null;

  const sessionRole =
    sessionStorage.getItem('userRole');

  const role = localRole || sessionRole;

  console.log('--------------------------------');
  console.log('ROUTE GUARD');
  console.log('Required Role:', requiredRole);
  console.log('LocalStorage Role:', localRole);
  console.log('SessionStorage Role:', sessionRole);
  console.log('Final Role:', role);
  console.log('--------------------------------');

  /* No login session */
  if (!role) {

    console.warn('No logged-in user found.');

    window.location.replace('index.html');

    return false;
  }


  /* Normalize role */
  const currentRole = String(role).trim().toLowerCase();
  const expectedRole = String(requiredRole || '').trim().toLowerCase();


  /* Wrong role */
  if (expectedRole && currentRole !== expectedRole) {

    console.warn(
      `Wrong role. Expected: ${expectedRole}, Found: ${currentRole}`
    );

    if (currentRole === 'admin') {

      window.location.replace('admin-dashboard.html');

    } else if (currentRole === 'student') {

      window.location.replace('student-dashboard.html');

    } else {

      if (window.Auth) {
        window.Auth.clearSession();
      } else {
        localStorage.clear();
        sessionStorage.clear();
      }

      window.location.replace('index.html');
    }

    return false;
  }


  console.log('Route access granted.');

  return true;
}


/* =========================================================
   RENDER SIDEBAR
   ========================================================= */

function renderSidebar(activeNav, role) {

  const userName =
    (window.Auth && window.Auth.getName())
    || sessionStorage.getItem('userName')
    || 'User';

  const userRole =
    (window.Auth && window.Auth.getRole())
    || sessionStorage.getItem('userRole')
    || role;

  const userEmail =
    (window.Auth && window.Auth.getEmail())
    || sessionStorage.getItem('userEmail')
    || '';


  const adminNav = [

    {
      id: 'dashboard',
      label: 'Dashboard',
      icon: '📊',
      href: 'admin-dashboard.html'
    },

    {
      id: 'students',
      label: 'Students',
      icon: '👥',
      href: 'admin-students.html'
    },

    {
      id: 'analyze',
      label: 'Upload & Analyze',
      icon: '🔍',
      href: 'admin-analyze.html'
    },

    {
      id: 'reports',
      label: 'Reports',
      icon: '📋',
      href: 'admin-reports.html'
    },

    {
      id: 'noticeboard',
      label: 'Notice Board',
      icon: '📢',
      href: 'admin-noticeboard.html'
    }

  ];


  const studentNav = [

    {
      id: 'dashboard',
      label: 'Dashboard',
      icon: '🏠',
      href: 'student-dashboard.html'
    },

    {
      id: 'profile',
      label: 'My Profile',
      icon: '👤',
      href: 'student-profile.html'
    },

    {
      id: 'reports',
      label: 'My Reports',
      icon: '📋',
      href: 'student-reports.html'
    }

  ];


  const navItems =
    userRole === 'admin'
      ? adminNav
      : studentNav;


  const navHTML = navItems.map(item => `

    <a
      href="${item.href}"
      class="nav-item ${item.id === activeNav ? 'active' : ''}"
      id="nav-${item.id}"
    >

      <span class="nav-icon">
        ${item.icon}
      </span>

      ${item.label}

    </a>

  `).join('');


  const sidebar =
    document.getElementById('sidebar');

  if (!sidebar) return;


  sidebar.innerHTML = `

    <div class="sidebar-logo-wrap brand-lockup">

      <img
        src="assets/logo.png"
        class="brand-icon"
        alt="ProctorIQ logo"
        style="width: 34px !important; height: 34px !important; max-width: 34px !important; max-height: 34px !important; object-fit: contain; flex-shrink: 0; display: block;"
        onerror="this.onerror=null; this.src='../assets/logo.png';"
      />
      <span class="brand-wordmark on-dark" style="font-size: 1.15rem; font-weight: 800; color: #ffffff; white-space: nowrap;">Proctor<span class="accent" style="color: #60a5fa;">IQ</span></span>

    </div>


    <div class="sidebar-user">

      Logged in as:
      <b>${userName}</b>

      <br>

      <span style="font-size:0.75rem;">
        ${userEmail}
      </span>

    </div>


    <nav class="sidebar-nav">

      ${navHTML}

    </nav>


    <div class="sidebar-footer">

      <button
        class="logout-btn"
        onclick="logout()"
      >

        <span>🚪</span>
        Logout

      </button>

    </div>

  `;
}


/* =========================================================
   RENDER TOPBAR
   ========================================================= */

function renderTopbar(pageTitle) {

  const userRole =
    (window.Auth && window.Auth.getRole())
    || sessionStorage.getItem('userRole')
    || '';

  const portalLabel =
    userRole.toLowerCase() === 'admin' ? 'Admin Portal' :
    userRole.toLowerCase() === 'student' ? 'Student Portal' :
    'Portal';

  const userName =
    (window.Auth && window.Auth.getName())
    || sessionStorage.getItem('userName')
    || 'User';


  const initials =
    userName
      .split(' ')
      .map(n => n[0])
      .join('')
      .slice(0, 2)
      .toUpperCase();


  const now = new Date();


  const dateStr =
    now.toLocaleDateString(
      'en-GB',
      {
        weekday: 'long',
        day: 'numeric',
        month: 'long',
        year: 'numeric'
      }
    );


  const topbar =
    document.getElementById('topbar');

  if (!topbar) return;


  topbar.innerHTML = `

    <div>

      <span class="topbar-title">
        ${portalLabel} <span class="topbar-crumb-sep">›</span> ${pageTitle}
      </span>

    </div>


    <div class="topbar-right">

      <span class="topbar-date">
        ${dateStr}
      </span>

      <div
        class="topbar-avatar"
        title="${userName}"
      >
        ${initials}
      </div>

    </div>

  `;
}


/* =========================================================
   LOGOUT
   ========================================================= */

function logout() {

  showToast(
    'Logged out successfully.',
    'info',
    1500
  );


  setTimeout(() => {

    if (window.api) {

      window.api.logout();

    } else {

      sessionStorage.clear();
      localStorage.clear();

      window.location.replace(
        'index.html'
      );

    }

  }, 400);

}


/* =========================================================
   FALLBACK MOCK DATA
   ========================================================= */

const MOCK_STUDENTS = [

  {
    name: 'Aarav Kumar',
    roll: '2023CS101',
    email: 'aarav.kumar@email.com',
    course: 'CSE',
    reg_date: '10 May 2025',
    status: 'Verified',
    reports: 3,
    score: 82,
    level: 'High'
  },

  {
    name: 'Priya Sharma',
    roll: '2023CS102',
    email: 'priya.sharma@email.com',
    course: 'CSE',
    reg_date: '09 May 2025',
    status: 'Verified',
    reports: 1,
    score: 45,
    level: 'Medium'
  },

  {
    name: 'Rohan Das',
    roll: '2023CS103',
    email: 'rohan.das@email.com',
    course: 'ECE',
    reg_date: '08 May 2025',
    status: 'Verified',
    reports: 2,
    score: 91,
    level: 'Critical'
  },

  {
    name: 'Sneha Patra',
    roll: '2023CS104',
    email: 'sneha.patra@email.com',
    course: 'IT',
    reg_date: '08 May 2025',
    status: 'Verified',
    reports: 1,
    score: 22,
    level: 'Low'
  },

  {
    name: 'Aditya Verma',
    roll: '2023CS105',
    email: 'aditya.verma@email.com',
    course: 'CSE',
    reg_date: '07 May 2025',
    status: 'Verified',
    reports: 1,
    score: 67,
    level: 'Medium'
  },

  {
    name: 'Ananya Sen',
    roll: '2023CS106',
    email: 'ananya.sen@email.com',
    course: 'ECE',
    reg_date: '06 May 2025',
    status: 'Pending',
    reports: 0,
    score: 0,
    level: '—'
  }

];


const MOCK_REPORTS = [

  {
    id: 'RPT-2026-00642',
    student: 'Aarav Kumar',
    roll: '2023CS101',
    score: 82,
    level: 'High',
    date: '16 August 2026',
    status: 'Published'
  },

  {
    id: 'RPT-2026-00643',
    student: 'Priya Sharma',
    roll: '2023CS102',
    score: 45,
    level: 'Medium',
    date: '16 August 2026',
    status: 'Published'
  },

  {
    id: 'RPT-2026-00644',
    student: 'Rohan Das',
    roll: '2023CS103',
    score: 91,
    level: 'Critical',
    date: '15 August 2026',
    status: 'Published'
  },

  {
    id: 'RPT-2026-00645',
    student: 'Sneha Patra',
    roll: '2023CS104',
    score: 22,
    level: 'Low',
    date: '15 August 2026',
    status: 'Published'
  },

  {
    id: 'RPT-2026-00646',
    student: 'Aditya Verma',
    roll: '2023CS105',
    score: 67,
    level: 'Medium',
    date: '14 August 2026',
    status: 'Draft'
  }

];


/* =========================================================
   RISK HELPERS
   ========================================================= */

function getLevelBadgeClass(level) {

  const normalized =
    String(level || '')
      .trim()
      .toLowerCase();


  const m = {

    low: 'badge-low',

    medium: 'badge-medium',

    high: 'badge-high',

    critical: 'badge-critical'

  };


  return m[normalized] || 'badge-info';
}


function getLevelColor(level) {

  const normalized =
    String(level || '')
      .trim()
      .toLowerCase();


  const m = {

    low: '#10b981',

    medium: '#f59e0b',

    high: '#ef4444',

    critical: '#9d174d'

  };


  return m[normalized] || '#64748b';
}


function getInitials(name) {

  if (!name) return 'US';


  return name
    .split(' ')
    .filter(Boolean)
    .map(n => n[0])
    .join('')
    .slice(0, 2)
    .toUpperCase();

}
