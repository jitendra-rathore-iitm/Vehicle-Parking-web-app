<template>
  <div class="edit-lot-container">
    <h2 style="text-align: center;">Edit Parking Lot</h2><br/><br/>
    
    <!-- Loading State -->
    <div v-if="isLoading" class="text-center py-4">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-2">Loading parking lot details...</p>
    </div>
    
    <!-- Edit Form -->
    <form v-else @submit.prevent="updateLot" @reset="resetForm">
      <!-- Current Status Display -->
      <div class="status-info mb-4">
        <h5 class="text-center mb-3">Current Status</h5>
        <div class="row text-center">
          <div class="col-4">
            <div class="status-box total">
              <span class="status-number">{{ lotInfo.number_of_spots }}</span>
              <span class="status-label">Total Spots</span>
            </div>
          </div>
          <div class="col-4">
            <div class="status-box available">
              <span class="status-number">{{ lotInfo.available_spots }}</span>
              <span class="status-label">Available</span>
            </div>
          </div>
          <div class="col-4">
            <div class="status-box occupied">
              <span class="status-number">{{ lotInfo.occupied_spots }}</span>
              <span class="status-label">Occupied</span>
            </div>
          </div>
        </div>
      </div>

      <label>Prime Location</label>
      <input type="text" v-model="form.prime_location" placeholder="Enter prime location" class="box" required /><br/><br/>

      <label>Address</label>
      <textarea v-model="form.address" placeholder="Enter address" class="box-textarea" required></textarea><br/><br/>

      <label>Pincode</label>
      <input type="number" v-model.number="form.pincode" placeholder="Enter pincode" class="box" required /><br/><br/>

      <label>Price (Per Hour)</label>
      <input type="number" v-model.number="form.price" placeholder="Enter price" class="box" required /><br/><br/>

      <label>Maximum Spots</label>
      <input type="number" v-model.number="form.number_of_spots" placeholder="Enter maximum spots" class="box" required />
      
      <!-- Warning for occupied spots -->
      <div v-if="showOccupiedWarning" class="warning-message">
        <i class="bi bi-exclamation-triangle"></i>
        <strong>Warning:</strong> This parking lot has {{ lotInfo.occupied_spots }} occupied spot(s). 
        You cannot reduce the number of spots below {{ lotInfo.number_of_spots }} until all spots are available.
      </div>
      
      <br/><br/>

      <div class="d-flex justify-content-between">
        <button type="submit" class="btn btn-outline-success">Update</button>
        <button type="button" class="btn btn-outline-secondary" @click="goBack">Cancel</button>
      </div>
    </form>

    <div class="d-flex justify-content-center mt-3">
      <p class="text-danger">{{ message }}</p>
    </div>
  </div>
</template>

<script>
import api from "../../api/api.js";
import toastr from "toastr";

toastr.options = {
  closeButton: true,
  progressBar: true,
  positionClass: "toast-top-right",
  timeOut: "3000",
};

export default {
  name: "EditParkingLot",
  data() {
    return {
      form: {
        prime_location: "",
        address: "",
        pincode: "",
        price: "",
        number_of_spots: ""
      },
      message: "",
      isLoading: true,
      lotId: null,
      lotInfo: { // Added lotInfo to store current status
        number_of_spots: 0,
        available_spots: 0,
        occupied_spots: 0
      },
      showOccupiedWarning: false // Added for warning display
    };
  },
  methods: {
    async fetchParkingLot() {
      try {
        this.isLoading = true;
        const response = await api.get(`/admin/parkinglot/${this.lotId}`);
        const lot = response.data;
        
        this.form = {
          prime_location: lot.prime_location,
          address: lot.address,
          pincode: lot.pincode,
          price: lot.price,
          number_of_spots: lot.number_of_spots
        };
        this.lotInfo = { // Populate lotInfo with current status
          number_of_spots: lot.number_of_spots,
          available_spots: lot.available_spots,
          occupied_spots: lot.occupied_spots
        };
        this.showOccupiedWarning = this.lotInfo.occupied_spots > 0; // Set warning based on current occupied spots
      } catch (error) {
        console.error('Error fetching parking lot:', error);
        this.message = error.response?.data?.message || "Failed to load parking lot details";
        toastr.error(this.message);
        this.goBack();
      } finally {
        this.isLoading = false;
      }
    },

    async updateLot() {
      try {
        if (
          !this.form.prime_location ||
          !this.form.address ||
          isNaN(this.form.pincode) ||
          isNaN(this.form.price) ||
          isNaN(this.form.number_of_spots)
        ) {
          this.message = "All fields are required and must be valid numbers";
          toastr.error(this.message);
          return;
        }

        const payload = {
          prime_location: this.form.prime_location,
          address: this.form.address,
          pincode: parseInt(this.form.pincode, 10),
          price: parseFloat(this.form.price),
          number_of_spots: parseInt(this.form.number_of_spots, 10)
        };

        await api.put(`/admin/edit/parkingLot/${this.lotId}`, payload);
        toastr.success("Parking Lot updated successfully");
        this.goBack();
      } catch (error) {
        console.error('Error updating parking lot:', error);
        
        // Handle specific error for occupied spots
        if (error.response?.status === 400 && error.response?.data?.occupied_count) {
          const data = error.response.data;
          const warningMessage = `${data.message}\n\nDetails:\n- Current spots: ${data.current_spots}\n- Occupied spots: ${data.occupied_count}\n- Requested spots: ${data.requested_spots}`;
          this.message = warningMessage;
          toastr.warning("Cannot reduce spots - some are occupied!");
        } else {
          this.message = error.response?.data?.message || "Something went wrong";
          toastr.error(this.message);
        }
      }
    },

    resetForm() {
      this.fetchParkingLot();
    },

    goBack() {
      this.$router.push('/admin/dashboard');
    }
  },
  
  mounted() {
    this.lotId = this.$route.params.id;
    if (this.lotId) {
      this.fetchParkingLot();
    } else {
      this.message = "No parking lot ID provided";
      toastr.error(this.message);
      this.goBack();
    }
  }
};
</script>

<style scoped>
.edit-lot-container {
  width: 420px;
  margin: 30px auto;
  padding: 30px;
  border: 3px solid #2ecc71;
  border-radius: 20px;
  background-color: #ffffff;
  box-shadow: 0 0 15px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease-in-out;
}

.edit-lot-container:hover {
  transform: scale(1.02);
  box-shadow: 0 0 20px rgba(46, 204, 113, 0.6);
}

.box {
  width: 100%;
  height: 45px;
  border: 2px solid #ccc;
  border-radius: 10px;
  text-align: center;
  font-size: 16px;
  outline: none;
  transition: all 0.3s ease-in-out;
}

.box:focus {
  border-color: #2ecc71;
  box-shadow: 0 0 8px #2ecc71;
  background-color: #f9f9ff;
}

.box-textarea {
  width: 100%;
  height: 80px;
  border: 2px solid #ccc;
  border-radius: 10px;
  font-size: 16px;
  padding: 10px;
  transition: all 0.3s ease-in-out;
  resize: none;
  outline: none;
}

.box-textarea:focus {
  border-color: #2ecc71;
  box-shadow: 0 0 8px #2ecc71;
  background-color: #f9f9ff;
}

label {
  display: block;
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 6px;
  transition: all 0.2s ease-in-out;
}

.btn-outline-success,
.btn-outline-secondary {
  width: 120px;
  padding: 8px;
  border-radius: 10px;
  font-weight: bold;
}

.text-danger {
  font-weight: 600;
  animation: fadeIn 0.5s ease-in-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* New styles for status display */
.status-info {
  background-color: #f0f0f0;
  padding: 20px;
  border-radius: 10px;
  margin-bottom: 20px;
  box-shadow: inset 0 0 10px rgba(0, 0, 0, 0.05);
}

.status-box {
  padding: 15px;
  border-radius: 10px;
  margin: 10px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background-color: #e0e0e0;
  transition: all 0.3s ease-in-out;
}

.status-box:hover {
  transform: scale(1.05);
  background-color: #d0d0d0;
}

.status-number {
  font-size: 28px;
  font-weight: bold;
  color: #333;
  margin-bottom: 5px;
}

.status-label {
  font-size: 14px;
  color: #666;
}

.status-box.total {
  background-color: #4CAF50;
  color: white;
}

.status-box.available {
  background-color: #2196F3;
  color: white;
}

.status-box.occupied {
  background-color: #F44336;
  color: white;
}

/* New styles for warning message */
.warning-message {
  background-color: #fff3cd;
  color: #856404;
  padding: 10px;
  border: 1px solid #ffeeba;
  border-radius: 8px;
  margin-top: 15px;
  display: flex;
  align-items: center;
  font-size: 14px;
  font-weight: 600;
}

.warning-message i {
  margin-right: 8px;
  font-size: 18px;
  color: #ffc107; /* Yellow color for exclamation triangle */
}
</style>