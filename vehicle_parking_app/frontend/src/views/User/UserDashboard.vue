<template>
  <div class="user-dashboard text-white">
    <!-- Navigation (Copied from AdminDashboard.vue, adapted for user) -->
    <nav class="custom-navbar">
      <div class="navbar-logo">
        <span class="quick">Quick</span><span class="park">Park</span>
      </div>
      <ul class="navbar-menu">
        <li><a href="/user/dashboard" class="nav-link active">Home</a></li>
        <li><a href="/user/summary" class="nav-link">Summary</a></li>
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

    <!-- Content -->
    <div class="container py-4">
      <h2 class="mb-4" style = "text-align: center;">Welcome, User!</h2>

      <!-- Section: Parking History -->
      <div class="mb-5">
        <div class="d-flex justify-content-between align-items-center mb-3">
          <h4>Recent Parking History</h4>
          <div class="d-flex gap-2">
            <button 
              class="btn btn-outline-secondary btn-sm" 
              @click="fetchParkingHistory"
              :disabled="isLoading"
            >
              <i class="bi bi-arrow-clockwise"></i> Refresh
            </button>
          </div>
        </div>
        
        <!-- History Loading State -->
        <div v-if="isLoadingHistory" class="text-center py-4">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
          <p class="mt-2">Loading parking history...</p>
        </div>
        
        <!-- History Table -->
        <table v-else class="table table-dark table-hover table-bordered">
          <thead>
            <tr>
              <th>Spot ID</th>
              <th>Location</th>
              <th>Vehicle Number</th>
              <th>Parked At</th>
              <th>Released At</th>
              <th>Action</th>
            </tr>
          </thead>
        <tbody>
          <tr v-for="entry in history" :key="entry.spot_id">
            <td>{{ entry.spot_id }}</td>
            <td>{{ entry.location }}</td>
            <td>{{ entry.vehicle_number }}</td>
            <td>{{ formatDateTime(entry.parking_timestamp) }}</td>
            <td>
              <span v-if="entry.leaving_timestamp">{{ formatDateTime(entry.leaving_timestamp) }}</span>
              <span v-else class="text-warning">Occupied</span>
            </td>
            <td>
              <button
                v-if="!entry.leaving_timestamp"
                class="btn btn-sm btn-outline-danger me-1"
                @click="releaseSpot(entry.spot_id)"
                :disabled="isReleasing"
              >
                <span v-if="isReleasing" class="spinner-border spinner-border-sm me-1"></span>
                Release
              </button>
              <span v-else-if="entry.booking_status === 'parking out'" class="text-success">Parking Out</span>
              <span v-else-if="entry.booking_status === 'released'" class="text-success">Released</span>
              <span v-else class="text-muted">Completed</span>
            </td>
          </tr>
        </tbody>  
        </table>
        
        <!-- No History Message -->
        <div v-if="!isLoadingHistory && history.length === 0" class="text-center py-4">
          <p class="text-muted">No parking history found.</p>
        </div>
      </div>

      <!-- Section: Search and Available Lots -->
      <div class="mb-5">
        <div class="d-flex justify-content-between align-items-center mb-3">
          <h4>Available Parking Lots</h4>
          <div class="d-flex gap-2">
            <button 
              class="btn btn-outline-secondary btn-sm" 
              @click="fetchParkingLots"
              :disabled="isLoading"
            >
              <i class="bi bi-arrow-clockwise"></i> Refresh
            </button>
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
          <div
            v-for="lot in filteredParkingLots"
            :key="lot.id"
            :data-lot-id="lot.id"
            class="lot-box animate__animated animate__fadeInUp"
          >
            <h5 class="lot-title">{{ lot.prime_location }}</h5>
            <div class="lot-info">
              <p class="lot-id">Lot ID: {{ lot.id }}</p>
              <p class="price">Price: ₹{{ lot.price }}/hour</p>
              <p class="address">{{ lot.address }}</p>
            </div>
            
            <!-- Availability Status -->
            <div class="availability-status">
              <div class="status-display">
                <span class="available-count">{{ lot.available_spots }}</span> / 
                <span class="total-count">{{ lot.number_of_spots }}</span> Available
              </div>
            </div>
            
            <!-- Action Buttons -->
            <div class="lot-actions">
              <button 
                class="btn btn-primary btn-sm" 
                @click="book(lot.id)"
                :disabled="lot.available_spots === 0"
              >
                <i class="bi bi-calendar-check"></i> 
                {{ lot.available_spots === 0 ? 'Full' : 'Book Now' }}
              </button>
            </div>
          </div>
        </div>
        
        <!-- No Parking Lots Message -->
        <div v-else-if="parkingLots.length === 0" class="text-center py-4">
          <p>No parking lots found.</p>
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

    <!-- Booking Modal -->
    <div v-if="showBookingModal" class="modal-overlay" @click="closeBookingModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h5 class="modal-title">
            Book Parking Spot
          </h5>
          <button type="button" class="btn-close" @click="closeBookingModal">
            <span aria-hidden="true">&times;</span>
          </button>
        </div>
        <div class="modal-body">
          <div class="booking-form">
            <!-- Prefilled Information -->
            <div class="info-section">
              <h6 class="section-title">Parking Lot Details</h6>
              <div class="info-grid">
                <div class="info-item">
                  <span class="label">Lot ID:</span>
                  <span class="value">{{ bookingData.lot_id }}</span>
                </div>
                <div class="info-item">
                  <span class="label">Location:</span>
                  <span class="value">{{ bookingData.location }}</span>
                </div>
                <div class="info-item">
                  <span class="label">Price:</span>
                  <span class="value">₹{{ bookingData.price }}/hour</span>
                </div>
              </div>
            </div>
            
            <div class="info-section">
              <h6 class="section-title">Booking Details</h6>
              <div class="info-grid">
                <div class="info-item">
                  <span class="label">Spot ID:</span>
                  <span class="value spot-id-highlight">{{ bookingData.spot_id }}</span>
                </div>
                <div class="info-item">
                  <span class="label">User ID:</span>
                  <span class="value">{{ bookingData.user_id }}</span>
                </div>
              </div>
              <small class="text-info mt-2 d-block">
                <i class="bi bi-info-circle me-1"></i>
                Spot ID {{ bookingData.spot_id }} is the next available spot in this parking lot
              </small>
            </div>
            
            <!-- Vehicle Number Input -->
            <div class="form-group">
              <label for="vehicleNumber" class="form-label">Vehicle Number *</label>
              <input 
                type="text" 
                id="vehicleNumber"
                v-model="bookingData.vehicle_number" 
                class="form-control"
                placeholder="Enter vehicle number (e.g., KA01AB1234)"
                required
              />
              <small class="form-text text-muted">Format: KA01AB1234</small>
            </div>
            
            <!-- Booking Time -->
            <div class="info-section">
              <h6 class="section-title">Booking Information</h6>
              <div class="info-grid">
                <div class="info-item">
                  <span class="label">Booking Time:</span>
                  <span class="value">{{ bookingData.booking_time }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" @click="closeBookingModal">
            Cancel
          </button>
          <button 
            type="button" 
            class="btn btn-primary" 
            @click="confirmBooking"
            :disabled="!bookingData.vehicle_number || isBooking"
          >
            <span v-if="isBooking" class="spinner-border spinner-border-sm me-2"></span>
            Book Spot
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
  name: 'UserDashboard',
  data() {
    return {
      searchQuery: '',
      isLoading: false,
      parkingLots: [],
      filteredParkingLots: [],
      history: [],
      showBookingModal: false,
      bookingData: {
        lot_id: '',
        location: '',
        price: '',
        spot_id: '',
        user_id: '',
        vehicle_number: '',
        booking_time: '',
      },
      isBooking: false,
      isReleasing: false,
      isParkingOut: false,
      isLoadingHistory: false,
    }
  },
  methods: {
    logout() {
      localStorage.removeItem('access_token')
      localStorage.removeItem('user_role')
      this.$router.push('/login')
      console.log('User logged out successfully')
    },
    async fetchParkingLots() {
      this.isLoading = true
      try {
        const response = await api.get('/user/parkinglots/show')
        this.parkingLots = response.data.parking_lots
        this.filteredParkingLots = response.data.parking_lots
        console.log('Fetched parking lots:', this.parkingLots)
      } catch (error) {
        console.error('Error fetching parking lots:', error)
        if (error.response?.status === 401) {
          toastr.error('Please login again')
          this.$router.push('/login')
        } else {
          toastr.error('Failed to fetch parking lots')
        }
      } finally {
        this.isLoading = false
      }
    },
    async fetchParkingHistory() {
      this.isLoadingHistory = true
      try {
        const response = await api.get('/user/parkinglots/history')
        this.history = response.data.history
        console.log('Fetched parking history:', this.history)
      } catch (error) {
        console.error('Error fetching parking history:', error)
        if (error.response?.status === 401) {
          toastr.error('Please login again')
          this.$router.push('/login')
        } else {
          toastr.error('Failed to fetch parking history')
        }
      } finally {
        this.isLoadingHistory = false
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
    async book(lotId) {
      try {
        console.log('Attempting to book lot ID:', lotId);
        console.log('Available parking lots:', this.parkingLots);
        
        // Find the lot data
        const lot = this.parkingLots.find(l => l.id === lotId);
        if (!lot) {
          toastr.error('Parking lot not found');
          return;
        }
        
        console.log('Found lot data:', lot);
        
        // Open booking modal with lot data
        await this.openBookingModal(lot);
      } catch (error) {
        console.error('Error booking parking lot:', error);
        toastr.error('Failed to book parking lot')
      }
    },
    async openBookingModal(lot) {
      console.log('Opening booking modal for lot:', lot);
      
      try {
        // Get the next available spot ID from backend
        const response = await api.get(`/user/parkinglots/next-available-spot/${lot.id}`);
        const nextSpotId = response.data.next_available_spot_id;
        
        console.log('Next available spot ID:', nextSpotId);
        
        // Get current user ID from localStorage or generate a placeholder
        const userRole = localStorage.getItem('user_role');
        const userId = userRole === 'user' ? 'Current User' : 'User ID';
        
        // Format current date and time in 24-hour format
        const now = new Date();
        const formattedDateTime = now.toLocaleString('en-GB', {
          year: 'numeric',
          month: '2-digit',
          day: '2-digit',
          hour: '2-digit',
          minute: '2-digit',
          second: '2-digit',
          hour12: false
        });
        
        this.bookingData = {
          lot_id: lot.id,
          location: lot.prime_location,
          price: lot.price,
          spot_id: nextSpotId, // Actual spot ID from backend
          user_id: userId,
          vehicle_number: '',
          booking_time: formattedDateTime,
        };
        
        console.log('Booking data set:', this.bookingData);
        this.showBookingModal = true;
      } catch (error) {
        console.error('Error getting next available spot:', error);
        toastr.error('Failed to get available spot. Please try again.');
      }
    },
    closeBookingModal() {
      this.showBookingModal = false;
      this.bookingData = {
        lot_id: '',
        location: '',
        price: '',
        spot_id: '',
        user_id: '',
        vehicle_number: '',
        booking_time: '',
      };
    },
    async confirmBooking() {
      this.isBooking = true;
      try {
        // Check if user is authenticated
        const token = localStorage.getItem('access_token');
        if (!token) {
          toastr.error('Please login again to book parking spots');
          this.$router.push('/login');
          return;
        }
        
        // Validate vehicle number
        if (!this.bookingData.vehicle_number || this.bookingData.vehicle_number.trim() === '') {
          toastr.error('Please enter a valid vehicle number');
          return;
        }
        
        // Validate lot_id
        if (!this.bookingData.lot_id) {
          toastr.error('Invalid parking lot selection');
          return;
        }
        
        console.log('Sending booking data:', this.bookingData);
        console.log('Auth token:', token ? 'Present' : 'Missing');
        
        const requestData = {
          lot_id: parseInt(this.bookingData.lot_id),
          vehicle_number: this.bookingData.vehicle_number.trim()
        };
        
        // Book parking spot (only adds to Booking table)
        const response = await api.post('/user/parkinglots/book', requestData);
        toastr.success(`Parking spot booked successfully! Spot ID: ${response.data.spot_id}`);
        
        console.log('Response:', response.data);
        this.closeBookingModal();
        
        // Show loading state while refreshing data
        this.isLoading = true;
        
        // Small delay to ensure backend has processed the booking
        await new Promise(resolve => setTimeout(resolve, 500));
        
        // Refresh data to show updated available spots count
        await this.fetchParkingLots(); // Refresh lots after booking
        await this.fetchParkingHistory(); // Refresh history after booking
        
        // Show success message with updated count
        const updatedLot = this.parkingLots.find(lot => lot.id === this.bookingData.lot_id);
        if (updatedLot) {
          toastr.info(`Updated: ${updatedLot.available_spots} spots now available`);
          // Trigger animation for the updated count
          this.$nextTick(() => {
            const countElement = document.querySelector(`[data-lot-id="${updatedLot.id}"] .available-count`);
            if (countElement) {
              countElement.classList.add('updated');
              setTimeout(() => {
                countElement.classList.remove('updated');
              }, 500);
            }
          });
        }
      } catch (error) {
        console.error('Error confirming booking:', error);
        console.error('Error response:', error.response?.data);
        
        if (error.response?.status === 401) {
          toastr.error('Please login again to book parking spots');
          this.$router.push('/login');
        } else if (error.response?.status === 403) {
          toastr.error(error.response?.data?.message || 'Access denied');
        } else if (error.response?.status === 404) {
          toastr.error(error.response?.data?.message || 'Resource not found');
        } else {
          const errorMessage = error.response?.data?.message || 'Failed to process parking spot request';
          toastr.error(errorMessage);
        }
      } finally {
        this.isBooking = false;
      }
    },
         async releaseSpot(spotId) {
       this.isReleasing = true;
       try {
         const response = await api.post('/user/parkinglots/release', {
           spot_id: spotId,
           action: 'release'
         });
         
         console.log('Release response:', response.data);
         toastr.success(`Parking spot released successfully! Cost: ₹${response.data.parking_cost}`);
         
         // Refresh data
         this.fetchParkingLots();
         this.fetchParkingHistory();
       } catch (error) {
         console.error('Error releasing parking spot:', error);
         console.error('Error response:', error.response?.data);
         
         if (error.response?.status === 401) {
           toastr.error('Please login again');
           this.$router.push('/login');
         } else {
           const errorMessage = error.response?.data?.message || 'Failed to release parking spot';
           toastr.error(errorMessage);
         }
       } finally {
         this.isReleasing = false;
       }
     },
     async parkingOut(spotId) {
       this.isParkingOut = true;
       try {
         const response = await api.post('/user/parkinglots/release', {
           spot_id: spotId,
           action: 'parking_out'
         });
         
         console.log('Parking out response:', response.data);
         toastr.success(`Vehicle marked as parking out! Cost: ₹${response.data.parking_cost}`);
         
         // Refresh data
         this.fetchParkingLots();
         this.fetchParkingHistory();
       } catch (error) {
         console.error('Error parking out:', error);
         console.error('Error response:', error.response?.data);
         
         if (error.response?.status === 401) {
           toastr.error('Please login again');
           this.$router.push('/login');
         } else {
           const errorMessage = error.response?.data?.message || 'Failed to mark vehicle as parking out';
           toastr.error(errorMessage);
         }
       } finally {
         this.isParkingOut = false;
       }
     },
    formatDateTime(dateTimeString) {
      if (!dateTimeString) return 'N/A';
      const date = new Date(dateTimeString);
      return date.toLocaleString('en-GB', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        hour12: false
      });
    }
  },
  mounted() {
    this.fetchParkingLots()
    this.fetchParkingHistory()
  }
}
</script>

<style scoped>
@import 'https://cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css';

.user-dashboard {
  min-height: 100vh;
  background-color: #000;
}

/* Custom Navbar (Copied from AdminDashboard.vue) */
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


/* Parking grid reused from admin dashboard */
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

.lot-id {
  color: #6c757d;
  font-weight: 500;
  margin-bottom: 5px;
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

.availability-status {
  margin-bottom: 15px;
}

.status-display {
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

.available-count {
  color: #28a745;
  font-weight: 600;
  font-size: 1.2em;
  transition: all 0.3s ease;
}

.available-count.updated {
  animation: countUpdate 0.5s ease-in-out;
}

@keyframes countUpdate {
  0% { transform: scale(1); }
  50% { transform: scale(1.2); color: #ffc107; }
  100% { transform: scale(1); }
}

.total-count {
  color: #6c757d;
  font-weight: 600;
  font-size: 1.2em;
}

.lot-actions {
  margin-top: auto;
  padding-top: 10px;
  border-top: 1px solid #333;
  display: flex;
  justify-content: center;
}

.lot-actions .btn {
  font-size: 0.9rem;
  padding: 8px 16px;
  border-radius: 8px;
  font-weight: 500;
}

.lot-actions .btn i {
  margin-right: 6px;
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
  z-index: 1000;
}

.modal-content {
  width: 420px;
  margin: 30px auto;
  padding: 30px;
  border: 3px solid #3bb3ff;
  border-radius: 20px;
  background-color: #1a1a1a;
  box-shadow: 0 0 15px rgba(0, 0, 0, 0.3);
  transition: all 0.3s ease-in-out;
  max-height: 90vh;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

.modal-content:hover {
  transform: scale(1.02);
  box-shadow: 0 0 20px rgba(59, 179, 255, 0.6);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 2px solid #333;
}

.modal-title {
  margin: 0;
  color: #3bb3ff;
  font-size: 24px;
  font-weight: 600;
  text-align: center;
  flex-grow: 1;
}

.btn-close {
  background-color: #333;
  border: none;
  color: #fff;
  font-size: 1.5rem;
  padding: 8px;
  border-radius: 50%;
  cursor: pointer;
  transition: background-color 0.2s;
  width: 35px;
  height: 35px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-close:hover {
  background-color: #444;
}

.modal-body {
  padding: 0;
  flex-grow: 1;
}

.booking-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.info-section {
  background-color: #2a2a2a;
  border: 2px solid #333;
  border-radius: 10px;
  padding: 15px;
  margin-bottom: 0;
}

.section-title {
  color: #3bb3ff;
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 15px;
  border-bottom: 1px solid #333;
  padding-bottom: 8px;
}

.info-grid {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #444;
}

.info-item:last-child {
  border-bottom: none;
}

.label {
  color: #6c757d;
  font-size: 16px;
  font-weight: 500;
}

.value {
  color: #fff;
  font-weight: 600;
  font-size: 16px;
}

.form-group {
  margin-top: 0;
}

.form-label {
  display: block;
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 6px;
  color: #fff;
  transition: all 0.2s ease-in-out;
}

.form-control {
  width: 100%;
  height: 45px;
  border: 2px solid #ccc;
  border-radius: 10px;
  text-align: center;
  font-size: 16px;
  outline: none;
  transition: all 0.3s ease-in-out;
  background-color: #171414;
  color: #fff !important;
  padding: 10px 15px;
}

.form-control:focus {
  border-color: #3bb3ff;
  box-shadow: 0 0 8px #3bb3ff;
  background-color: #efefef;
  color: #000 !important;
}

.form-control::placeholder {
  color: #6c757d;
}

.form-text {
  color: #6c757d;
  font-size: 14px;
  margin-top: 5px;
  text-align: center;
}

.modal-footer {
  display: flex;
  justify-content: space-between;
  gap: 15px;
  padding: 0;
  margin-top: 20px;
  border-top: none;
  background-color: transparent;
}

.modal-footer .btn {
  width: 120px;
  padding: 8px;
  border-radius: 10px;
  font-weight: bold;
  font-size: 16px;
  transition: all 0.3s ease-in-out;
}

.modal-footer .btn:hover {
  transform: scale(1.05);
}

.modal-footer .btn i {
  margin-right: 6px;
}

.spot-id-highlight {
  background-color: #28a745;
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-weight: bold;
  font-size: 1.1em;
}
</style>
