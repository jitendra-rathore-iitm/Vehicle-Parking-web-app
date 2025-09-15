<template>
  <div class="add-lot-container">
    <h2 style="text-align: center;">New Parking Lot</h2><br/><br/>
    <form @submit.prevent="addLot" @reset="resetForm">
      <label>Prime Location</label>
      <input type="text" v-model="form.prime_location" placeholder="Enter prime location" class="box" required /><br/><br/>

      <label>Address</label>
      <textarea v-model="form.address" placeholder="Enter address" class="box-textarea" required></textarea><br/><br/>

      <label>Pincode</label>
      <input type="number" v-model.number="form.pincode" placeholder="Enter pincode" class="box" required /><br/><br/>

      <label>Price (Per Hour)</label>
      <input type="number" v-model.number="form.price" placeholder="Enter price" class="box" required /><br/><br/>

      <label>Maximum Spots</label>
      <input type="number" v-model.number="form.number_of_spots" placeholder="Enter maximum spots" class="box" required /><br/><br/>


      <div class="d-flex justify-content-between">
        <button type="submit" class="btn btn-outline-success">Add</button>
        <button type="reset" class="btn btn-outline-secondary">Cancel</button>
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
  name: "AddParkingLot",
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
    };
  },
  methods: {
  async addLot() {
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
      await api.post("/admin/add/parkinglot", payload);
      toastr.success("Parking Lot added successfully");
      this.resetForm();
    } catch (error) {
      this.message = error.response?.data?.message || "Something went wrong";
      toastr.error(this.message);
    }
  },

    resetForm() {
      this.form = {
        prime_location: "",
        address: "",
        pincode: "",
        price: "",
        number_of_spots: ""
      };
      this.message = "";
    },
  },
};
</script>

<style scoped>
.add-lot-container {
  width: 420px;
  margin: 30px auto;
  padding: 30px;
  border: 3px solid #2ecc71;
  border-radius: 20px;
  background-color: #ffffff;
  box-shadow: 0 0 15px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease-in-out;
}
.add-lot-container:hover {
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
</style>


