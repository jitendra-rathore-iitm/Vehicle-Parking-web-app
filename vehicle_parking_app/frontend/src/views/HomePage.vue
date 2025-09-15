<template>
  <div class="home-page d-flex flex-column justify-content-center align-items-center text-center text-white ">
    <div class="container">
      <h1 class="display-3 mb-3 animate__animated animate__fadeInDown">Welcome to Quick Park</h1>
      <p class="lead mb-4 animate__animated animate__fadeInUp">
        Reserve your parking space with ease and manage everything on your dashboard.
      </p>
      <div class="d-flex justify-content-center gap-3">
        <router-link to="/login" class="btn btn-outline-light btn-lg">Login</router-link>
        <router-link to="/register" class="btn btn-light btn-lg text-primary">Register</router-link>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'HomePage'
}
</script>

<style scoped>
@import 'https://cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css';

.home-page {
  height: 100vh;
  /* background: linear-gradient(to right, #0fa2a9, #1d7bba); */
  background: linear-gradient(to right, #2e60dd, #078bd2);
  padding: 20px;
}

.btn:hover {
  transform: scale(1.05);
  transition: all 0.3s ease-in-out;
}
</style>


