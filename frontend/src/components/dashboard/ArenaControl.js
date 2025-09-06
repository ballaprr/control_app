import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  Slider,
  Grid,
  Alert,
  CircularProgress,
  Card,
  CardContent,
  CardActions,
  AppBar,
  Toolbar,
  IconButton,
} from '@mui/material';
import { ArrowBack, Brightness6, PowerSettingsNew, Settings } from '@mui/icons-material';
import { useParams, useNavigate } from 'react-router-dom';
import { arenaService } from '../../services/arena';
import { deviceService } from '../../services/device';
import { useAuth } from '../../contexts/AuthContext';

const ArenaControl = () => {
  const { arenaId } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();

  const [arena, setArena] = useState(null);
  const [devices, setDevices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [brightness, setBrightness] = useState(50);
  const [updating, setUpdating] = useState(false);

  useEffect(() => {
    loadArenaData();
    loadDevices();
  }, [arenaId]); // eslint-disable-line react-hooks/exhaustive-deps

  const loadArenaData = async () => {
    const result = await arenaService.getArena(arenaId);
    if (result.success) {
      setArena(result.data);
      setBrightness(result.data.brightness);
      
      // Check if user has control
      if (result.data.active_controller?.username !== user?.username) {
        setError('You do not have control of this arena');
      }
    } else {
      setError('Failed to load arena data');
    }
    setLoading(false);
  };

  const loadDevices = async () => {
    const result = await deviceService.getDevicesByArena(arenaId);
    if (result.success) {
      setDevices(result.data.devices || []);
    }
  };

  const handleBrightnessChange = async (event, newValue) => {
    setBrightness(newValue);
  };

  const handleBrightnessCommit = async (event, newValue) => {
    setUpdating(true);
    const result = await arenaService.updateBrightness(arenaId, newValue);
    if (result.success) {
      setArena(result.data.arena);
      setError('');
    } else {
      setError(result.error);
      setBrightness(arena.brightness); // Reset to original value
    }
    setUpdating(false);
  };

  const handleReleaseControl = async () => {
    const result = await arenaService.releaseControl(arenaId);
    if (result.success) {
      navigate('/dashboard');
    } else {
      setError(result.error);
    }
  };

  const handleDeviceReboot = async (deviceId) => {
    const result = await deviceService.rebootDevice(deviceId);
    if (result.success) {
      setError('');
      // You might want to show a success message
    } else {
      setError(result.error);
    }
  };

  const handleDeviceAction = async (deviceId, action) => {
    const result = await deviceService.triggerAction(deviceId, action);
    if (result.success) {
      setError('');
      // You might want to show a success message
    } else {
      setError(result.error);
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  const hasControl = arena?.active_controller?.username === user?.username;

  return (
    <Box>
      <AppBar position="static">
        <Toolbar>
          <IconButton
            edge="start"
            color="inherit"
            onClick={() => navigate('/dashboard')}
            sx={{ mr: 2 }}
          >
            <ArrowBack />
          </IconButton>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            {arena?.arena_name} Control Panel
          </Typography>
          {hasControl && (
            <Button color="inherit" onClick={handleReleaseControl}>
              Release Control
            </Button>
          )}
        </Toolbar>
      </AppBar>

      <Box sx={{ p: 3 }}>
        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        {!hasControl && (
          <Alert severity="warning" sx={{ mb: 3 }}>
            You do not have control of this arena. 
            {arena?.active_controller?.username && 
              ` Currently controlled by: ${arena.active_controller.username}`
            }
          </Alert>
        )}

        <Grid container spacing={3}>
          {/* Brightness Control */}
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 3 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Brightness6 sx={{ mr: 1 }} />
                <Typography variant="h6">Brightness Control</Typography>
              </Box>
              <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
                Current brightness: {brightness}%
              </Typography>
              <Slider
                value={brightness}
                onChange={handleBrightnessChange}
                onChangeCommitted={handleBrightnessCommit}
                min={0}
                max={100}
                disabled={!hasControl || updating}
                valueLabelDisplay="auto"
                sx={{ mt: 2 }}
              />
              {updating && (
                <Box sx={{ display: 'flex', justifyContent: 'center', mt: 2 }}>
                  <CircularProgress size={20} />
                </Box>
              )}
            </Paper>
          </Grid>

          {/* Arena Info */}
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Arena Information
              </Typography>
              <Typography variant="body2" sx={{ mb: 1 }}>
                <strong>Name:</strong> {arena?.arena_name}
              </Typography>
              <Typography variant="body2" sx={{ mb: 1 }}>
                <strong>Current Brightness:</strong> {arena?.brightness}%
              </Typography>
              <Typography variant="body2" sx={{ mb: 1 }}>
                <strong>Controller:</strong> {arena?.active_controller?.username || 'None'}
              </Typography>
              <Typography variant="body2">
                <strong>Total Devices:</strong> {(devices || []).length}
              </Typography>
            </Paper>
          </Grid>

          {/* Devices */}
          <Grid item xs={12}>
            <Typography variant="h6" gutterBottom>
              Devices ({(devices || []).length})
            </Typography>
            <Grid container spacing={2}>
              {(devices || []).map((device) => (
                <Grid item xs={12} sm={6} md={4} key={device.id}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6" component="h3">
                        {device.name}
                      </Typography>
                      <Typography variant="body2" color="textSecondary">
                        ID: {device.device_id}
                      </Typography>
                      <Typography variant="body2" color="textSecondary">
                        Position: {device.tile_label || 'Not assigned'}
                      </Typography>
                    </CardContent>
                    <CardActions>
                      <Button
                        size="small"
                        startIcon={<PowerSettingsNew />}
                        onClick={() => handleDeviceReboot(device.device_id)}
                        disabled={!hasControl}
                      >
                        Reboot
                      </Button>
                      <Button
                        size="small"
                        startIcon={<Settings />}
                        onClick={() => handleDeviceAction(device.device_id, 'configure')}
                        disabled={!hasControl}
                      >
                        Configure
                      </Button>
                    </CardActions>
                  </Card>
                </Grid>
              ))}
            </Grid>

            {(devices || []).length === 0 && (
              <Alert severity="info">
                No devices found for this arena.
              </Alert>
            )}
          </Grid>
        </Grid>
      </Box>
    </Box>
  );
};

export default ArenaControl;
