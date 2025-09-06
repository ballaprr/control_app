import api from './api';

export const authService = {
  // Login user
  async login(email, password) {
    try {
      const response = await api.post('/auth/login/', {
        email,
        password,
      });

      const { access, refresh, user } = response.data;
      
      // Store tokens and user data
      localStorage.setItem('access_token', access);
      localStorage.setItem('refresh_token', refresh);
      localStorage.setItem('user', JSON.stringify(user));

      return { success: true, user };
    } catch (error) {
      const message = error.response?.data?.non_field_errors?.[0] || 
                     error.response?.data?.email?.[0] || 
                     error.response?.data?.password?.[0] || 
                     'Login failed. Please try again.';
      return { success: false, error: message };
    }
  },

  // Register user
  async register(userData) {
    try {
      const response = await api.post('/auth/register/', userData);
      return { success: true, data: response.data };
    } catch (error) {
      const errors = error.response?.data || {};
      return { success: false, errors };
    }
  },

  // Logout user
  async logout() {
    try {
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        await api.post('/auth/logout/', {
          refresh: refreshToken,
        });
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      // Clear local storage regardless of API call success
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user');
    }
  },

  // Get current user from localStorage
  getCurrentUser() {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  },

  // Check if user is authenticated
  isAuthenticated() {
    const token = localStorage.getItem('access_token');
    const user = this.getCurrentUser();
    return !!(token && user);
  },

  // Get user profile
  async getProfile() {
    try {
      const response = await api.get('/auth/profile/');
      const user = response.data;
      localStorage.setItem('user', JSON.stringify(user));
      return { success: true, user };
    } catch (error) {
      return { success: false, error: error.response?.data };
    }
  },

  // Update user profile
  async updateProfile(userData) {
    try {
      const response = await api.patch('/auth/profile/', userData);
      const user = response.data;
      localStorage.setItem('user', JSON.stringify(user));
      return { success: true, user };
    } catch (error) {
      return { success: false, errors: error.response?.data };
    }
  },

  // Change password
  async changePassword(passwordData) {
    try {
      const response = await api.post('/auth/change-password/', passwordData);
      return { success: true, message: response.data.message };
    } catch (error) {
      return { success: false, errors: error.response?.data };
    }
  },

  // Forgot password
  async forgotPassword(email) {
    try {
      const response = await api.post('/auth/forgot-password/', { email });
      return { success: true, message: response.data.message };
    } catch (error) {
      return { success: false, error: error.response?.data?.email?.[0] || 'An error occurred' };
    }
  },
};
