<template>
  <div class="edit-profile-container">
    <h2 style="text-align: center;">Edit Profile</h2><br/><br/>
    <form @submit.prevent="updateProfile" @reset="resetForm">
      <label>Username</label>
      <input type="text" v-model="form.username" placeholder="Enter username" class="box" required /><br/><br/>

      <label>Email</label> 
      <input type="email" v-model="form.email" placeholder="Enter email" class="box" required /><br/><br/>

      <label>Full Name</label>
      <input type="text" v-model="form.full_name" placeholder="Enter full name" class="box" required /><br/><br/>

      <label>Address</label>
      <textarea v-model="form.address" placeholder="Enter address" class="box-textarea" required></textarea><br/><br/>

      <label>Pincode</label>
      <input type="number" v-model.number="form.pincode" placeholder="Enter pincode" class="box" required /><br/><br/>

      <label>New Password</label>
      <input type="password" v-model="form.password" placeholder="Leave blank to keep current password" class="box" /><br/><br/>

      <div class="d-flex justify-content-between">
        <button type="submit" class="btn btn-outline-success">Save</button>
        <button type="reset" class="btn btn-outline-secondary">Cancel</button>
      </div>
    </form>
    <div class="d-flex justify-content-center mt-3">
      <p class="text-success">{{ successMessage }}</p>
      <p class="text-danger">{{ errorMessage }}</p>
    </div>
  </div>
</template>

<script>
import api from '../api/api.js';
import toastr from 'toastr';

toastr.options = {
  closeButton: true,
  progressBar: true,
  positionClass: 'toast-top-right',
  timeOut: '3000',
};

export default {
  name: 'EditProfile',
  data() {
    return {
      form: {
        username: '',
        email: '',
        full_name: '',
        address: '',
        pincode: '',
        password: ''
      },
      successMessage: '',
      errorMessage: ''
    };
  },
  async mounted() {
    try {
      // Use role from localStorage to determine endpoint
      const role = localStorage.getItem('user_role') || 'user';
      const url = role === 'admin' ? '/admin/profile' : '/user/profile';
      const res = await api.get(url);
      this.form.username = res.data.username;
      this.form.email = res.data.email;
      this.form.full_name = res.data.full_name;
      this.form.address = res.data.address;
      this.form.pincode = res.data.pincode;
    } catch (err) {
      this.errorMessage = 'Failed to load profile.';
    }
  },
  methods: {
    async updateProfile() {
      try {
        const role = localStorage.getItem('user_role') || 'user';
        const url = role === 'admin' ? '/admin/profile' : '/user/profile';
        const payload = { ...this.form };
        if (!payload.password) delete payload.password;
        await api.put(url, payload);
        this.successMessage = 'Profile updated successfully!';
        toastr.success('Profile updated successfully!');
        this.form.password = '';
      } catch (err) {
        this.errorMessage = err.response?.data?.message || 'Failed to update profile.';
      }
    },
    resetForm() {
      this.form.password = '';
      this.successMessage = '';
      this.errorMessage = '';
    }
  }
};
</script>

<style scoped>
.edit-profile-container {
  width: 420px;
  margin: 30px auto;
  padding: 30px;
  border: 3px solid #2ecc71;
  border-radius: 20px;
  background-color: #ffffff;
  box-shadow: 0 0 15px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease-in-out;
}
.edit-profile-container:hover {
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
.text-success {
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