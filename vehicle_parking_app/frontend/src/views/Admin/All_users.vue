<template>
  <div class="admin-dashboard text-white">
      <nav class="custom-navbar">
        <div class="navbar-logo">
          <span class="quick">Quick</span><span class="park">Park</span>
        </div>
        <ul class="navbar-menu">
          <li><a href="/admin/dashboard" class="nav-link">Home</a></li>
          <li><a href="/admin/users/show" class="nav-link active">Users</a></li>
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

      <div class="container py-4">
        <h2 class="mb-4 text-center">Registered Users</h2>
        
        <div class="search-container mb-4">
          <div class="input-group">
            <span class="input-group-text">
              <i class="bi bi-search"></i>
            </span>
            <input 
              type="text" 
              v-model="searchQuery" 
              placeholder="Search users by ID, name, or username..." 
              class="form-control search-input"
              @input="filterUsers"
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
              Showing {{ filteredUsers.length }} of {{ users.length }} users
            </small>
          </div>
        </div>
        
        <div class="table-responsive">
          <table class="table table-dark table-hover table-bordered rounded shadow">
            <thead class="table-primary text-dark">
              <tr>
                <th>ID</th>
                <th>Full Name</th>
                <th>Email</th>
                <th>Username</th>
                <th>Address</th>
                <th>Pincode</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="user in filteredUsers" :key="user.id">
                <td>{{ user.id }}</td>
                <td>{{ user.full_name }}</td>
                <td>{{ user.email }}</td>
                <td>{{ user.username }}</td>
                <td>{{ user.address }}</td>
                <td>{{ user.pincode }}</td>
                <td>
                  <button
                    class="btn btn-sm me-2"
                    :class="user.is_blocked ? 'btn-success' : 'btn-danger'"
                    @click="blockUser(user)"
                  >
                    {{ user.is_blocked ? 'Unblock' : 'Block' }}
                  </button>
                </td>
              </tr>
              <tr v-if="filteredUsers.length === 0">
                <td colspan="7" class="text-center">
                  no user
                </td>
              </tr>
            </tbody>
          </table>
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
      users: [],
      searchQuery: '',
      filteredUsers: []
    }
  },
  methods: {
    logout() {
      localStorage.removeItem('access_token')
      localStorage.removeItem('user_role')
      this.$router.push('/login')
    },
    async fetchUsers() {
      try {
        const res = await api.get('/admin/users/show')
        this.users = res.data.users
        this.filteredUsers = res.data.users // Initialize filteredUsers
      } catch (err) {
        // If the API returns a 404 (no users found), the user array will be empty
        // and the template will show the "no user" message.
        if (err.response && err.response.status === 404) {
          this.users = [];
          this.filteredUsers = [];
        } else {
          toastr.error('Failed to fetch users')
        }
      }
    },
    async blockUser(user) {
      try {
        if (user.is_blocked) {
          await api.post(`/admin/unblock/user/${user.id}`)
          user.is_blocked = false
          toastr.success('User unblocked')
        } else {
          await api.post(`/admin/block/user/${user.id}`)
          user.is_blocked = true
          toastr.success('User blocked')
        }
      } catch (err) {
        toastr.error('Failed to change block status')
      }
    },
    filterUsers() {
      this.filteredUsers = this.users.filter(user => {
        const idMatch = user.id.toString().includes(this.searchQuery)
        const nameMatch = user.full_name.toLowerCase().includes(this.searchQuery.toLowerCase())
        const usernameMatch = user.username.toLowerCase().includes(this.searchQuery.toLowerCase())
        return idMatch || nameMatch || usernameMatch
      })
    },
    clearSearch() {
      this.searchQuery = ''
      this.filteredUsers = this.users
    }
  },
  mounted() {
    this.fetchUsers()
  }
}
</script>

<style scoped>
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

.navbar-profile {
  /* Keep your profile dropdown styles here */
}

/* Search Bar Styles */
.search-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  margin-bottom: 20px;
  width: 100%;
}

.search-input {
  width: 100%;
  max-width: 600px;
  padding: 0.75rem 1rem;
  font-size: 1rem;
  border-radius: 0.5rem;
  border: 1px solid #3bb3ff;
  background-color: #222;
  color: #fff;
  margin: 0 auto;
}

.search-input:focus {
  background-color: #333;
  border-color: #3bb3ff;
  box-shadow: 0 0 0 0.25rem rgba(59, 179, 255, 0.25);
  color: #fff;
}

.search-results-info {
  font-size: 0.9rem;
  color: #888;
  text-align: center;
  margin-top: 10px;
}

</style>