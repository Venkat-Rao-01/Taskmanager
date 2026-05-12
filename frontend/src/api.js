const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

export function getToken() {
  return localStorage.getItem("taskflow_token");
}

export function setSession(payload) {
  localStorage.setItem("taskflow_token", payload.access_token);
  localStorage.setItem("taskflow_user", JSON.stringify(payload.user));
}

export function clearSession() {
  localStorage.removeItem("taskflow_token");
  localStorage.removeItem("taskflow_user");
}

export function getStoredUser() {
  const raw = localStorage.getItem("taskflow_user");
  return raw ? JSON.parse(raw) : null;
}

export async function api(path, options = {}) {
  const token = getToken();
  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(options.headers || {}),
    },
  });

  if (response.status === 204) return null;
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.detail || "Something went wrong");
  }
  return data;
}
