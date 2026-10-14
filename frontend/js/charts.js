/**
 * CivicPulse AI - Chart.js Analytics Module
 * Renders interactive visual graphs for category distributions,
 * resolution pipelines, and 7-day municipal velocity trends.
 */

const ChartsModule = {
  instances: {},

  // Color constants matching the design system
  palette: {
    cyan: '#06B6D4',
    blue: '#3B82F6',
    indigo: '#6366F1',
    violet: '#8B5CF6',
    rose: '#F43F5E',
    amber: '#F59E0B',
    emerald: '#10B981',
    sky: '#38BDF8',
    slate: '#64748B'
  },

  renderAllCharts(analyticsData) {
    if (!analyticsData) return;
    this.renderCategoryChart('chart-categories', analyticsData.category_breakdown);
    this.renderStatusChart('chart-status', analyticsData.status_breakdown);
    this.renderTrendsChart('chart-trends', analyticsData.daily_trends);
    this.renderPriorityChart('chart-priority', analyticsData.priority_breakdown);
  },

  // 1. Category Distribution (Doughnut Chart)
  renderCategoryChart(canvasId, categoryData) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;

    if (this.instances[canvasId]) {
      this.instances[canvasId].destroy();
    }

    const labels = Object.keys(categoryData || {});
    const dataValues = Object.values(categoryData || {});
    const colors = [
      '#EF4444', '#F97316', '#F59E0B', '#10B981', 
      '#06B6D4', '#3B82F6', '#8B5CF6', '#EC4899', '#64748B'
    ];

    this.instances[canvasId] = new Chart(canvas, {
      type: 'doughnut',
      data: {
        labels: labels,
        datasets: [{
          data: dataValues,
          backgroundColor: colors.slice(0, labels.length),
          borderColor: '#151D2F',
          borderWidth: 2,
          hoverOffset: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'bottom',
            labels: {
              color: '#94A3B8',
              font: { family: 'Inter', size: 11 },
              boxWidth: 12,
              padding: 12
            }
          },
          tooltip: {
            backgroundColor: '#0F172A',
            titleColor: '#F8FAFC',
            bodyColor: '#94A3B8',
            borderColor: 'rgba(255,255,255,0.1)',
            borderWidth: 1,
            padding: 10
          }
        },
        cutout: '68%'
      }
    });
  },

  // 2. Status Distribution (Bar Chart)
  renderStatusChart(canvasId, statusData) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;

    if (this.instances[canvasId]) {
      this.instances[canvasId].destroy();
    }

    const labels = Object.keys(statusData || {});
    const dataValues = Object.values(statusData || {});
    const colors = ['#818CF8', '#38BDF8', '#FBBF24', '#34D399'];

    this.instances[canvasId] = new Chart(canvas, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [{
          label: 'Total Reports',
          data: dataValues,
          backgroundColor: colors,
          borderRadius: 6,
          borderWidth: 0
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false }
        },
        scales: {
          x: {
            grid: { display: false },
            ticks: { color: '#94A3B8', font: { family: 'Inter', size: 11 } }
          },
          y: {
            beginAtZero: true,
            grid: { color: 'rgba(255, 255, 255, 0.05)' },
            ticks: { stepSize: 1, color: '#94A3B8', font: { family: 'Inter', size: 11 } }
          }
        }
      }
    });
  },

  // 3. 7-Day Resolution & Intake Trends (Area Line Chart)
  renderTrendsChart(canvasId, trendsData) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;

    if (this.instances[canvasId]) {
      this.instances[canvasId].destroy();
    }

    const labels = (trendsData || []).map(t => t.date);
    const reportedData = (trendsData || []).map(t => t.reported);
    const resolvedData = (trendsData || []).map(t => t.resolved);

    this.instances[canvasId] = new Chart(canvas, {
      type: 'line',
      data: {
        labels: labels,
        datasets: [
          {
            label: 'New Complaints',
            data: reportedData,
            borderColor: '#06B6D4',
            backgroundColor: 'rgba(6, 182, 212, 0.12)',
            fill: true,
            tension: 0.35,
            pointBackgroundColor: '#06B6D4',
            pointRadius: 4
          },
          {
            label: 'Resolved Issues',
            data: resolvedData,
            borderColor: '#10B981',
            backgroundColor: 'rgba(16, 185, 129, 0.12)',
            fill: true,
            tension: 0.35,
            pointBackgroundColor: '#10B981',
            pointRadius: 4
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'top',
            labels: { color: '#94A3B8', font: { family: 'Inter', size: 12 }, boxWidth: 12 }
          }
        },
        scales: {
          x: {
            grid: { color: 'rgba(255, 255, 255, 0.03)' },
            ticks: { color: '#94A3B8', font: { family: 'Inter', size: 11 } }
          },
          y: {
            beginAtZero: true,
            grid: { color: 'rgba(255, 255, 255, 0.05)' },
            ticks: { stepSize: 1, color: '#94A3B8', font: { family: 'Inter', size: 11 } }
          }
        }
      }
    });
  },

  // 4. Priority Breakdown
  renderPriorityChart(canvasId, priorityData) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;

    if (this.instances[canvasId]) {
      this.instances[canvasId].destroy();
    }

    const labels = ['Low', 'Medium', 'High', 'Critical'];
    const dataValues = labels.map(l => (priorityData && priorityData[l]) || 0);
    const colors = ['#10B981', '#F59E0B', '#F97316', '#EF4444'];

    this.instances[canvasId] = new Chart(canvas, {
      type: 'polarArea',
      data: {
        labels: labels,
        datasets: [{
          data: dataValues,
          backgroundColor: colors.map(c => `${c}88`),
          borderColor: colors,
          borderWidth: 1.5
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'bottom',
            labels: { color: '#94A3B8', font: { family: 'Inter', size: 11 }, boxWidth: 12 }
          }
        },
        scales: {
          r: {
            grid: { color: 'rgba(255, 255, 255, 0.05)' },
            ticks: { display: false }
          }
        }
      }
    });
  }
};
