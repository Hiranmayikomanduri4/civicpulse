/**
 * CivicPulse AI - Main Frontend Application Controller
 * Handles view routing, dynamic data fetching, AI vision triggers,
 * duplicate detection alerts, form submissions, and modals.
 */

document.addEventListener('DOMContentLoaded', () => {
  App.init();
});

const App = {
  currentView: 'dashboard',
  selectedImageFile: null,
  pickerCoords: { lat: 28.6139, lng: 77.2090 },
  aiClassificationResult: null,
  reportsState: {
    page: 1,
    limit: 9,
    category: '',
    status: '',
    priority: '',
    search: '',
    sort_by: 'created_at',
    sort_order: 'desc'
  },

  async init() {
    this.bindNavigation();
    this.bindReportForm();
    this.bindFilters();
    this.bindAdminActions();
    this.checkHealth();
    this.checkAdminSession();

    // Load initial view
    this.navigate('dashboard');
  },

  // View Navigation
  navigate(viewName) {
    this.currentView = viewName;

    // Update nav links
    document.querySelectorAll('.nav-link').forEach(link => {
      link.classList.toggle('active', link.dataset.view === viewName);
    });

    // Update view panels
    document.querySelectorAll('.view-section').forEach(view => {
      view.classList.toggle('active', view.id === `view-${viewName}`);
    });

    // Update Header Title
    const titles = {
      dashboard: 'Municipal Overview & KPIs',
      report: 'Report a Civic Issue',
      reports: 'All Reported Issues',
      map: 'Interactive Civic Map',
      analytics: 'Resolution Analytics & Trends',
      admin: 'Municipal Admin Portal',
      about: 'About Project & Architecture'
    };
    const titleEl = document.getElementById('header-page-title');
    if (titleEl) titleEl.textContent = titles[viewName] || 'CivicPulse AI';

    // View-specific initializers
    if (viewName === 'dashboard') {
      this.loadDashboardData();
    } else if (viewName === 'report') {
      setTimeout(() => {
        MapModule.initPickerMap('picker-map-container', (lat, lng) => {
          this.onPickerLocationChanged(lat, lng);
        });
      }, 150);
    } else if (viewName === 'reports') {
      this.loadReportsList();
    } else if (viewName === 'map') {
      setTimeout(() => {
        MapModule.initFullMap('leaflet-full-map');
        this.loadMapReports();
      }, 150);
    } else if (viewName === 'analytics') {
      this.loadAnalyticsData();
    } else if (viewName === 'admin') {
      this.refreshAdminView();
    }
  },

  bindNavigation() {
    document.querySelectorAll('[data-view]').forEach(el => {
      el.addEventListener('click', (e) => {
        e.preventDefault();
        const view = el.dataset.view;
        this.navigate(view);

        // Close mobile sidebar if open
        const sidebar = document.querySelector('.sidebar');
        if (sidebar) sidebar.classList.remove('mobile-open');
      });
    });

    // Mobile sidebar toggle
    const toggleBtn = document.getElementById('btn-mobile-toggle');
    if (toggleBtn) {
      toggleBtn.addEventListener('click', () => {
        const sidebar = document.querySelector('.sidebar');
        if (sidebar) sidebar.classList.toggle('mobile-open');
      });
    }

    // Modal close buttons
    document.querySelectorAll('.btn-close-modal, .modal-overlay').forEach(el => {
      el.addEventListener('click', (e) => {
        if (e.target === el || el.classList.contains('btn-close-modal') || el.closest('.btn-close-modal')) {
          this.closeModals();
        }
      });
    });
  },

  // Health Check
  async checkHealth() {
    try {
      const data = await API.getHealth();
      const dot = document.getElementById('status-indicator-dot');
      const text = document.getElementById('status-indicator-text');
      if (dot && text) {
        dot.style.background = '#10B981';
        text.textContent = 'Backend Active (v' + data.version + ')';
      }
    } catch (_) {
      const dot = document.getElementById('status-indicator-dot');
      const text = document.getElementById('status-indicator-text');
      if (dot && text) {
        dot.style.background = '#EF4444';
        text.textContent = 'Server Connecting...';
      }
    }
  },

  // =========================================================================
  // Dashboard Logic
  // =========================================================================
  async loadDashboardData() {
    try {
      const [analytics, reportsData] = await Promise.all([
        API.getAnalytics(),
        API.getReports({ page: 1, limit: 4, sort_by: 'created_at', sort_order: 'desc' })
      ]);

      // Populate KPI Cards
      document.getElementById('kpi-total-val').textContent = analytics.total_reports;
      document.getElementById('kpi-pending-val').textContent = analytics.pending_reports + analytics.in_progress_reports;
      document.getElementById('kpi-resolved-val').textContent = analytics.resolved_reports;
      document.getElementById('kpi-critical-val').textContent = analytics.high_priority_reports;
      document.getElementById('kpi-rate-val').textContent = `${analytics.resolution_rate_percentage}%`;

      // Render Mini Chart
      ChartsModule.renderTrendsChart('dash-chart-trends', analytics.daily_trends);

      // Render Recent Feed
      const feedContainer = document.getElementById('dash-recent-feed');
      if (!feedContainer) return;
      
      if (!reportsData.reports || reportsData.reports.length === 0) {
        feedContainer.innerHTML = '<div style="color:#64748B; text-align:center; padding:20px;">No complaints recorded yet.</div>';
        return;
      }

      feedContainer.innerHTML = reportsData.reports.map(r => `
        <div class="feed-item" onclick="window.viewReportDetail('${r.id}')">
          <img class="feed-thumb" src="${r.image_url || '/uploads/sample_pothole.jpg'}" alt="${r.category}" />
          <div class="feed-info">
            <div class="feed-title">${this.escapeHtml(r.title)}</div>
            <div class="feed-meta">
              <span class="badge badge-${r.priority.toLowerCase()}">${r.priority}</span>
              <span class="badge badge-status">${r.status}</span>
              <span>📍 ${this.escapeHtml(r.address.split(',')[0])}</span>
            </div>
          </div>
        </div>
      `).join('');
    } catch (err) {
      console.error('Error loading dashboard:', err);
    }
  },

  // =========================================================================
  // Report Submission Wizard & AI Vision Logic
  // =========================================================================
  bindReportForm() {
    const dropzone = document.getElementById('report-dropzone');
    const fileInput = document.getElementById('report-file-input');
    const previewContainer = document.getElementById('preview-container');
    const previewImg = document.getElementById('preview-img');
    const classifyBtn = document.getElementById('btn-classify-ai');
    const scannerBeam = document.getElementById('scanner-beam');
    const form = document.getElementById('form-report-issue');

    if (!dropzone || !fileInput) return;

    // Drag and drop events
    ['dragenter', 'dragover'].forEach(eventName => {
      dropzone.addEventListener(eventName, (e) => {
        e.preventDefault();
        dropzone.classList.add('dragover');
      });
    });

    ['dragleave', 'drop'].forEach(eventName => {
      dropzone.addEventListener(eventName, (e) => {
        e.preventDefault();
        dropzone.classList.remove('dragover');
      });
    });

    dropzone.addEventListener('drop', (e) => {
      const files = e.dataTransfer.files;
      if (files && files[0]) {
        this.handleImageSelected(files[0]);
      }
    });

    dropzone.addEventListener('click', () => fileInput.click());

    fileInput.addEventListener('change', (e) => {
      if (e.target.files && e.target.files[0]) {
        this.handleImageSelected(e.target.files[0]);
      }
    });

    // AI Classification Trigger
    if (classifyBtn) {
      classifyBtn.addEventListener('click', async () => {
        if (!this.selectedImageFile) {
          this.showToast('Please upload an issue photo first', 'error');
          return;
        }

        try {
          classifyBtn.disabled = true;
          classifyBtn.innerHTML = `
            <svg class="spinner" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="animation:spin 1s linear infinite;">
              <circle cx="12" cy="12" r="10" stroke-opacity="0.25"/>
              <path d="M12 2a10 10 0 0 1 10 10"/>
            </svg>
            Analyzing Visual Features...
          `;
          if (scannerBeam) scannerBeam.style.display = 'block';

          const textHint = document.getElementById('report-title')?.value || '';
          const result = await API.classifyImage(this.selectedImageFile, textHint);
          this.aiClassificationResult = result;

          // Display AI result box
          const resultBox = document.getElementById('ai-result-box');
          const predictedCat = document.getElementById('ai-predicted-category');
          const confFill = document.getElementById('ai-confidence-fill');
          const confText = document.getElementById('ai-confidence-text');
          const explanation = document.getElementById('ai-explanation');
          const modeBadge = document.getElementById('ai-mode-badge');

          if (resultBox) {
            resultBox.style.display = 'block';
            predictedCat.textContent = result.predicted_category;
            confFill.style.width = `${Math.round(result.confidence * 100)}%`;
            confText.textContent = `${Math.round(result.confidence * 100)}% Confidence`;
            explanation.textContent = result.explanation;

            if (modeBadge) {
              modeBadge.textContent = result.is_ai_vision ? 'Gemini 1.5 Vision AI' : 'Heuristic Rule Fallback';
              modeBadge.style.background = result.is_ai_vision ? '#06B6D4' : '#F59E0B';
            }

            // Auto-select category in dropdown
            const catSelect = document.getElementById('report-category');
            if (catSelect) catSelect.value = result.predicted_category;

            this.updatePriorityPreview();
            this.triggerDuplicateCheck();
          }

          this.showToast(`AI Suggestion: ${result.predicted_category}`, 'success');
        } catch (err) {
          console.error('Classification error:', err);
          this.showToast('AI analysis encountered an issue: ' + err.message, 'error');
        } finally {
          classifyBtn.disabled = false;
          classifyBtn.innerHTML = `
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/>
            </svg>
            Re-Analyze with AI Vision
          `;
          if (scannerBeam) scannerBeam.style.display = 'none';
        }
      });
    }

    // Geolocation Button
    const btnGeolocate = document.getElementById('btn-geolocate');
    if (btnGeolocate) {
      btnGeolocate.addEventListener('click', () => {
        if (!navigator.geolocation) {
          this.showToast('Browser geolocation is not supported on this device.', 'error');
          return;
        }

        btnGeolocate.textContent = 'Locating...';
        navigator.geolocation.getCurrentPosition(
          (pos) => {
            const lat = pos.coords.latitude;
            const lng = pos.coords.longitude;
            MapModule.setPickerLocation(lat, lng);
            this.onPickerLocationChanged(lat, lng);
            btnGeolocate.innerHTML = '📍 Use My Location';
            this.showToast('Current GPS coordinates located!', 'success');
          },
          (err) => {
            btnGeolocate.innerHTML = '📍 Use My Location';
            this.showToast('Location permission denied or unavailable. Please click location on map.', 'info');
          },
          { enableHighAccuracy: true, timeout: 8000 }
        );
      });
    }

    // Dynamic Live Priority & Duplicate Triggers
    const titleInput = document.getElementById('report-title');
    const descInput = document.getElementById('report-description');
    const catSelect = document.getElementById('report-category');

    [titleInput, descInput, catSelect].forEach(el => {
      if (el) {
        el.addEventListener('input', () => {
          this.updatePriorityPreview();
          this.debounceDuplicateCheck();
        });
      }
    });

    // Form Submission
    if (form) {
      form.addEventListener('submit', async (e) => {
        e.preventDefault();
        await this.submitReportForm();
      });
    }
  },

  handleImageSelected(file) {
    this.selectedImageFile = file;
    const previewContainer = document.getElementById('preview-container');
    const previewImg = document.getElementById('preview-img');

    if (previewImg && previewContainer) {
      const reader = new FileReader();
      reader.onload = (e) => {
        previewImg.src = e.target.result;
        previewContainer.style.display = 'block';
      };
      reader.readAsDataURL(file);
    }
    this.updatePriorityPreview();
  },

  async onPickerLocationChanged(lat, lng) {
    this.pickerCoords = { lat, lng };
    document.getElementById('report-lat').value = lat.toFixed(6);
    document.getElementById('report-lng').value = lng.toFixed(6);

    // Reverse Geocode
    try {
      const res = await API.reverseGeocode(lat, lng);
      const addrInput = document.getElementById('report-address');
      if (addrInput && res.address) {
        addrInput.value = res.address;
      }
    } catch (_) {}

    this.triggerDuplicateCheck();
  },

  // Priority Preview Logic in UI
  updatePriorityPreview() {
    const title = document.getElementById('report-title')?.value || '';
    const desc = document.getElementById('report-description')?.value || '';
    const cat = document.getElementById('report-category')?.value || 'Roads & Potholes';
    const hasImg = !!this.selectedImageFile;

    // Client-side quick calculation matching backend algorithm
    const text = `${title} ${desc}`.lower ? `${title} ${desc}`.toLowerCase() : '';
    let score = 20;

    if (cat === 'Traffic & Signage') score = 35;
    else if (cat === 'Roads & Potholes') score = 30;
    else if (cat === 'Water & Drainage') score = 28;
    else if (cat === 'Street Lighting') score = 24;

    if (/accident|emergency|sparking|exposed wire|burst pipe|flooding|sinkhole/.test(text)) {
      score += 30;
    } else if (/hospital|school|children|blocking road|highway|sewage/.test(text)) {
      score += 20;
    }

    if (hasImg) score += 10;
    if (desc.split(/\s+/).length > 20) score += 8;

    let tier = 'Low';
    let badgeClass = 'badge-low';
    if (score >= 75) { tier = 'Critical'; badgeClass = 'badge-critical'; }
    else if (score >= 55) { tier = 'High'; badgeClass = 'badge-high'; }
    else if (score >= 35) { tier = 'Medium'; badgeClass = 'badge-medium'; }

    const pill = document.getElementById('priority-preview-pill');
    const scoreVal = document.getElementById('priority-preview-score');
    if (pill && scoreVal) {
      pill.textContent = tier;
      pill.className = `badge ${badgeClass}`;
      scoreVal.textContent = `Estimated Urgency: ~${Math.min(score, 98)}/100`;
    }
  },

  // Duplicate Check with Debounce
  duplicateTimeout: null,
  debounceDuplicateCheck() {
    clearTimeout(this.duplicateTimeout);
    this.duplicateTimeout = setTimeout(() => {
      this.triggerDuplicateCheck();
    }, 600);
  },

  async triggerDuplicateCheck() {
    const cat = document.getElementById('report-category')?.value;
    const desc = document.getElementById('report-description')?.value;
    const lat = this.pickerCoords.lat;
    const lng = this.pickerCoords.lng;

    if (!desc || desc.length < 8) return;

    try {
      const res = await API.checkDuplicates({
        category: cat,
        description: desc,
        latitude: lat,
        longitude: lng
      });

      const alertEl = document.getElementById('duplicate-alert-banner');
      const listEl = document.getElementById('duplicate-items-list');

      if (res.has_duplicates && alertEl && listEl) {
        alertEl.style.display = 'block';
        listEl.innerHTML = res.duplicates.map(d => `
          <div class="duplicate-item-card">
            <div>
              <strong style="color:#FFF;">${this.escapeHtml(d.title)}</strong>
              <div style="font-size:11px; color:#94A3B8;">📍 ${d.distance_meters.toFixed(0)}m away • ${d.similarity_score * 100}% similarity</div>
            </div>
            <button type="button" class="btn-secondary" style="padding:4px 8px; font-size:11px;" onclick="window.viewReportDetail('${d.id}')">
              View & Upvote
            </button>
          </div>
        `).join('');
      } else if (alertEl) {
        alertEl.style.display = 'none';
      }
    } catch (_) {}
  },

  // Submit Complaint Form
  async submitReportForm() {
    const btn = document.getElementById('btn-submit-form');
    const form = document.getElementById('form-report-issue');

    const title = document.getElementById('report-title').value.trim();
    const description = document.getElementById('report-description').value.trim();
    const category = document.getElementById('report-category').value;
    const address = document.getElementById('report-address').value.trim();
    const reporterName = document.getElementById('report-name').value.trim() || 'Anonymous Citizen';
    const reporterContact = document.getElementById('report-contact').value.trim();

    if (!title || !description || !address) {
      this.showToast('Please fill all mandatory fields.', 'error');
      return;
    }

    const formData = new FormData();
    formData.append('title', title);
    formData.append('description', description);
    formData.append('category', category);
    formData.append('latitude', this.pickerCoords.lat);
    formData.append('longitude', this.pickerCoords.lng);
    formData.append('address', address);
    formData.append('reporter_name', reporterName);
    if (reporterContact) formData.append('reporter_contact', reporterContact);

    if (this.selectedImageFile) {
      formData.append('image', this.selectedImageFile);
    }

    if (this.aiClassificationResult) {
      formData.append('ai_classified', 'true');
      formData.append('ai_confidence', this.aiClassificationResult.confidence);
      formData.append('ai_notes', this.aiClassificationResult.explanation);
    }

    try {
      btn.disabled = true;
      btn.textContent = 'Registering Complaint...';

      const created = await API.createReport(formData);

      this.showToast(`Complaint registered successfully! ID: ${created.id}`, 'success');

      // Reset Form
      form.reset();
      this.selectedImageFile = null;
      this.aiClassificationResult = null;
      document.getElementById('preview-container').style.display = 'none';
      document.getElementById('ai-result-box').style.display = 'none';
      document.getElementById('duplicate-alert-banner').style.display = 'none';

      // Switch to All Reports and view created report
      this.navigate('reports');
    } catch (err) {
      console.error('Submission failed:', err);
      this.showToast('Failed to submit report: ' + err.message, 'error');
    } finally {
      btn.disabled = false;
      btn.textContent = 'Submit Civic Complaint';
    }
  },

  // =========================================================================
  // All Reports List Logic
  // =========================================================================
  bindFilters() {
    const searchInput = document.getElementById('filter-search');
    const catFilter = document.getElementById('filter-category');
    const statusFilter = document.getElementById('filter-status');
    const priorityFilter = document.getElementById('filter-priority');
    const sortFilter = document.getElementById('filter-sort');

    let debounceTimeout = null;
    if (searchInput) {
      searchInput.addEventListener('input', (e) => {
        clearTimeout(debounceTimeout);
        debounceTimeout = setTimeout(() => {
          this.reportsState.search = e.target.value.trim();
          this.reportsState.page = 1;
          this.loadReportsList();
        }, 400);
      });
    }

    [catFilter, statusFilter, priorityFilter, sortFilter].forEach(el => {
      if (el) {
        el.addEventListener('change', () => {
          this.reportsState.category = catFilter.value;
          this.reportsState.status = statusFilter.value;
          this.reportsState.priority = priorityFilter.value;
          
          if (sortFilter.value === 'priority') {
            this.reportsState.sort_by = 'priority_score';
          } else if (sortFilter.value === 'upvotes') {
            this.reportsState.sort_by = 'upvotes';
          } else {
            this.reportsState.sort_by = 'created_at';
          }

          this.reportsState.page = 1;
          this.loadReportsList();
        });
      }
    });

    // Pagination buttons
    const prevBtn = document.getElementById('btn-prev-page');
    const nextBtn = document.getElementById('btn-next-page');

    if (prevBtn) {
      prevBtn.addEventListener('click', () => {
        if (this.reportsState.page > 1) {
          this.reportsState.page--;
          this.loadReportsList();
        }
      });
    }

    if (nextBtn) {
      nextBtn.addEventListener('click', () => {
        this.reportsState.page++;
        this.loadReportsList();
      });
    }
  },

  async loadReportsList() {
    const grid = document.getElementById('reports-grid');
    if (!grid) return;

    grid.innerHTML = '<div style="grid-column:1/-1; text-align:center; padding:40px; color:#94A3B8;">Loading complaints ledger...</div>';

    try {
      const data = await API.getReports(this.reportsState);

      // Update Pagination UI
      const prevBtn = document.getElementById('btn-prev-page');
      const nextBtn = document.getElementById('btn-next-page');
      const pageInfo = document.getElementById('page-info-label');

      if (prevBtn) prevBtn.disabled = data.page <= 1;
      if (nextBtn) nextBtn.disabled = data.page >= data.total_pages;
      if (pageInfo) pageInfo.textContent = `Page ${data.page} of ${data.total_pages} (${data.total} total)`;

      if (!data.reports || data.reports.length === 0) {
        grid.innerHTML = '<div style="grid-column:1/-1; text-align:center; padding:40px; color:#64748B;">No civic issues match your current filters.</div>';
        return;
      }

      grid.innerHTML = data.reports.map(r => `
        <div class="report-card">
          <div class="report-card-media">
            <img class="report-card-img" src="${r.image_url || '/uploads/sample_pothole.jpg'}" alt="${r.category}" />
            <div class="media-badges">
              <span class="badge badge-${r.priority.toLowerCase()}">${r.priority}</span>
              <span class="badge badge-status">${r.status}</span>
            </div>
          </div>
          <div class="report-card-body">
            <div class="card-category">${this.escapeHtml(r.category)}</div>
            <h4 class="card-title">${this.escapeHtml(r.title)}</h4>
            <p class="card-desc">${this.escapeHtml(r.description)}</p>
            <div class="card-address">📍 ${this.escapeHtml(r.address)}</div>
            <div class="card-footer">
              <button class="btn-upvote" onclick="window.upvoteReport('${r.id}', event)">
                👍 <span id="upvote-count-${r.id}">${r.upvotes}</span> Upvotes
              </button>
              <button class="btn-view-detail" onclick="window.viewReportDetail('${r.id}')">
                Inspect Details
              </button>
            </div>
          </div>
        </div>
      `).join('');
    } catch (err) {
      console.error('Failed to load reports:', err);
      grid.innerHTML = `<div style="grid-column:1/-1; color:#EF4444; text-align:center; padding:40px;">Failed to load reports: ${err.message}</div>`;
    }
  },

  // =========================================================================
  // Full Map View Logic
  // =========================================================================
  async loadMapReports() {
    try {
      const reports = await API.getMapReports();
      MapModule.renderMapReports(reports);

      const listPanel = document.getElementById('map-sidebar-reports');
      if (!listPanel) return;

      listPanel.innerHTML = reports.map(r => `
        <div class="feed-item" onclick="MapModule.focusReport(${r.latitude}, ${r.longitude})">
          <div class="feed-info">
            <div class="feed-title">${this.escapeHtml(r.title)}</div>
            <div class="feed-meta">
              <span class="badge" style="background:${r.priority_color}22; color:${r.priority_color}; border:1px solid ${r.priority_color}44;">${r.priority}</span>
              <span class="badge badge-status">${r.status}</span>
            </div>
          </div>
        </div>
      `).join('');
    } catch (err) {
      console.error('Failed to load map data:', err);
    }
  },

  // =========================================================================
  // Analytics View Logic
  // =========================================================================
  async loadAnalyticsData() {
    try {
      const analytics = await API.getAnalytics();
      ChartsModule.renderAllCharts(analytics);

      // Bind Export Buttons
      const btnExportCSV = document.getElementById('btn-export-csv');
      const btnExportJSON = document.getElementById('btn-export-json');

      if (btnExportCSV) {
        btnExportCSV.onclick = () => this.exportAnalyticsCSV(analytics);
      }
      if (btnExportJSON) {
        btnExportJSON.onclick = () => this.exportAnalyticsJSON(analytics);
      }
    } catch (err) {
      console.error('Failed to load analytics:', err);
    }
  },

  exportAnalyticsCSV(data) {
    let csv = "Category,Reports Count\n";
    for (const [cat, count] of Object.entries(data.category_breakdown || {})) {
      csv += `"${cat}",${count}\n`;
    }
    csv += "\nStatus,Reports Count\n";
    for (const [st, count] of Object.entries(data.status_breakdown || {})) {
      csv += `"${st}",${count}\n`;
    }
    
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `CivicPulse_Analytics_${new Date().toISOString().slice(0, 10)}.csv`;
    a.click();
    this.showToast('Analytics CSV exported successfully.', 'success');
  },

  exportAnalyticsJSON(data) {
    const jsonStr = JSON.stringify(data, null, 2);
    const blob = new Blob([jsonStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `CivicPulse_Analytics_${new Date().toISOString().slice(0, 10)}.json`;
    a.click();
    this.showToast('Analytics JSON exported successfully.', 'success');
  },

  // =========================================================================
  // Admin Portal & Authentication Logic
  // =========================================================================
  checkAdminSession() {
    const isLogged = API.isLoggedIn();
    const adminBtn = document.getElementById('sidebar-admin-login-btn');
    if (adminBtn) {
      adminBtn.textContent = isLogged ? '👤 Admin Dashboard' : '🔒 Admin Portal Login';
    }
  },

  bindAdminActions() {
    const loginForm = document.getElementById('form-admin-login');
    const logoutBtn = document.getElementById('btn-admin-logout');

    if (loginForm) {
      loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const user = document.getElementById('admin-user').value.trim();
        const pass = document.getElementById('admin-pass').value.trim();

        try {
          await API.adminLogin(user, pass);
          this.showToast('Admin session authenticated successfully!', 'success');
          this.checkAdminSession();
          this.refreshAdminView();
        } catch (err) {
          this.showToast('Admin login failed: ' + err.message, 'error');
        }
      });
    }

    if (logoutBtn) {
      logoutBtn.addEventListener('click', () => {
        API.clearToken();
        this.checkAdminSession();
        this.refreshAdminView();
        this.showToast('Admin logged out.', 'info');
      });
    }

    // Resolve Proof Form
    const proofForm = document.getElementById('form-resolve-proof');
    if (proofForm) {
      proofForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const reportId = document.getElementById('resolve-report-id').value;
        const remarks = document.getElementById('resolve-remarks').value;
        const fileInput = document.getElementById('resolve-proof-image');
        const proofFile = fileInput.files ? fileInput.files[0] : null;

        try {
          await API.resolveWithProof(reportId, remarks, proofFile);
          this.showToast(`Ticket ${reportId} marked Resolved with proof!`, 'success');
          this.closeModals();
          this.refreshAdminView();
        } catch (err) {
          this.showToast('Failed to resolve: ' + err.message, 'error');
        }
      });
    }
  },

  async refreshAdminView() {
    const loginContainer = document.getElementById('admin-login-container');
    const panelContainer = document.getElementById('admin-panel-container');

    if (!API.isLoggedIn()) {
      if (loginContainer) loginContainer.style.display = 'block';
      if (panelContainer) panelContainer.style.display = 'none';
      return;
    }

    if (loginContainer) loginContainer.style.display = 'none';
    if (panelContainer) panelContainer.style.display = 'block';

    const user = API.getUser();
    const nameEl = document.getElementById('admin-user-display-name');
    if (nameEl && user) nameEl.textContent = `${user.full_name} (${user.role})`;

    // Load reports into management table
    const tbody = document.getElementById('admin-table-body');
    if (!tbody) return;

    tbody.innerHTML = '<tr><td colspan="7" style="text-align:center; padding:30px;">Loading administration ledger...</td></tr>';

    try {
      const data = await API.getReports({ page: 1, limit: 50, sort_by: 'created_at', sort_order: 'desc' });
      
      tbody.innerHTML = data.reports.map(r => `
        <tr>
          <td><strong style="color:#38BDF8;">${r.id}</strong></td>
          <td>
            <div style="font-weight:600; color:#FFF; max-width:240px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">
              ${this.escapeHtml(r.title)}
            </div>
            <div style="font-size:11px; color:#64748B;">📍 ${this.escapeHtml(r.address.split(',')[0])}</div>
          </td>
          <td><span style="font-size:12px; font-weight:600;">${r.category}</span></td>
          <td><span class="badge badge-${r.priority.toLowerCase()}">${r.priority}</span></td>
          <td>
            <select class="form-select" style="padding:6px 10px; font-size:12px;" onchange="window.adminChangeStatus('${r.id}', this.value)">
              <option value="Reported" ${r.status === 'Reported' ? 'selected' : ''}>Reported</option>
              <option value="Acknowledged" ${r.status === 'Acknowledged' ? 'selected' : ''}>Acknowledged</option>
              <option value="In Progress" ${r.status === 'In Progress' ? 'selected' : ''}>In Progress</option>
              <option value="Resolved" ${r.status === 'Resolved' ? 'selected' : ''}>Resolved</option>
            </select>
          </td>
          <td>${new Date(r.created_at).toLocaleDateString()}</td>
          <td>
            <button class="btn-secondary" style="padding:6px 10px; font-size:11px;" onclick="window.openResolveModal('${r.id}')">
              Resolution Proof
            </button>
          </td>
        </tr>
      `).join('');
    } catch (err) {
      console.error('Failed to load admin reports:', err);
    }
  },

  // Modal Closures
  closeModals() {
    document.querySelectorAll('.modal-overlay').forEach(m => m.classList.remove('open'));
  },

  // Toast Notification System
  showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    let icon = 'ℹ️';
    if (type === 'success') icon = '✅';
    if (type === 'error') icon = '⚠️';

    toast.innerHTML = `<span>${icon}</span> <span>${this.escapeHtml(message)}</span>`;
    container.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(10px)';
      toast.style.transition = 'all 0.3s ease';
      setTimeout(() => toast.remove(), 300);
    }, 4000);
  },

  escapeHtml(str) {
    if (!str) return '';
    return str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }
};

// Global Handlers accessible from inline HTML
window.viewReportDetail = async (reportId) => {
  try {
    const report = await API.getReport(reportId);
    const modal = document.getElementById('modal-report-detail');
    if (!modal) return;

    document.getElementById('modal-detail-id').textContent = report.id;
    document.getElementById('modal-detail-title').textContent = report.title;
    document.getElementById('modal-detail-desc').textContent = report.description;
    document.getElementById('modal-detail-cat').textContent = report.category;
    document.getElementById('modal-detail-address').textContent = report.address;
    document.getElementById('modal-detail-reporter').textContent = `${report.reporter_name || 'Anonymous Citizen'}`;
    document.getElementById('modal-detail-score').textContent = `${report.priority_score}/100`;

    const priBadge = document.getElementById('modal-detail-priority');
    priBadge.textContent = report.priority;
    priBadge.className = `badge badge-${report.priority.toLowerCase()}`;

    const stBadge = document.getElementById('modal-detail-status');
    stBadge.textContent = report.status;

    // Explainable Priority Breakdown
    const reasonEl = document.getElementById('modal-detail-reason');
    if (reasonEl) reasonEl.textContent = report.priority_reason || 'Standard category base evaluation.';

    // Image
    const imgEl = document.getElementById('modal-detail-img');
    if (imgEl) {
      imgEl.src = report.image_url || '/uploads/sample_pothole.jpg';
    }

    // Status Timeline
    const timelineEl = document.getElementById('modal-timeline-container');
    if (timelineEl) {
      if (report.status_history && report.status_history.length > 0) {
        timelineEl.innerHTML = report.status_history.map(s => `
          <div class="timeline-step ${s.new_status === 'Resolved' ? 'completed' : ''}">
            <div class="step-status">${s.new_status}</div>
            <div class="step-time">${new Date(s.created_at).toLocaleString()} by ${s.changed_by}</div>
            <div class="step-remarks">${App.escapeHtml(s.remarks || 'No remarks')}</div>
          </div>
        `).join('');
      } else {
        timelineEl.innerHTML = '<div style="color:#64748B;">No timeline updates recorded.</div>';
      }
    }

    modal.classList.add('open');

    // Render Mini Location Map
    if (report.latitude && report.longitude) {
      setTimeout(() => {
        MapModule.renderDetailMap('modal-detail-map', report.latitude, report.longitude, report.title);
      }, 150);
    }
  } catch (err) {
    App.showToast('Could not load report details: ' + err.message, 'error');
  }
};

window.upvoteReport = async (reportId, e) => {
  if (e) e.stopPropagation();
  try {
    const updated = await API.upvoteReport(reportId);
    const counter = document.getElementById(`upvote-count-${reportId}`);
    if (counter) counter.textContent = updated.upvotes;
    App.showToast(`Upvoted ticket ${reportId}! (Total: ${updated.upvotes})`, 'success');
  } catch (err) {
    App.showToast('Failed to upvote: ' + err.message, 'error');
  }
};

window.adminChangeStatus = async (reportId, newStatus) => {
  try {
    const remarks = prompt(`Enter administrative note for transitioning ${reportId} to ${newStatus}:`, `Municipal review update: ${newStatus}`);
    if (remarks === null) return;

    await API.updateReportStatus(reportId, newStatus, remarks);
    App.showToast(`Status updated to ${newStatus}`, 'success');
    App.refreshAdminView();
  } catch (err) {
    App.showToast('Failed to update status: ' + err.message, 'error');
    App.refreshAdminView();
  }
};

window.openResolveModal = (reportId) => {
  const modal = document.getElementById('modal-resolve-proof');
  if (modal) {
    document.getElementById('resolve-report-id').value = reportId;
    modal.classList.add('open');
  }
};
