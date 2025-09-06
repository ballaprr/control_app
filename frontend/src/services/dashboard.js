import api from './api';

export const dashboardService = {
  // Get legend data for a specific setup
  async getLegendData(setupId) {
    try {
      const response = await api.get(`/fetch-legend-data/${setupId}/`);
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: error.response?.data };
    }
  },

  // Get device output for a specific tile
  async getDeviceOutput(tileIndex, arenaId) {
    try {
      const response = await api.get(`/device-output/${tileIndex}/`, {
        params: { arena_id: arenaId }
      });
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: error.response?.data };
    }
  },

  // Get device sensor data
  async getDeviceSensorData(tileIndex) {
    try {
      const response = await api.get(`/get-deviceid/${tileIndex}/`);
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: error.response?.data };
    }
  },

  // Trigger black screen for all devices
  async blackScreen() {
    try {
      const response = await api.post('/blackscreen/');
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: error.response?.data?.error || 'Failed to trigger black screen' };
    }
  },

  // Reboot specific device
  async rebootDevice(tileNumber) {
    try {
      const response = await api.post('/reboot-device/', {
        tile: tileNumber
      });
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: error.response?.data?.error || 'Failed to reboot device' };
    }
  },

  // Switch setup for all devices
  async switchSetup() {
    try {
      const response = await api.post('/switch-setup/');
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: error.response?.data?.error || 'Failed to switch setup' };
    }
  },

  // Trigger action on specific tiles (legacy - kept for compatibility)
  async triggerTileAction(tile, payload, arenaId) {
    try {
      const response = await api.post('/trigger-action/', {
        tile,
        payload,
        arena_id: arenaId
      });
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: error.response?.data?.error || 'Failed to trigger action' };
    }
  },

  // OPTIMIZED: Trigger action on entire zone (much faster!)
  async triggerZoneAction(zone, payload, arenaId) {
    try {
      const response = await api.post('/trigger-action/', {
        zone,  // Send zone instead of individual tiles
        payload,
        arena_id: arenaId
      });
      return { 
        success: true, 
        data: response.data,
        duration_ms: response.data?.duration_ms
      };
    } catch (error) {
      return { success: false, error: error.response?.data?.error || 'Failed to trigger zone action' };
    }
  },
};
