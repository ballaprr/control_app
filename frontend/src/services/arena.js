import api from './api';

export const arenaService = {
  // Get all arenas
  async getArenas() {
    try {
      const response = await api.get('/arenas/');
      // Handle both paginated and non-paginated responses
      const data = response.data.results || response.data;
      return { success: true, data: Array.isArray(data) ? data : [] };
    } catch (error) {
      return { success: false, error: error.response?.data };
    }
  },

  // Get specific arena
  async getArena(id) {
    try {
      const response = await api.get(`/arenas/${id}/`);
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: error.response?.data };
    }
  },

  // Create new arena
  async createArena(arenaData) {
    try {
      const response = await api.post('/arenas/', arenaData);
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, errors: error.response?.data };
    }
  },

  // Update arena
  async updateArena(id, arenaData) {
    try {
      const response = await api.patch(`/arenas/${id}/`, arenaData);
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, errors: error.response?.data };
    }
  },

  // Delete arena
  async deleteArena(id) {
    try {
      await api.delete(`/arenas/${id}/`);
      return { success: true };
    } catch (error) {
      return { success: false, error: error.response?.data };
    }
  },

  // Take control of arena
  async takeControl(arenaId) {
    try {
      const response = await api.post(`/arenas/${arenaId}/take-control/`);
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: error.response?.data?.error || 'Failed to take control' };
    }
  },

  // Release control of arena
  async releaseControl(arenaId) {
    try {
      const response = await api.post(`/arenas/${arenaId}/release-control/`);
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: error.response?.data?.error || 'Failed to release control' };
    }
  },

  // Update arena brightness
  async updateBrightness(arenaId, brightness) {
    try {
      const response = await api.put(`/arenas/${arenaId}/brightness/`, { brightness });
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: error.response?.data?.error || 'Failed to update brightness' };
    }
  },
};
