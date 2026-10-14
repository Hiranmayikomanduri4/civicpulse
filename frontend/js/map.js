/**
 * CivicPulse AI - Leaflet & OpenStreetMap Module
 * Handles full-screen interactive civic map, custom colored SVG markers,
 * click-to-pin location picker, and reverse-geocoding.
 */

const MapModule = {
  fullMap: null,
  pickerMap: null,
  miniDetailMap: null,
  pickerMarker: null,
  markersLayer: null,
  
  // Default center coordinates (New Delhi / Configurable city center)
  defaultCoords: [28.6139, 77.2090],
  defaultZoom: 13,

  // Initialize Map on Report Form for Citizen Location Picking
  initPickerMap(containerId, onLocationSelected) {
    if (this.pickerMap) {
      this.pickerMap.invalidateSize();
      return;
    }

    const container = document.getElementById(containerId);
    if (!container) return;

    this.pickerMap = L.map(containerId, {
      zoomControl: true,
      attributionControl: true
    }).setView(this.defaultCoords, this.defaultZoom);

    // Standard OpenStreetMap tiles (free, public, zero API key required)
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener noreferrer">OpenStreetMap</a> contributors'
    }).addTo(this.pickerMap);

    // Custom Draggable Pin
    const pinIcon = L.divIcon({
      className: 'picker-custom-pin',
      html: `
        <div style="background: #06B6D4; width: 28px; height: 28px; border-radius: 50% 50% 50% 0; transform: rotate(-45deg); border: 2px solid #FFFFFF; box-shadow: 0 0 10px rgba(6,182,212,0.8); display:flex; align-items:center; justify-content:center;">
          <div style="width: 8px; height: 8px; background:#FFFFFF; border-radius:50%; transform: rotate(45deg);"></div>
        </div>
      `,
      iconSize: [28, 28],
      iconAnchor: [14, 28]
    });

    this.pickerMarker = L.marker(this.defaultCoords, {
      draggable: true,
      icon: pinIcon
    }).addTo(this.pickerMap);

    // Initial trigger
    if (onLocationSelected) {
      onLocationSelected(this.defaultCoords[0], this.defaultCoords[1]);
    }

    // Drag event
    this.pickerMarker.on('dragend', (e) => {
      const pos = e.target.getLatLng();
      if (onLocationSelected) {
        onLocationSelected(pos.lat, pos.lng);
      }
    });

    // Click map to reposition
    this.pickerMap.on('click', (e) => {
      this.pickerMarker.setLatLng(e.latlng);
      if (onLocationSelected) {
        onLocationSelected(e.latlng.lat, e.latlng.lng);
      }
    });
  },

  setPickerLocation(lat, lng) {
    if (this.pickerMap && this.pickerMarker) {
      const target = [lat, lng];
      this.pickerMarker.setLatLng(target);
      this.pickerMap.panTo(target);
    }
  },

  // Initialize Full-Screen Map on Map View
  initFullMap(containerId, onMarkerClicked) {
    if (this.fullMap) {
      this.fullMap.invalidateSize();
      return;
    }

    const container = document.getElementById(containerId);
    if (!container) return;

    this.fullMap = L.map(containerId, {
      zoomControl: true,
      attributionControl: true
    }).setView(this.defaultCoords, 12);

    // Standard OpenStreetMap tiles (free, public, zero API key required)
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener noreferrer">OpenStreetMap</a> contributors'
    }).addTo(this.fullMap);

    this.markersLayer = L.layerGroup().addTo(this.fullMap);
  },

  // Render Markers on Full Map
  renderMapReports(reports, onSelectReport) {
    if (!this.fullMap || !this.markersLayer) return;

    this.markersLayer.clearLayers();
    if (!reports || reports.length === 0) return;

    const bounds = [];

    reports.forEach((item) => {
      if (!item.latitude || !item.longitude) return;

      const pos = [item.latitude, item.longitude];
      bounds.push(pos);

      // Create Custom Colored SVG Pulse Marker based on Priority
      const color = item.priority_color || '#3B82F6';
      const markerIcon = L.divIcon({
        className: 'custom-leaflet-marker',
        html: `
          <div style="background: ${color}; width: 28px; height: 28px; border-radius: 50%; display: flex; align-items: center; justify-content: center; box-shadow: 0 0 12px ${color}; border: 2px solid #FFFFFF;">
            <span style="font-size: 11px; font-weight: 800; color: #FFFFFF;">!</span>
          </div>
        `,
        iconSize: [28, 28],
        iconAnchor: [14, 14]
      });

      const marker = L.marker(pos, { icon: markerIcon }).addTo(this.markersLayer);

      // Rich Interactive Popup
      const popupHtml = `
        <div style="font-family: 'Inter', sans-serif; min-width: 200px; max-width: 250px; color: #1E293B;">
          ${item.image_url ? `<img src="${item.image_url}" style="width:100%; height:100px; object-fit:cover; border-radius:6px; margin-bottom:8px;" />` : ''}
          <div style="font-size:10px; font-weight:700; color:${color}; text-transform:uppercase;">${item.category}</div>
          <div style="font-size:13px; font-weight:700; margin:3px 0 6px 0; line-height:1.2;">${item.title}</div>
          <div style="display:flex; justify-content:space-between; align-items:center; font-size:11px; margin-bottom:8px;">
            <span style="background:${item.priority_color}22; color:${item.priority_color}; padding:2px 6px; border-radius:4px; font-weight:600;">${item.priority}</span>
            <span style="background:#F1F5F9; color:#475569; padding:2px 6px; border-radius:4px; font-weight:600;">${item.status}</span>
          </div>
          <div style="font-size:11px; color:#64748B; margin-bottom:8px; line-height:1.3;">📍 ${item.address}</div>
          <button onclick="window.viewReportDetail('${item.id}')" style="width:100%; padding:6px; border-radius:4px; background:#3B82F6; color:#FFF; border:none; font-size:11px; font-weight:600; cursor:pointer;">
            Inspect Full Report
          </button>
        </div>
      `;

      marker.bindPopup(popupHtml);
    });

    // Fit map bounds to show all markers
    if (bounds.length > 0) {
      this.fullMap.fitBounds(bounds, { padding: [50, 50], maxZoom: 15 });
    }
  },

  // Focus Map to Specific Location
  focusReport(lat, lng) {
    if (this.fullMap) {
      this.fullMap.setView([lat, lng], 16, { animate: true });
    }
  },

  // Render Mini Detail Map in Report Inspector Modal
  renderDetailMap(containerId, lat, lng, title) {
    if (this.miniDetailMap) {
      this.miniDetailMap.remove();
      this.miniDetailMap = null;
    }
    const container = document.getElementById(containerId);
    if (!container || !lat || !lng) return;

    this.miniDetailMap = L.map(containerId, {
      zoomControl: false,
      attributionControl: true
    }).setView([lat, lng], 15);

    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener noreferrer">OpenStreetMap</a> contributors'
    }).addTo(this.miniDetailMap);

    L.marker([lat, lng]).addTo(this.miniDetailMap);

    setTimeout(() => {
      if (this.miniDetailMap) this.miniDetailMap.invalidateSize();
    }, 200);
  }
};
