/**
 * ZERVO API Service Client
 * Connects frontend pages to the FastAPI + Supabase PostgreSQL Backend
 */

const API_BASE = window.API_BASE_URL || 
  (typeof import.meta !== 'undefined' && import.meta.env && import.meta.env.VITE_API_BASE_URL) || 
  'https://zervo-1.onrender.com/api/v1';

// Helper to handle Auth Token
function getAuthHeaders() {
  const token = localStorage.getItem('zervo_token');
  const headers = { 'Content-Type': 'application/json' };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  return headers;
}

// Universal fetch wrapper
async function request(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const config = {
    headers: getAuthHeaders(),
    ...options
  };

  try {
    const response = await fetch(url, config);
    const data = await response.json().catch(() => ({}));
    
    if (!response.ok) {
      throw new Error(data.detail || `HTTP Error ${response.status}`);
    }
    return data;
  } catch (err) {
    console.warn(`API Error [${endpoint}]:`, err.message);
    throw err;
  }
}

// ── Auth Endpoints ──────────────────────────────────────────────────────────
export async function apiRegister(name, email, password, phone = '') {
  return await request('/auth/register', {
    method: 'POST',
    body: JSON.stringify({ name, email, password, phone })
  });
}

export async function apiLogin(email, password) {
  return await request('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password })
  });
}

export async function apiGetMe() {
  return await request('/auth/me');
}

// ── Profile Endpoints ───────────────────────────────────────────────────────
export async function apiGetProfile() {
  return await request('/users/profile');
}

export async function apiUpdateProfile(name, phone) {
  return await request('/users/profile', {
    method: 'PUT',
    body: JSON.stringify({ name, phone })
  });
}

export async function apiChangePassword(oldPassword, newPassword) {
  return await request('/users/password', {
    method: 'POST',
    body: JSON.stringify({ old_password: oldPassword, new_password: newPassword })
  });
}

export async function apiUpdateRole(role) {
  return await request('/users/role', {
    method: 'PUT',
    body: JSON.stringify({ role })
  });
}

// ── Food Endpoints ──────────────────────────────────────────────────────────
export async function apiCreateFoodListing(listingData) {
  return await request('/food/listings', {
    method: 'POST',
    body: JSON.stringify(listingData)
  });
}

export async function apiGetFoodListings() {
  return await request('/food/listings');
}

export async function apiCreateFoodRequest(requestData) {
  return await request('/food/requests', {
    method: 'POST',
    body: JSON.stringify(requestData)
  });
}

export async function apiGetFoodRequests() {
  return await request('/food/requests');
}

// ── Volunteer Endpoints ─────────────────────────────────────────────────────
export async function apiGetVolunteerDashboard() {
  return await request('/volunteer/dashboard');
}

export async function apiClaimPickup(foodId) {
  return await request(`/volunteer/claim/${foodId}`, {
    method: 'POST'
  });
}

export async function apiDeliverPickup(foodId, photoBase64 = null) {
  return await request(`/volunteer/deliver/${foodId}`, {
    method: 'POST',
    body: JSON.stringify({ photo: photoBase64 })
  });
}

// ── Notification Endpoints ──────────────────────────────────────────────────
export async function apiGetNotifications() {
  return await request('/notifications');
}

export async function apiMarkNotificationsRead() {
  return await request('/notifications/mark-read', {
    method: 'POST'
  });
}

// ── AI Extraction Endpoints ────────────────────────────────────────────────
export async function apiExtractFoodDetails(description) {
  try {
    return await request('/ai/extract-food', {
      method: 'POST',
      body: JSON.stringify({ description })
    });
  } catch (err) {
    // Also try alternate top-level /api/ai/extract-food path if needed
    const altUrl = `${API_BASE.replace('/api/v1', '')}/api/ai/extract-food`;
    const res = await fetch(altUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ description })
    });
    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      throw new Error(errData.detail || `AI Extraction failed (${res.status})`);
    }
    return await res.json();
  }
}

window.zervoAPI = {
  apiRegister,
  apiLogin,
  apiGetMe,
  apiGetProfile,
  apiUpdateProfile,
  apiChangePassword,
  apiUpdateRole,
  apiCreateFoodListing,
  apiGetFoodListings,
  apiCreateFoodRequest,
  apiGetFoodRequests,
  apiGetVolunteerDashboard,
  apiClaimPickup,
  apiDeliverPickup,
  apiGetNotifications,
  apiMarkNotificationsRead,
  apiExtractFoodDetails
};

