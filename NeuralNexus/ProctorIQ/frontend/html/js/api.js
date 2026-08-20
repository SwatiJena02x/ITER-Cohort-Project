// Port 8000 → served directly by FastAPI; use same origin.
// Port 8080 → served by nginx which proxies /api/* to FastAPI; use same origin.
// Any other port (e.g. local http.server dev) → fall back to localhost:8000.
const API_BASE = (typeof window !== 'undefined' && (window.location.port === '8000' || window.location.port === '8080'))
  ? window.location.origin
  : "http://localhost:8000";


const Auth = {

  setSession(data) {

    localStorage.setItem(
      "access_token",
      data.access_token
    );

    localStorage.setItem(
      "user_role",
      data.role
    );

    localStorage.setItem(
      "user_id",
      String(data.user_id)
    );

    localStorage.setItem(
      "user_name",
      data.name
    );

    localStorage.setItem(
      "user_email",
      data.email
    );

    sessionStorage.setItem(
      "userRole",
      data.role
    );

    sessionStorage.setItem(
      "userName",
      data.name
    );

    sessionStorage.setItem(
      "userEmail",
      data.email
    );

    sessionStorage.setItem(
      "userId",
      String(data.user_id)
    );
  },


  clearSession() {

    [
      "access_token",
      "user_role",
      "user_id",
      "user_name",
      "user_email"
    ].forEach(
      key => localStorage.removeItem(key)
    );

    sessionStorage.clear();
  },


  getToken() {

    return localStorage.getItem(
      "access_token"
    );
  },


  getRole() {

    return localStorage.getItem(
      "user_role"
    );
  },


  getUserId() {

    return localStorage.getItem(
      "user_id"
    );
  },


  getName() {

    return localStorage.getItem(
      "user_name"
    );
  },


  getEmail() {

    return localStorage.getItem(
      "user_email"
    );
  },


  isLoggedIn() {

    return Boolean(
      Auth.getToken()
    );
  }
};


/* ============================================================
   FETCH
   ============================================================ */

async function _fetch(
  path,
  options = {}
) {

  const token =
    Auth.getToken();

  const headers = {
    ...(options.headers || {})
  };

  if (token) {

    headers[
      "Authorization"
    ] = `Bearer ${token}`;
  }

  if (
    options.body &&
    !(options.body instanceof FormData)
  ) {

    headers[
      "Content-Type"
    ] = "application/json";
  }

  const response =
    await fetch(
      API_BASE + path,
      {
        ...options,
        headers
      }
    );

  if (response.status === 401) {

    /*
       Only clear the session for protected
       API calls. Login errors must not destroy
       the login tab state.
    */

    if (
      !path.includes(
        "/api/auth/"
      )
    ) {

      Auth.clearSession();

      window.location.href =
        "index.html?logout=true";
    }

    let detail =
      "Unauthorized.";

    try {

      const data =
        await response.json();

      detail =
        data.detail ||
        detail;

    } catch (_) {}

    throw new Error(
      detail
    );
  }

  if (!response.ok) {

    let message =
      `HTTP ${response.status}`;

    try {

      const data =
        await response.json();

      message =
        data.detail ||
        JSON.stringify(data);

    } catch (_) {}

    throw new Error(
      message
    );
  }

  if (
    response.status === 204
  ) {

    return null;
  }

  return response.json();
}


function _get(path) {

  return _fetch(
    path,
    {
      method: "GET"
    }
  );
}


function _post(
  path,
  body
) {

  if (
    body instanceof FormData
  ) {

    return _fetch(
      path,
      {
        method: "POST",
        body
      }
    );
  }

  return _fetch(
    path,
    {
      method: "POST",
      body: JSON.stringify(body)
    }
  );
}


/* ============================================================
   API
   ============================================================ */

const api = {

  async loginAdmin(
    email,
    password
  ) {

    const data =
      await _post(
        "/api/auth/admin/login",
        {
          email,
          password
        }
      );

    Auth.setSession(data);

    return data;
  },


  async loginStudent(
    identifier,
    password
  ) {

    const isEmail =
      identifier.includes("@");

    const body = isEmail
      ? {
          email:
            identifier.toLowerCase(),
          password
        }
      : {
          roll_number:
            identifier,
          password
        };

    const data =
      await _post(
        "/api/auth/student/login",
        body
      );

    Auth.setSession(data);

    return data;
  },


  async registerAdmin(
    name,
    email,
    password
  ) {

    const data =
      await _post(
        "/api/auth/admin/register",
        {
          name,
          email,
          password
        }
      );

    Auth.setSession(data);

    return data;
  },


  async registerStudent(
    formData
  ) {

    return _post(
      "/api/students",
      formData
    );
  },


  async getMyProfile() {

    return _get(
      "/api/students/me"
    );
  },


  async getMyNotices() {

    return _get(
      "/api/students/me/notices"
    );
  },


  async getStudents(
    limit = 100
  ) {

    return _get(
      `/api/students?limit=${limit}`
    );
  },


  async getStudentById(id) {

    return _get(
      `/api/students/${id}`
    );
  },


  async verifyStudentIdentity(
    studentId
  ) {

    return _post(
      `/api/students/${studentId}/verify`,
      {}
    );
  },


  async getStudentNotices(
    studentId
  ) {

    return _get(
      `/api/students/${studentId}/notices`
    );
  },


  async uploadMalpracticeImage(
    imageFile,
    studentCode
  ) {

    const form =
      new FormData();

    form.append(
      "image",
      imageFile
    );

    if (studentCode) {

      form.append(
        "student_code",
        studentCode
      );
    }

    return _post(
      "/api/malpractice/upload",
      form
    );
  },


  async generateReport(
    malpracticeEventId
  ) {

    return _post(
      "/api/reports/generate",
      {
        malpractice_event_id:
          malpracticeEventId
      }
    );
  },


  async getDashboardStats() {
    return _get(
      "/api/admin/dashboard"
    );
  },


  async getAllReports() {

    return _get(
      "/api/reports/all"
    );
  },


  async getReportsByStudent(
    studentId
  ) {

    return _get(
      `/api/reports/student/${studentId}`
    );
  },


  async getReport(reportId) {

    return _get(
      `/api/reports/${reportId}`
    );
  },


  async publishReport(
    reportId
  ) {

    return _post(
      `/api/reports/${reportId}/publish`,
      {}
    );
  },


  getDownloadUrl(
    reportId
  ) {

    const token =
      Auth.getToken();

    return (
      `${API_BASE}/api/reports/${reportId}/download` +
      `?token=${encodeURIComponent(token || "")}`
    );
  },


  logout() {

    Auth.clearSession();

    window.location.href =
      "index.html?logout=true";
  },


  Auth
};


window.api = api;
window.Auth = Auth;
