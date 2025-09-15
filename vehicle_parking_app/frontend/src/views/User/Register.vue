
<template>
    <div class="login-container">
        <h2 style = "text-align: center;">Register</h2><br/>
        <div style = "text-align: center;">
            <form @submit.prevent="registerUser">
                <label style = "font-size: 20px; font-weight: 600; ">Username</label>
                <input type = "text" placeholder="Username" required v-model = "username" class = "box"/><br/><br/>
                <label style = "font-size: 20px; font-weight: 600; ">Email</label>
                <input type = "email" placeholder="Email" required v-model = "email" class = "box"/><br/><br/> 
                <label style = "font-size: 20px; font-weight: 600; ">Password</label>
                <input type = "password" placeholder="Password" required v-model = "password" class = "box"/><br/><br/>
                <label style = "font-size: 20px; font-weight: 600; ">Full Name</label>
                <input type = "text" placeholder="Full Name" required v-model = "full_name" class = "box"/><br/><br/>
                <label style = "font-size: 20px; font-weight: 600; ">Address</label>
                <input type = "text" placeholder="Address" required v-model = "address" class = "box"/><br/><br/>
                <label style = "font-size: 20px; font-weight: 600; ">Pincode</label>
                <input type = "number" placeholder="pincode" required v-model = "pincode" class = "box"/><br/><br/>
                <button type = "submit" class = "btn btn-outline-primary ">Register</button>
                <a href = "/login" style="margin-left: 90px;" class = "no-style-link">Login</a>
            </form>
        </div>
        <div class="d-flex justify-content-center">
          <p class="text-danger">{{ message }}</p>
        </div>
    </div>
</template>

<script>
import api from '../../api/api.js'
import toastr from 'toastr';


toastr.options = {
  closeButton: true,
  progressBar: true,
  positionClass: "toast-top-right", // This puts it in the top right
  timeOut: "3000",                  // Toast disappears after 3s
};

export default {
    data() {
        return {
            username: '',
            password: '',
            full_name: '',
            address: '',
            pincode: '',
            email: ''
        }
    },

    methods: {
        async registerUser() {
            try {
                const response = await api.post('/register', {
                    username: this.username,
                    password: this.password,
                    full_name: this.full_name,
                    address: this.address,
                    pincode: this.pincode,
                    email: this.email
                })
                toastr.success(`${ this.full_name } registered successfully`)
                this.$router.push('/login')
            } catch (error) {
                this.message = error.response?.data?.message || 'Registration failed. Please try again.'
            }
        },
    },
}

</script>

<style scoped>
/* Container */
.login-container {
  width: 400px;
  margin: 50px auto;
  padding: 10px;
  border: 3px solid #3498db;
  border-radius: 20px;
  background-color: #ffffff;
  box-shadow: 0 0 15px rgba(0,0,0,0.1);
  transition: all 0.3s ease-in-out;
}
.login-container:hover {
  transform: scale(1.02);
  box-shadow: 0 0 20px rgba(52, 152, 219, 0.6);
}

/* Input Box */
.box {
  width: 300px;
  height: 45px;
  border: 2px solid #ccc;
  border-radius: 10px;
  text-align: center;
  font-size: 16px;
  outline: none;
  transition: all 0.3s ease-in-out;
  margin-top: 5px;
}

/* Input Focus Animation */
.box:focus {
  border-color: #3498db;
  box-shadow: 0 0 8px #3498db;
  background-color: #f9f9ff;
}

/* Label Animation */
label {
  display: block;
  font-size: 20px;
  font-weight: 600;
  margin-bottom: 5px;
  transition: all 0.2s ease-in-out;
}

/* Button Styling */
.btn-outline-primary {
  font-size: 16px;
  font-weight: 600;
  width: 120px;
  border-radius: 10px;
  padding: 8px;
}

.btn-outline-primary:hover {
  background-color: #3498db;
  color: #fff;
  transition: all 0.3s ease-in-out;
}

/* Register Link */
.no-style-link {
  text-decoration: none;
  font-weight: bold;
  color: #3498db;
}

.no-style-link:hover {
  text-decoration: underline;
  color: #1d6fa5;
}

/* Error Message */
.text-danger {
  font-weight: 600;
  animation: fadeIn 0.5s ease-in-out;
}

/* Subtle fade-in animation */
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}

</style>