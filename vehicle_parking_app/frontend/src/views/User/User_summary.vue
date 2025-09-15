<template>
  <div class="user-dashboard text-white">
    <nav class="custom-navbar">
      <div class="navbar-logo">
        <span class="quick">Quick</span><span class="park">Park</span>
      </div>
      <ul class="navbar-menu">
        <li><a href="/user/dashboard" class="nav-link">Home</a></li>
        <li><a href="/user/summary" class="nav-link active">Summary</a></li>
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
            <li><a class="dropdown-item" @click="$router.push('/user/edit-profile')" href="#">Edit Profile</a></li>
            <li><hr class="dropdown-divider" /></li>
            <li><a class="dropdown-item text-danger" @click="logout" href="#">Logout</a></li>
          </ul>
        </li>
      </div>
    </nav>

    <div class="container py-4">
      <h2 class="mb-4" style="text-align: center;">Your Parking Summary</h2>

      <div class="row">
        <div class="col-md-12">
          <div class="chart-container">
            <h4 class="chart-title">Parking Lot Usage</h4>
            <canvas id="usage-chart" v-if="chartData.labels.length > 0"></canvas>
            <p v-else class="text-center">No use of parking lots</p>
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
  name: 'UserSummary',
  data() {
    return {
      usageChart: null,
      chartData: {
        labels: [],
        datasets: [{
          label: 'Parking Lot Usage',
          data: [],
          backgroundColor: 'rgba(54, 162, 235, 0.7)',
        }]
      }
    };
  },
  methods: {
    logout() {
      localStorage.removeItem('access_token');
      localStorage.removeItem('user_role');
      this.$router.push('/login');
    },
    async fetchUsageData() {
      try {
        const response = await api.get('/user/summary/slots');
        const data = response.data;

        if (Array.isArray(data) && data.length > 0) {
          this.chartData.labels = data.map(item => item.location);
          this.chartData.datasets[0].data = data.map(item => item.count);
          
          this.$nextTick(() => {
            this.renderUsageChart();
          });

        } else {
            this.chartData.labels = [];
            this.chartData.datasets[0].data = [];
        }
      } catch (error) {
        let errorMessage = 'Failed to fetch usage data';
        if (error.response && error.response.data && error.response.data.message) {
            errorMessage = error.response.data.message;
        }
        toastr.error(errorMessage);
        console.error('Error fetching usage data:', error.response || error);
      }
    },
    renderUsageChart() {
      const ctx = document.getElementById('usage-chart').getContext('2d');
      if (this.usageChart) {
        this.usageChart.destroy();
      }
      this.usageChart = new Chart(ctx, {
        type: 'bar',
        data: this.chartData,
        options: {
          responsive: true,
          plugins: {
            legend: {
              display: false
            },
            title: {
              display: true,
              text: 'Number of Times Each Parking Lot was Used'
            }
          },
          scales: {
            y: {
              beginAtZero: true,
              ticks: {
                stepSize: 1
              }
            }
          }
        },
      });
    }
  },
  mounted() {
    this.fetchUsageData();
  }
};
</script>

<style scoped>
.user-dashboard {
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