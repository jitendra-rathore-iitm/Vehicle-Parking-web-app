<template>
    <div class = "login-container">
        <h2 style = "text-align: center;">Login</h2><br/><br/>
        <div style = "text-align: center;">
            <form @submit.prevent = "login">
                <label style = "font-size: 20px; font-weight: 600; ">Username</label><br/>
                <input type = "text" placeholder="Username" required v-model = "username" class = "box" /><br/><br/>
                <label style = "font-size: 20px; font-weight: 600; ">Password</label><br/>
                <input type = "password" placeholder="Password" required v-model = "password" class = "box" /><br/><br/>
                <button type = "submit" class = "btn btn-outline-primary ">Login</button>
                <a class = "no-style-link" href = "/register" style="margin-left: 30px;">Create account</a>
            </form>
        </div>
        <br/>
        <div class="d-flex justify-content-center">
            <p class = "text-danger" > {{ message }}</p>
        </div>
    </div>
</template>

<script>
import api from '../api/api.js'
import toastr from "toastr";


toastr.options = {
  closeButton: true,
  progressBar: true,
  positionClass: "toast-top-right", // This puts it in the top right
  timeOut: "3000",                  // Toast disappears after 3s
};


export default{
    data() {
        return {
            username: '',
            password: '',
            message: ''
        }
    },
    methods: {
        async login(){
            try {
                const response = await api.post('/login',{
                    username: this.username,
                    password: this.password
                })
                const { role, access_token } = response.data
    
                localStorage.setItem('access_token', access_token)
                localStorage.setItem('user_role', role) // Store role
                localStorage.setItem('username', this.username) // Store username too

                if (role === 'admin'){
                    toastr.success(`${ this.username } Signed in successfully!`)
                    this.$router.push('/admin/dashboard')
                }else if(role === 'user'){
                    toastr.success(` ${ this.username } signed in successfully`)
                    this.$router.push('/user/dashboard')
                }else{
                    this.message = "Login Failed"
                }
            } catch (error){
                this.message = error.response?.data?.message || 'Login Failed'
            }

        }
    }


}

</script>

<style scoped>

/* Container */
.login-container {
  width: 400px;
  margin: 150px auto;
  padding: 30px;
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