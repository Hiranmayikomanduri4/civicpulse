/**
 * CivicPulse AI - Frontend API Service Client
 * Handles communication with the FastAPI backend endpoints.
 */

const API_BASE_URL = window.location.origin;

const API = {
  // Auth Token Utilities
  getToken() {
    return localStorage.getItem('civicpulse_admin_token');
  },
  
  setToken(token) {
    localStorage.setItem('civicpulse_admin_token', token);
  },
  
  clearToken() {
    localStorage.removeItem('civicpulse_admin_token');
    localStorage.removeItem('civicpulse_admin_user');
  },
  
  getUser() {
    const u = localStorage.getItem('civicpulse_admin_user');
    return u ? JSON.parse(u) : null;
  },

  setUser(user) {
    localStorage.setItem('civicpulse_admin_user', JSON.stringify(user));
  },

  isLoggedIn() {
    return !!this.getToken();
  },

  // Generic Request Helper
  async request(endpoint, options = {}) {
    const headers = options.headers || {};
    
    // Add Authorization header if available
    const token = this.getToken();
    if (token && !headers['Authorization']) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    // Do not set Content-Type if sending FormData (browser sets boundary automatically)
    if (!(options.body instanceof FormData) && !headers['Content-Type']) {
      headers['Content-Type'] = 'application/json';
    }

    options.headers = headers;

    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
      
      if (!response.ok) {
        let errMessage = `Error ${response.status}: ${response.statusText}`;
        try {
          const errData = await response.json();
          if (errData && errData.detail) {
            errMessage = typeof errData.detail === 'string' ? errData.detail : JSON.stringify(errData.detail);
          }
        } catch (_) {}
        throw new Error(errMessage);
      }

      return await response.json();
    } catch (error) {
      console.error(`API Request Failed [${endpoint}]:`, error);
      throw error;
    }
  },

  // Endpoints
  async getHealth() {
    return this.request('/api/health');
  },

  async getReports({ page = 1, limit = 10, category = '', status = '', priority = '', search = '', sort_by = 'created_at', sort_order = 'desc' } = {}) {
    const params = new URLSearchParams();
    if (page) params.append('page', page);
    if (limit) params.append('limit', limit);
    if (category && category !== 'All') params.append('category', category);
    if (status && status !== 'All') params.append('status', status);
    if (priority && priority !== 'All') params.append('priority', priority);
    if (search) params.append('search', search);
    if (sort_by) params.append('sort_by', sort_by);
    if (sort_order) params.append('sort_order', sort_order);

    return this.request(`/api/reports?${params.toString()}`);
  },

  async getReport(reportId) {
    return this.request(`/api/reports/${encodeURIComponent(reportId)}`);
  },

  async createReport(formData) {
    return this.request('/api/reports', {
      method: 'POST',
      body: formData
    });
  },

  async upvoteReport(reportId) {
    return this.request(`/api/reports/${encodeURIComponent(reportId)}/upvote`, {
      method: 'POST'
    });
  },

  async classifyImage(imageFile, textHint = '') {
    const formData = new FormData();
    formData.append('image', imageFile);
    if (textHint) formData.append('text_hint', textHint);

    return this.request('/api/reports/ai-classify', {
      method: 'POST',
      body: formData
    });
  },

  async checkDuplicates({ category, description, latitude, longitude }) {
    return this.request('/api/reports/check-duplicate', {
      method: 'POST',
      body: JSON.stringify({ category, description, latitude, longitude })
    });
  },

  async getAnalytics() {
    return this.request('/api/analytics');
  },

  async getMapReports({ category = '', status = '', priority = '' } = {}) {
    const params = new URLSearchParams();
    if (category && category !== 'All') params.append('category', category);
    if (status && status !== 'All') params.append('status', status);
    if (priority && priority !== 'All') params.append('priority', priority);

    return this.request(`/api/map/reports?${params.toString()}`);
  },

  async reverseGeocode(latitude, longitude) {
    try {
      return await this.request(`/api/map/reverse-geocode?latitude=${latitude}&longitude=${longitude}`);
    } catch (_) {
      return { address: `Lat: ${latitude.toFixed(4)}, Lon: ${longitude.toFixed(4)}` };
    }
  },

  // Admin Endpoints
  async adminLogin(username, password) {
    const data = await this.request('/api/admin/login', {
      method: 'POST',
      body: JSON.stringify({ username, password })
    });
    this.setToken(data.access_token);
    this.setUser(data.user_info);
    return data;
  },

  async getAdminProfile() {
    return this.request('/api/admin/me');
  },

  async updateReportStatus(reportId, newStatus, remarks = '') {
    return this.request(`/api/admin/reports/${encodeURIComponent(reportId)}/status`, {
      method: 'PATCH',
      body: JSON.stringify({ new_status: newStatus, remarks })
    });
  },

  async resolveWithProof(reportId, remarks, proofImageFile = null) {
    const formData = new FormData();
    formData.append('remarks', remarks);
    if (proofImageFile) {
      formData.append('proof_image', proofImageFile);
    }
    return this.request(`/api/admin/reports/${encodeURIComponent(reportId)}/resolve-with-proof`, {
      method: 'POST',
      body: formData
    });
  }
};
