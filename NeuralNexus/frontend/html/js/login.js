/* ============================================================
   LOGIN PAGE
   Real backend authentication
   ============================================================ */

function switchTab(role) {

  if (window.Auth) {
    window.Auth.clearSession();
  }

  const adminTab = document.getElementById("tab-admin");
  const studentTab = document.getElementById("tab-student");

  const adminPanel = document.getElementById("panel-admin");
  const studentPanel = document.getElementById("panel-student");

  adminTab.classList.remove("active");
  studentTab.classList.remove("active");

  adminPanel.classList.remove("active");
  studentPanel.classList.remove("active");

  if (role === "student") {

    studentTab.classList.add("active");
    studentPanel.classList.add("active");

    studentTab.setAttribute(
      "aria-selected",
      "true"
    );

    adminTab.setAttribute(
      "aria-selected",
      "false"
    );

  } else {

    adminTab.classList.add("active");
    adminPanel.classList.add("active");

    adminTab.setAttribute(
      "aria-selected",
      "true"
    );

    studentTab.setAttribute(
      "aria-selected",
      "false"
    );
  }
}


/* ============================================================
   ADMIN LOGIN
   ============================================================ */

async function handleAdminLogin(event) {

  event.preventDefault();

  const email =
    document.getElementById(
      "admin-email"
    ).value.trim();

  const password =
    document.getElementById(
      "admin-password"
    ).value;

  const error =
    document.getElementById(
      "admin-error"
    );

  const button =
    document.getElementById(
      "admin-login-btn"
    );

  if (!email || !password) {

    error.textContent =
      "Please enter admin email and password.";

    error.classList.remove("hidden");

    return;
  }

  error.classList.add("hidden");

  button.disabled = true;

  button.textContent =
    "Authenticating...";

  try {

    const data =
      await api.loginAdmin(
        email,
        password
      );

    if (data.role !== "admin") {

      throw new Error(
        "Invalid account role."
      );
    }

    showToast(
      `Welcome, ${data.name}!`,
      "success"
    );

    setTimeout(() => {

      window.location.href =
        "admin-dashboard.html";

    }, 500);

  } catch (errorObject) {

    button.disabled = false;

    button.textContent =
      "➜ Enter Admin Portal";

    error.textContent =
      errorObject.message ||
      "Admin login failed.";

    error.classList.remove("hidden");
  }
}


/* ============================================================
   STUDENT LOGIN
   ============================================================ */

async function handleStudentLogin(event) {

  event.preventDefault();

  const identifier =
    document.getElementById(
      "student-id"
    ).value.trim();

  const password =
    document.getElementById(
      "student-password"
    ).value;

  const error =
    document.getElementById(
      "student-error"
    );

  const button =
    document.getElementById(
      "student-login-btn"
    );

  if (!identifier || !password) {

    error.textContent =
      "Please enter your email/roll number and password.";

    error.classList.remove("hidden");

    return;
  }

  error.classList.add("hidden");

  button.disabled = true;

  button.textContent =
    "Verifying...";

  try {

    const data =
      await api.loginStudent(
        identifier,
        password
      );

    if (data.role !== "student") {

      throw new Error(
        "This account is not a student account."
      );
    }

    /*
       Fetch real student profile after login.
    */

    try {

      const profile =
        await api.getMyProfile();

      sessionStorage.setItem(
        "userRoll",
        profile.roll_number ||
        profile.student_code ||
        ""
      );

      sessionStorage.setItem(
        "userCourse",
        profile.course ||
        ""
      );

      sessionStorage.setItem(
        "userRegistrationDate",
        profile.created_at ||
        ""
      );

    } catch (profileError) {

      console.error(
        "Profile fetch failed:",
        profileError
      );
    }

    showToast(
      `Welcome, ${data.name}!`,
      "success"
    );

    setTimeout(() => {

      window.location.href =
        "student-dashboard.html";

    }, 500);

  } catch (errorObject) {

    button.disabled = false;

    button.textContent =
      "➜ Enter Student Portal";

    error.textContent =
      errorObject.message ||
      "Student login failed.";

    error.classList.remove("hidden");
  }
}


/* ============================================================
   PAGE LOAD
   ============================================================ */

document.addEventListener(
  "DOMContentLoaded",
  () => {

    const params =
      new URLSearchParams(
        window.location.search
      );

    const requestedTab =
      params.get("tab");

    const logout =
      params.get("logout") === "true";

    if (logout && window.Auth) {

      window.Auth.clearSession();
    }

    if (
      requestedTab === "student" ||
      requestedTab === "admin"
    ) {

      switchTab(
        requestedTab
      );

    } else {

      switchTab("admin");
    }

    /*
       Do not redirect if the user intentionally
       opened a login tab.
    */

    if (
      !logout &&
      !requestedTab &&
      window.Auth &&
      window.Auth.isLoggedIn()
    ) {

      const role =
        window.Auth.getRole();

      if (role === "admin") {

        window.location.href =
          "admin-dashboard.html";

        return;
      }

      if (role === "student") {

        window.location.href =
          "student-dashboard.html";

        return;
      }
    }
  }
);
