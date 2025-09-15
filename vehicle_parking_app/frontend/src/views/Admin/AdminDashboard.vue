<template>
  <div class="admin-dashboard text-white">
    <!-- Navigation -->
    <nav class="custom-navbar">
      <div class="navbar-logo">
        <span class="quick">Quick</span><span class="park">Park</span>
      </div>
      <ul class="navbar-menu">
        <li><a href="/admin/dashboard" class="nav-link active">Home</a></li>
        <li><a href="/admin/users/show" class="nav-link">Users</a></li>
        <li><a href="/admin/add/parkinglot" class="nav-link">Parking Lots</a></li>
        <li><a href="/admin/summary" class="nav-link">Summary</a></li>
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

    <!-- Dashboard Content -->
    <div class="container py-4">
      <h2 class="mb-4" style = "text-align: center;">Welcome, Admin!</h2>

      <!-- Section: Parking Lot Grid -->
      <div class="mb-5">
        <div class="d-flex justify-content-between align-items-center mb-3">
          <h4>Parking Lots</h4>
          <div class="d-flex gap-2">
            <button 
              class="btn btn-outline-secondary btn-sm" 
              @click="fetchParkingLots"
              :disabled="isLoading"
            >
              <i class="bi bi-arrow-clockwise"></i> Refresh
            </button>
            <a href="/admin/add/parkinglot" class="btn btn-outline-primary btn-sm">+ Add Lot</a>
          </div>
        </div>
        
        <!-- Search Bar -->
        <div class="search-container mb-4">
          <div class="input-group">
            <span class="input-group-text">
              <i class="bi bi-search"></i>
            </span>
            <input 
              type="text" 
              v-model="searchQuery" 
              placeholder="Search parking lots by location..." 
              class="form-control search-input"
              @input="filterParkingLots"
            />
            <button 
              v-if="searchQuery" 
              class="btn btn-outline-secondary" 
              @click="clearSearch"
              type="button"
            >
              <i class="bi bi-x"></i>
            </button>
          </div>
          <div v-if="searchQuery" class="search-results-info mt-2">
            <small class="text-muted">
              Showing {{ filteredParkingLots.length }} of {{ parkingLots.length }} parking lots
            </small>
          </div>
        </div>
        
        <!-- Loading State -->
        <div v-if="isLoading" class="text-center py-4">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
          <p class="mt-2">Loading parking lots...</p>
        </div>
        
        <!-- Parking Lots Grid -->
        <div v-else-if="filteredParkingLots.length > 0" class="parking-grid">
          <div v-for="lot in filteredParkingLots" :key="lot.id" class="lot-box">
            <h5 class="lot-title">{{ lot.prime_location }}</h5>
            <div class="lot-info">
              <p class="price">Price: ₹{{ lot.price }}/hour</p>
              <p class="address">{{ lot.address }}</p>
            </div>
            
            <!-- Slot Status Display -->
            <div class="slot-status">
              <div class="status-summary">
                <span class="status-label">Available:</span>
                <span class="available-count">{{ lot.available_spots }}</span> / 
                <span class="total-count">{{ lot.number_of_spots }}</span>
                <span class="spots-label">spots</span>
              </div>
              
              <!-- Visual Slot Grid -->
              <div class="slot-grid">
                <!-- Debug info -->
                <div v-if="!lot.spots || lot.spots.length === 0" style="color: #ffc107; font-size: 0.8rem; margin-bottom: 5px;">
                  Using fallback display (no spots data)
                </div>
                
                <!-- If spots data is available, show actual spots -->
                <template v-if="lot.spots && lot.spots.length > 0">
                  <div 
                    v-for="spot in lot.spots.slice().sort((a, b) => a.id - b.id)" 
                    :key="`spot-${spot.id}`"
                    class="slot-box"
                    :class="{ occupied: spot.status === 'O', available: spot.status === 'A' }"
                    :title="`Spot ${spot.id}: ${spot.status === 'O' ? 'Occupied' : 'Available'}`"
                    @click="showSpotDetails(lot.id, spot.id, lot.prime_location, spot.status)"
                  >
                    {{ spot.status === 'O' ? 'O' : 'A' }}
                  </div>
                </template>
                
                <!-- Fallback: Show generic spots if spots data is not available -->
                <template v-else>
                  <div 
                    v-for="spotIndex in (lot.number_of_spots - lot.available_spots)" 
                    :key="`occupied-${spotIndex}`"
                    class="slot-box occupied"
                    :title="`Occupied Spot ${spotIndex}`"
                  >
                    O
                  </div>
                  <div 
                    v-for="spotIndex in lot.available_spots" 
                    :key="`available-${spotIndex}`"
                    class="slot-box available"
                    :title="`Available Spot ${spotIndex}`"
                  >
                    A
                  </div>
                </template>
              </div>
            </div>
            
            <!-- Action Buttons -->
            <div class="lot-actions">
              <button class="btn btn-sm btn-outline-info me-2" @click="editLot(lot.id)">
                <i class="bi bi-pencil"></i> Edit
              </button>
              <button class="btn btn-sm btn-outline-danger" @click="deleteLot(lot.id)">
                <i class="bi bi-trash"></i> Delete
              </button>
            </div>
          </div>
        </div>

        <!-- No Parking Lots Message -->
        <div v-else-if="parkingLots.length === 0" class="text-center py-4">
          <p>No parking lots found. Please add a new one.</p>
        </div>
        
        <!-- No Search Results Message -->
        <div v-else-if="searchQuery && filteredParkingLots.length === 0" class="text-center py-4">
          <p>No parking lots found matching "{{ searchQuery }}".</p>
          <button class="btn btn-outline-secondary btn-sm" @click="clearSearch">
            Clear Search
          </button>
        </div>
      </div>

    </div>
    
    <!-- Spot Details Modal -->
    <div v-if="showSpotModal" class="modal-overlay" @click="closeSpotModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h5 class="modal-title">
            <i class="bi bi-info-circle me-2"></i>
            Spot Details
          </h5>
          <button type="button" class="btn-close" @click="closeSpotModal">
            <i class="bi bi-x-lg"></i>
          </button>
        </div>
        
        <div class="modal-body">
          <div v-if="spotDetails" class="spot-info">
            <!-- Occupied Spot Details -->
            <div v-if="spotDetails.status === 'O'" class="info-section">
              <h6 class="section-title">
                <i class="bi bi-info-circle me-2"></i>
                Spot Details
              </h6>
              <div class="info-grid">
                <div class="info-item">
                  <span class="label">Parking Lot:</span>
                  <span class="value">{{ selectedSpotLocation }}</span>
                </div>
                <div class="info-item">
                  <span class="label">Spot ID:</span>
                  <span class="value">{{ spotDetails.spot_id }}</span>
                </div>
                <div class="info-item">
                  <span class="label">Status:</span>
                  <span class="value status-badge occupied">Occupied</span>
                </div>
                <div class="info-item">
                  <span class="label">Customer Name:</span>
                  <span class="value">{{ spotDetails.booking?.customer_name || 'N/A' }}</span>
                </div>
                <div class="info-item">
                  <span class="label">Vehicle Number:</span>
                  <span class="value">{{ spotDetails.booking?.vehicle_number || 'N/A' }}</span>
                </div>
                <div class="info-item">
                  <span class="label">Parking Time:</span>
                  <span class="value">{{ formatDate(spotDetails.booking?.parking_timestamp) }}</span>
                </div>
              </div>
            </div>

            <!-- Available Spot Details -->
            <div v-else class="info-section">
              <h6 class="section-title">
                <i class="bi bi-info-circle me-2"></i>
                Spot Details
              </h6>
              <div class="info-grid">
                <div class="info-item">
                  <span class="label">Parking Lot:</span>
                  <span class="value">{{ selectedSpotLocation }}</span>
                </div>
                <div class="info-item">
                  <span class="label">Spot ID:</span>
                  <span class="value">{{ spotDetails.spot_id }}</span>
                </div>
                <div class="info-item">
                  <span class="label">Status:</span>
                  <span class="value status-badge available">Available</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Loading State -->
          <div v-else class="loading-state">
            <div class="spinner-border text-primary" role="status">
              <span class="visually-hidden">Loading...</span>
            </div>
            <p class="mt-2">Loading spot details...</p>
          </div>
        </div>
        
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" @click="closeSpotModal">
            Close
          </button>
        </div>
      </div>
    </div>
</div>  
      
</template>

<script>
import api from '../../api/api.js'
import toastr from 'toastr'


export default {
    data() {
        return {
            parkingLots: [],
            refreshInterval: null,
            isLoading: false, // Added loading state
            searchQuery: '', // Added search query
            filteredParkingLots: [], // Added filtered parking lots
            showSpotModal: false, // Added modal state
            selectedLotId: null,
            selectedSpotId: null,
            selectedSpotStatus: null,
            selectedSpotLocation: null,
            spotDetails: null
        }
    },
    methods: {
      logout() {
      localStorage.removeItem('access_token')
      localStorage.removeItem('user_role')
      this.$router.push('/login')
      console.log('Admin logged out successfully')
    },
    async editLot(lotId) {
      this.$router.push(`/admin/edit/parkinglot/${lotId}`)
    },
    async deleteLot(lotId){
      if (confirm('Are you sure that you want to delete this parking lot?')) {
        try {
          await api.delete(`/admin/delete/parkingLot/${lotId}`)
          this.parkingLots = this.parkingLots.filter(lot => lot.id !== lotId)
          toastr.success('Parking lot deleted successfully')
          // Refresh data after deletion
          this.fetchParkingLots()
        } catch (error) {
          console.error('Error deleting parking lot:', error)
          toastr.error('Failed to delete parking lot')
        }
      }
    },
    async fetchParkingLots() {
      this.isLoading = true // Set loading to true
      try {
        const response = await api.get('/admin/parkinglots/show')
        console.log('API response:', response.data)
        this.parkingLots = response.data.parking_lots
        this.filteredParkingLots = response.data.parking_lots // Initialize filtered lots
        
        // Debug: Check if spots data is available
        this.parkingLots.forEach((lot, index) => {
          console.log(`Lot ${lot.id} (${lot.prime_location}):`, {
            total_spots: lot.number_of_spots,
            available_spots: lot.available_spots,
            spots_data: lot.spots ? lot.spots.length : 'No spots data',
            spots_details: lot.spots ? lot.spots.map(s => `${s.id}:${s.status}`) : []
          });
        });
      } catch (error) {
        console.error('Error fetching parking lots:', error)
        toastr.error('Failed to fetch parking lots data')
      } finally {
        this.isLoading = false // Set loading to false
      }
    },
    filterParkingLots() {
      if (!this.searchQuery) {
        this.filteredParkingLots = this.parkingLots
        return
      }
      this.filteredParkingLots = this.parkingLots.filter(lot => 
        lot.prime_location.toLowerCase().includes(this.searchQuery.toLowerCase())
      )
    },
    clearSearch() {
      this.searchQuery = ''
      this.filteredParkingLots = this.parkingLots
    },
    startAutoRefresh() {
      // Refresh data every 30 seconds
      this.refreshInterval = setInterval(() => {
        this.fetchParkingLots()
      }, 30000)
    },
    stopAutoRefresh() {
      if (this.refreshInterval) {
        clearInterval(this.refreshInterval)
        this.refreshInterval = null
      }
    },
    async showSpotDetails(lotId, spotId, location, expectedStatus) {
      this.selectedLotId = lotId;
      this.selectedSpotId = spotId;
      this.selectedSpotLocation = location;
      this.spotDetails = null; // Clear previous details
      this.showSpotModal = true;

      try {
        // Get the actual spot details from the database
        const response = await api.get(`/admin/spot-details/${lotId}/${spotId}`);
        this.spotDetails = {
          ...response.data,
          price_per_hour: response.data.price_per_hour || this.getPricePerHourFromLot(lotId)
        };
        // Verify the status matches what we expect
        if (this.spotDetails.status !== expectedStatus) {
          // Refresh the parking lots to get updated data
          this.fetchParkingLots();
        }
      } catch (error) {
        // error handling
      }
    },
    getPricePerHourFromLot(lotId) {
      const lot = this.parkingLots.find(l => l.id === lotId);
      return lot ? lot.price : 0;
    },
    closeSpotModal() {
      this.showSpotModal = false;
      this.selectedLotId = null;
      this.selectedSpotId = null;
      this.selectedSpotLocation = null;
      this.spotDetails = null;
    },
    formatDate(timestamp) {
      if (!timestamp) return 'N/A';
      const date = new Date(timestamp);
      const options = { year: 'numeric', month: 'numeric', day: 'numeric', hour: 'numeric', minute: 'numeric' };
      return date.toLocaleDateString(undefined, options);
    },
    calculateParkingHours(timestamp) {
      if (!timestamp) return 'N/A';
      const parkingTime = new Date(timestamp);
      const currentTime = new Date();
      const diffInHours = (currentTime - parkingTime) / (1000 * 60 * 60);
      // Round up to nearest hour
      return Math.ceil(diffInHours) + ' hours';
    },
    calculateParkingCost(timestamp, pricePerHour) {
      if (!timestamp || !pricePerHour) return 'N/A';
      const hours = Math.ceil((new Date() - new Date(timestamp)) / (1000 * 60 * 60));
      return hours * pricePerHour;
    }
 },
 mounted(){
      this.fetchParkingLots()
      this.startAutoRefresh()
    },
    beforeUnmount() {
      this.stopAutoRefresh()
    }
}
</script>


<style scoped>
@import 'https://cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css';

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


/* Search styles */
.search-container {
  max-width: 500px;
  margin: 0 auto;
}

.search-input {
  border-radius: 10px;
  border: 2px solid #333;
  background-color: #171414;
  color: #171713;
  transition: all 0.3s ease-in-out;
}

.search-input:focus {
  border-color: #20d367;
  box-shadow: 0 0 8px #18415b;
  background-color: #efefef;
}

.search-input::placeholder {
  color: #a70b56;
}

.input-group-text {
  background-color: #333;
  border: 2px solid #333;
  border-right: none;
  color: #3bb3ff;
  border-radius: 8px 0 0 8px;
}

.search-results-info {
  text-align: center;
  color: #6c757d;
  font-size: 0.9rem;
}

/* Parking grid layout */
.parking-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  justify-content: center;
  align-items: stretch;
}

.lot-box {
  flex: 1 1 300px;
  max-width: 400px;
  min-width: 280px;
  background-color: #1a1a1a;
  padding: 20px;
  border: 1px solid #333;
  border-radius: 10px;
  text-align: center;
  transition: transform 0.2s ease-in-out;
  min-height: 280px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.lot-box:hover {
  transform: scale(1.03);
  box-shadow: 0 0 10px #3498db;
}

.lot-title {
  color: #3bb3ff;
  font-size: 1.3rem;
  font-weight: 600;
  margin-bottom: 10px;
}

.lot-info {
  margin-bottom: 15px;
}

.price {
  color: #28a745;
  font-weight: 500;
  margin-bottom: 5px;
}

.address {
  color: #6c757d;
  font-size: 0.9rem;
  margin-bottom: 0;
}

.slot-status {
  margin-bottom: 15px;
}

.status-summary {
  color: #fff;
  font-weight: 500;
  margin-bottom: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
  background-color: #2a2a2a;
  padding: 10px;
  border-radius: 8px;
}

.status-label {
  color: #6c757d;
  font-weight: 500;
}

.available-count {
  color: #28a745;
  font-weight: 600;
  font-size: 1.2em;
}

.total-count {
  color: #6c757d;
  font-weight: 600;
  font-size: 1.2em;
}

.spots-label {
  color: #6c757d;
  font-weight: 600;
}

.slot-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 4px;
  margin: 10px 0;
  max-height: 80px;
  overflow-y: auto;
}

.slot-box {
  width: 25px;
  height: 25px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.slot-box.available {
  background-color: #28a745;
  color: white;
  border: 1px solid #20c997;
}

.slot-box.occupied {
  background-color: #dc3545;
  color: white;
  border: 1px solid #c82333;
}

.slot-box:hover {
  transform: scale(1.1);
  box-shadow: 0 2px 4px rgba(0,0,0,0.3);
}

.lot-actions {
  margin-top: auto;
  padding-top: 10px;
  border-top: 1px solid #333;
}

.lot-actions .btn {
  font-size: 0.8rem;
  padding: 4px 8px;
}

.lot-actions .btn i {
  margin-right: 4px;
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1050;
  backdrop-filter: blur(5px);
}

.modal-content {
  background-color: #1a1a1a;
  border-radius: 15px;
  width: 90%;
  max-width: 500px;
  max-height: 80vh;
  overflow-y: auto;
  border: 2px solid #333;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
  animation: modalSlideIn 0.3s ease-out;
}

@keyframes modalSlideIn {
  from {
    opacity: 0;
    transform: translateY(-50px) scale(0.9);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 25px;
  border-bottom: 1px solid #333;
  background-color: #222;
  border-radius: 15px 15px 0 0;
}

.modal-title {
  color: #3bb3ff;
  margin: 0;
  font-weight: 600;
  font-size: 1.2rem;
}

.btn-close {
  background: none;
  border: none;
  color: #6c757d;
  font-size: 1.2rem;
  cursor: pointer;
  padding: 5px;
  border-radius: 5px;
  transition: all 0.2s ease;
}

.btn-close:hover {
  color: #dc3545;
  background-color: rgba(220, 53, 69, 0.1);
}

.modal-body {
  padding: 25px;
  color: #fff;
}

.spot-info {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.info-section {
  background-color: #222;
  padding: 20px;
  border-radius: 10px;
  border: 1px solid #333;
}

.section-title {
  color: #3bb3ff;
  margin-bottom: 15px;
  font-weight: 600;
  font-size: 1rem;
  display: flex;
  align-items: center;
}

.info-grid {
  display: grid;
  gap: 12px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #333;
}

.info-item:last-child {
  border-bottom: none;
}

.label {
  color: #6c757d;
  font-weight: 500;
  font-size: 0.9rem;
}

.value {
  color: #fff;
  font-weight: 600;
  text-align: right;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
}

.status-badge.available {
  background-color: #28a745;
  color: white;
}

.status-badge.occupied {
  background-color: #dc3545;
  color: white;
}

.cost {
  color: #28a745;
  font-weight: 700;
  font-size: 1.1rem;
}

.available-message {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  background-color: rgba(40, 167, 69, 0.1);
  border: 1px solid #28a745;
  border-radius: 8px;
  color: #28a745;
  font-weight: 500;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  color: #6c757d;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  padding: 20px 25px;
  border-top: 1px solid #333;
  background-color: #222;
  border-radius: 0 0 15px 15px;
}

.modal-footer .btn {
  padding: 8px 20px;
  border-radius: 8px;
  font-weight: 500;
}

body{
    background: #000;
}
</style>

