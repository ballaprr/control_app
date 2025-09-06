import api from './api';

export const deviceService = {
  // Get all devices
  async getDevices(arenaId = null) {
    try {
      const params = arenaId ? { arena_id: arenaId } : {};
      const response = await api.get('/devices/', { params });
      // Handle both paginated and non-paginated responses
      const data = response.data.results || response.data;
      return { success: true, data: Array.isArray(data) ? data : [] };
    } catch (error) {
      return { success: false, error: error.response?.data };
    }
  },

  // Get devices by arena
  async getDevicesByArena(arenaId) {
    try {
      const response = await api.get(`/devices/arena/${arenaId}/`);
      // Handle different response structures
      const devices = response.data.devices || response.data.results || response.data;
      return { success: true, data: { devices: Array.isArray(devices) ? devices : [] } };
    } catch (error) {
      return { success: false, error: error.response?.data };
    }
  },

  // Get specific device
  async getDevice(id) {
    try {
      const response = await api.get(`/devices/${id}/`);
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: error.response?.data };
    }
  },

  // Create new device
  async createDevice(deviceData) {
    try {
      const response = await api.post('/devices/', deviceData);
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, errors: error.response?.data };
    }
  },

  // Update device
  async updateDevice(id, deviceData) {
    try {
      const response = await api.patch(`/devices/${id}/`, deviceData);
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, errors: error.response?.data };
    }
  },

  // Delete device
  async deleteDevice(id) {
    try {
      await api.delete(`/devices/${id}/`);
      return { success: true };
    } catch (error) {
      return { success: false, error: error.response?.data };
    }
  },

  // Reboot device
  async rebootDevice(deviceId) {
    try {
      const response = await api.post('/devices/reboot/', { device_id: deviceId });
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: error.response?.data?.error || 'Failed to reboot device' };
    }
  },

  // Trigger device action
  async triggerAction(deviceId, action) {
    try {
      const response = await api.post('/devices/action/', { 
        device_id: deviceId, 
        action 
      });
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: error.response?.data?.error || 'Failed to trigger action' };
    }
  },
};
