<template>
  <div class="admin-dashboard text-white">
    <nav class="custom-navbar">
      <div class="navbar-logo">
        <span class="quick">Quick</span><span class="park">Park</span>
      </div>
      <ul class="navbar-menu">
        <li><a href="/admin/dashboard" class="nav-link">Home</a></li>
        <li><a href="/admin/users/show" class="nav-link">Users</a></li>
        <li><a href="/admin/add/parkinglot" class="nav-link">Parking Lots</a></li>
        <li><a href="/admin/summary" class="nav-link active">Summary</a></li>
      </ul>
      <div class="navbar-profile">
        <li class="nav-item dropdown">
          <a
            class="nav-link dropdown-toggle"
            href="#"
            role="button"
            data-bs-toggle="dropdown"
            aria-expanded="false"
          >
            <i class="bi bi-person-circle me-1"></i> Profile
          </a>
          <ul class="dropdown-menu dropdown-menu-end">
            <li><a class="dropdown-item" @click="$router.push('/admin/edit-profile')" href="#">Edit Profile</a></li>
            <li><hr class="dropdown-divider" /></li>
            <li><a class="dropdown-item text-danger" @click="logout" href="#">Logout</a></li>
          </ul>
        </li>
      </div>
    </nav>

    <div class="container py-4">
      <h2 class="mb-4" style="text-align: center;">Summary</h2>

      <div class="row">
        <div class="col-md-6">
          <div class="chart-container">
            <h4 class="chart-title">Revenue by Parking Lot</h4>
            <canvas id="revenue-chart"></canvas>
          </div>
        </div>
        <div class="col-md-6">
          <div class="chart-container">
            <h4 class="chart-title">Slot Availability</h4>
            <canvas id="slots-chart"></canvas>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../../api/api.js';
import Chart from 'chart.js/auto';
import toastr from 'toastr';

export default {
  name: 'AdminSummary',
  data() {
    return {
      revenueChart: null,
      slotsChart: null,
    };
  },
  methods: {
    logout() {
      localStorage.removeItem('access_token');
      localStorage.removeItem('user_role');
      this.$router.push('/login');
    },
    async fetchRevenueData() {
      try {
        const response = await api.get('/admin/summary/revenue');
        const data = response.data;

        const chartData = {
          labels: data.map(item => item.location),
          datasets: [{
            label: 'Revenue',
            data: data.map(item => item.revenue),
            backgroundColor: [
              'rgba(255, 99, 132, 0.7)',
              'rgba(54, 162, 235, 0.7)',
              'rgba(255, 206, 86, 0.7)',
              'rgba(75, 192, 192, 0.7)',
              'rgba(153, 102, 255, 0.7)',
              'rgba(255, 159, 64, 0.7)'
            ],
          }]
        };

        this.renderRevenueChart(chartData);
      } catch (error) {
        toastr.error('Failed to fetch revenue data');
        console.error(error);
      }
    },
    async fetchSlotsData() {
      try {
        const response = await api.get('/admin/summary/slots');
        const data = response.data;

        const chartData = {
          labels: ['Available', 'Occupied'],
          datasets: [{
            label: 'Slots',
            data: [data.available_spots, data.occupied_spots],
            backgroundColor: [
              'rgba(75, 192, 192, 0.7)',
              'rgba(255, 99, 132, 0.7)',
            ],
          }]
        };

        this.renderSlotsChart(chartData);
      } catch (error) {
        toastr.error('Failed to fetch slots data');
        console.error(error);
      }
    },
    renderRevenueChart(data) {
      const ctx = document.getElementById('revenue-chart').getContext('2d');
      if (this.revenueChart) {
        this.revenueChart.destroy();
      }
      this.revenueChart = new Chart(ctx, {
        type: 'doughnut',
        data: data,
        options: {
          responsive: true,
          plugins: {
            legend: {
              position: 'top',
            },
            title: {
              display: true,
              text: 'Revenue by Parking Lot'
            }
          }
        },
      });
    },
    renderSlotsChart(data) {
      const ctx = document.getElementById('slots-chart').getContext('2d');
      if (this.slotsChart) {
        this.slotsChart.destroy();
      }
      this.slotsChart = new Chart(ctx, {
        type: 'bar',
        data: data,
        options: {
          responsive: true,
          plugins: {
            legend: {
              display: false
            },
            title: {
              display: true,
              text: 'Slot Availability'
            }
          },
          scales: {
            y: {
              beginAtZero: true
            }
          }
        },
      });
    }
  },
  mounted() {
    this.fetchRevenueData();
    this.fetchSlotsData();
  }
};
</script>

<style scoped>
/* Copied from AdminDashboard.vue */
.admin-dashboard {
  min-height: 100vh;
  background-color: #000;
}

.custom-navbar {
  display: flex !important;
  align-items: center !important;
  justify-content: space-between !important;
  background: #111 !important;
  border-radius: 2.5rem !important;
  box-shadow: 0 2px 24px 0 rgba(0,0,0,0.25) !important;
  padding: 0.5rem 2.5rem !important;
  margin: 2rem auto 2rem auto !important;
  max-width: 80vw !important;
  border: none !important;
}

.navbar-logo {
  font-size: 1.7rem !important;
  font-weight: 700 !important;
  display: flex !important;
  align-items: center !important;
  margin-right: 2rem !important;
}

.quick {
  color: #fff !important;
}

.park {
  color: #3bb3ff !important;
  margin-left: 0.2rem !important;
}

.navbar-menu {
  display: flex !important;
  gap: 2.5rem !important;
  list-style: none !important;
  margin: 0 !important;
  padding: 0 !important;
}

.nav-link {
  color: #3bb3ff !important;
  font-size: 1.1rem !important;
  font-weight: 500 !important;
  text-decoration: none !important;
  padding: 0.5rem 1.2rem !important;
  border-radius: 1.2rem !important;
  background: none !important;
  border: none !important;
  transition: background 0.2s, color 0.2s !important;
}

.nav-link.active,
.nav-link:hover {
  background: #3bb3ff !important;
  color: #fff !important;
}
.chart-container {
  background-color: #1a1a1a;
  padding: 20px;
  border-radius: 10px;
  border: 1px solid #333;
}

.chart-title {
  color: #3bb3ff;
  text-align: center;
  margin-bottom: 20px;
}
</style>