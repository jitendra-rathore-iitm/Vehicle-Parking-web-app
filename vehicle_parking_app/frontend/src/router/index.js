import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import Register from '../views/User/Register.vue'
import HomePage from '../views/HomePage.vue'
// Admin
import AdminDashboard from '../views/Admin/AdminDashboard.vue'
import Add_parking_lot from '../views/Admin/Add_parking_lot.vue'
import Edit_parking_lot from '../views/Admin/Edit_parking_lot.vue'
import All_users from  '../views/Admin/All_users.vue'
import AdminSummary from '../views/Admin/Summary.vue'
//User
import UserDashboard from '../views/User/UserDashboard.vue'
import UserSummary from '../views/User/User_summary.vue'


function requireAuth(to, from, next){
  const token = localStorage.getItem('access_token')
  if (!token){
    next('/login')
  }else{
    next()
  }
}

function requireAdminAuth(to, from, next) {
  const token = localStorage.getItem('access_token')
  const role = localStorage.getItem('user_role')
  
  if (!token) {
    next('/login')
  } else if (role !== 'admin') {
    next('/user/dashboard')
  } else {
    next()
  }
}



const routes = [
  { path: '/', redirect: '/home' },
  { path: '/login', component: Login},
  { path: '/register', component: Register},
  { path: '/home', component: HomePage },
  { 
    path: '/admin/dashboard',
    component: AdminDashboard,
    beforeEnter: requireAdminAuth
  },
  { 
    path: '/admin/add/parkinglot',
    component: Add_parking_lot,
    beforeEnter: requireAdminAuth
  },
  { 
    path: '/admin/edit/parkinglot/:id',
    component: Edit_parking_lot,
    beforeEnter: requireAdminAuth
  },
  {
    path: '/admin/users/show',
    component: All_users,
    beforeEnter: requireAdminAuth
  },
  {
    path: '/admin/summary',
    component: AdminSummary,
    beforeEnter: requireAdminAuth
  },
  {
    path: '/admin/edit-profile',
    name: 'AdminEditProfile',
    component: () => import('../views/EditProfile.vue'),
    beforeEnter: requireAdminAuth 
  },
  { 
    path: '/user/dashboard',
    component: UserDashboard,
    beforeEnter: requireAuth 
  },
  {
    path: '/user/summary',
    component: UserSummary,
    beforeEnter: requireAuth
  },
  {
    path: '/user/edit-profile',
    name: 'UserEditProfile',
    component: () => import('../views/EditProfile.vue'),
    beforeEnter: requireAuth 
  }

]

const router = createRouter({
  history: createWebHistory(),
  routes,
});

function logout() {
  localStorage.removeItem('access_token')
  localStorage.removeItem('user_role')
  router.push('/login')
}

export default router
