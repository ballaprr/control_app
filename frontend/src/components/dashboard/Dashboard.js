import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Grid,
  Typography,
  Button,
  AppBar,
  Toolbar,
  IconButton,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableRow,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  CircularProgress,
  Chip,
} from '@mui/material';
import { ArrowBack, Refresh, PowerSettingsNew } from '@mui/icons-material';
import { useParams, useNavigate } from 'react-router-dom';
import { arenaService } from '../../services/arena';
import { deviceService } from '../../services/device';
import { dashboardService } from '../../services/dashboard';
import { useAuth } from '../../contexts/AuthContext';

const Dashboard = () => {
  const { arenaId } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();

  const [arena, setArena] = useState(null);
  const [devices, setDevices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [currentTime, setCurrentTime] = useState('');
  const [selectedTile, setSelectedTile] = useState(null);
  const [currentView, setCurrentView] = useState({});
  const [previewView, setPreviewView] = useState({});
  const [legendData, setLegendData] = useState([]);
  const [selectedSetup, setSelectedSetup] = useState('254745');
  const [deviceInfo, setDeviceInfo] = useState(null);
  const [loadingAction, setLoadingAction] = useState(false);
  
  // Keyboard navigation state
  const [keyBuffer, setKeyBuffer] = useState('');
  const [firstParam, setFirstParam] = useState(''); // Zone (0, a, b, c, d, e)
  const [secondParam, setSecondParam] = useState(''); // Activation (1-24)
  const [selectedTiles, setSelectedTiles] = useState(new Set());
  const [fgSequence, setFgSequence] = useState(false);

  // Create tile grid (A1-A14)
  const tileRange = Array.from({ length: 14 }, (_, i) => i + 1);

  // Calculate if user has control
  const hasControl = arena?.active_controller?.username === user?.username;

  useEffect(() => {
    loadArenaData();
    loadDevices();
    loadLegendData();
    loadCurrentView(); // Load current device outputs
    updateTime();
    const timer = setInterval(updateTime, 1000);
    return () => clearInterval(timer);
  }, [arenaId]);

  useEffect(() => {
    if (selectedSetup) {
      loadLegendData();
    }
  }, [selectedSetup]);

  // Keyboard event listener
  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => {
    const handleKeyPress = (event) => {
      if (!hasControl) return; // Only allow keyboard input if user has control
      
      // Handle 'z' reset first, before any other processing
      if (event.key === 'z') {
        // Clear both parameters and reset state
        setFirstParam('');
        setSecondParam('');
        setSelectedTiles(new Set());
        setPreviewView({});
        setKeyBuffer('');
        console.log('Reset: Cleared both parameters and state');
        return; // Exit early to prevent further processing
      }
      
      let newKeyBuffer = keyBuffer;
      
      if (event.key.length === 1 || event.key === 'Enter') {
        newKeyBuffer += event.key;
        setKeyBuffer(newKeyBuffer);
      }

      // Tile group mapping
      const keyToTileGroupMap = {
        '0': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14],  // All tiles
        'a': [1, 2, 3, 4],    // Tiles A1 to A4
        'b': [6, 7, 8, 9],    // Tiles A6 to A9
        'c': [11, 12, 13, 14], // Tiles A11 to A14
        'd': [1, 2, 3, 4, 5, 6, 7], // Tiles A1 to A7
        'e': [8, 9, 10, 11, 12, 13, 14] // Tiles A8 to A14
      };

      // Handle zone selection (first parameter)
      if (['0', 'a', 'b', 'c', 'd', 'e'].includes(newKeyBuffer)) {
        setFirstParam(newKeyBuffer);
        const tileIndices = keyToTileGroupMap[newKeyBuffer];
        setSelectedTiles(new Set(tileIndices));
        updatePreviewTiles(tileIndices, secondParam);
        setKeyBuffer('');
      }

      // Handle activation selection (second parameter)
      const validSecondParams = Array.from({length: 24}, (_, i) => String(i + 1));
      if (validSecondParams.includes(newKeyBuffer)) {
        setSecondParam(newKeyBuffer);
        updatePreviewTiles(Array.from(selectedTiles), newKeyBuffer);
        setKeyBuffer('');
      }

      // Special key handlers

      if (event.key === 'm') {
        handleBlackScreenAll();
        setKeyBuffer('');
      }

      if (event.key === 'i') {
        const tileNumber = prompt("Enter tile number (e.g., 1, 2, ..., 14):");
        if (tileNumber && !isNaN(tileNumber)) {
          const tileIndex = parseInt(tileNumber, 10);
          if (tileIndex >= 1 && tileIndex <= 14) {
            handleTileClick(tileIndex);
          }
        }
        setKeyBuffer('');
      }

      if (event.key === 'f') {
        setFgSequence(true);
        setKeyBuffer('');
        return;
      }

      if (fgSequence && event.key === 'g') {
        setFgSequence(false);
        const tileNumber = prompt("Enter tile number (e.g., 1, 2, ..., 14):");
        if (tileNumber && !isNaN(tileNumber)) {
          handleRebootDevice(parseInt(tileNumber, 10));
        }
        setKeyBuffer('');
      }

      if (event.key === 's') {
        handleSwitchSetup();
        setKeyBuffer('');
      }

      // Apply changes when Enter is pressed
      if (event.key === 'Enter') {
        if (firstParam && secondParam) {
          handleTriggerAction(firstParam, secondParam);
        }
        setKeyBuffer('');
      }

      // Limit buffer length
      if (newKeyBuffer.length > 2) {
        setKeyBuffer(newKeyBuffer.slice(-2));
      }
    };

    document.addEventListener('keydown', handleKeyPress);
    return () => document.removeEventListener('keydown', handleKeyPress);
  }, [keyBuffer, firstParam, secondParam, selectedTiles, fgSequence, hasControl]);

  const updateTime = () => {
    const now = new Date();
    setCurrentTime(now.toLocaleTimeString('en-US', { hour12: false }));
  };

  const loadArenaData = useCallback(async () => {
    const result = await arenaService.getArena(arenaId);
    if (result.success) {
      setArena(result.data);
      
      // Check if user has control
      if (result.data.active_controller?.username !== user?.username) {
        setError('You do not have control of this arena. Click "Take Control" to begin.');
      }
    } else {
      setError('Failed to load arena data');
    }
    setLoading(false);
  }, [arenaId, user?.username]);

  const loadDevices = useCallback(async () => {
    const result = await deviceService.getDevicesByArena(arenaId);
    if (result.success) {
      setDevices(result.data.devices || []);
    }
  }, [arenaId]);

  const loadLegendData = useCallback(async () => {
    if (selectedSetup) {
      const result = await dashboardService.getLegendData(selectedSetup);
      if (result.success) {
        setLegendData(Array.isArray(result.data) ? result.data : []);
      }
    }
  }, [selectedSetup]);

  const loadCurrentView = useCallback(async () => {
    // Load current device outputs for all tiles
    console.log('Loading current view...');
    const currentViewData = {};
    for (let i = 1; i <= 14; i++) {
      try {
        const result = await dashboardService.getDeviceOutput(i, arenaId);
        console.log(`Tile ${i} result:`, result);
        if (result.success && result.data?.src) {
          currentViewData[i] = result.data.src;
          console.log(`Tile ${i} loaded successfully with src: ${result.data.src?.substring(0, 50)}...`);
        } else {
          console.log(`Tile ${i} - no data or error:`, result);
        }
      } catch (error) {
        console.error(`Failed to load tile ${i}:`, error);
      }
    }
    console.log('Final currentViewData:', Object.keys(currentViewData));
    setCurrentView(currentViewData);
  }, [arenaId]);

  const updatePreviewTiles = (tileIndices, activation) => {
    const newPreviewView = { ...previewView };
    
    // Clear all preview tiles first
    for (let i = 1; i <= 14; i++) {
      delete newPreviewView[i];
    }

    if (activation && legendData.length > 0) {
      // Filter legend data by activation trigger
      const filteredLegendData = legendData.filter(item => String(item.trigger) === activation);
      
      tileIndices.forEach((tileIndex, idx) => {
        if (filteredLegendData.length > 0) {
          const legendItem = filteredLegendData[idx % filteredLegendData.length];
          if (legendItem?.thumb) {
            newPreviewView[tileIndex] = legendItem.thumb;
          }
        }
      });
    }
    
    setPreviewView(newPreviewView);
  };

  // Optimized function to update only specific tiles after trigger
  const updateTriggeredTiles = async (tileNumbers) => {
    const updatePromises = tileNumbers.map(async (tileNumber) => {
      try {
        const result = await dashboardService.getDeviceOutput(tileNumber, arenaId);
        if (result.success && result.data?.src) {
          setCurrentView(prev => ({
            ...prev,
            [tileNumber]: result.data.src
          }));
        }
      } catch (error) {
        console.error(`Failed to update tile ${tileNumber}:`, error);
      }
    });
    
    // Execute all updates in parallel
    await Promise.allSettled(updatePromises);
  };

  const handleTriggerAction = async (zone, activation) => {
    const startTime = performance.now();
    console.log(`🚀 Starting trigger action for zone ${zone}, activation ${activation}`);
    setLoadingAction(true);
    
    // Get tile numbers for the zone
    const keyToTileGroupMap = {
      '0': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14],  // All tiles
      'a': [1, 2, 3, 4],    // Tiles A1 to A4
      'b': [6, 7, 8, 9],    // Tiles A6 to A9
      'c': [11, 12, 13, 14], // Tiles A11 to A14
      'd': [1, 2, 3, 4, 5, 6, 7], // Tiles A1 to A7
      'e': [8, 9, 10, 11, 12, 13, 14] // Tiles A8 to A14
    };
    
    const tileNumbers = keyToTileGroupMap[zone];
    if (!tileNumbers) {
      setError(`Invalid zone: ${zone}`);
      setLoadingAction(false);
      return;
    }
    
    // Filter to only tiles that have registered devices (from devices state)
    const tilesWithDevices = tileNumbers.filter(tileNumber => {
      return devices.some(device => device.tile_label === `A${tileNumber}`);
    });
    
    if (tilesWithDevices.length === 0) {
      setError('No devices registered for selected zone');
      setLoadingAction(false);
      return;
    }
    
    // OPTIMIZED: Single API call per zone instead of multiple tile calls
    try {
      console.log(`📡 Sending zone trigger: zone=${zone}, activation=${activation}, devices=${tilesWithDevices.length}`);
      const result = await dashboardService.triggerZoneAction(zone, activation, arenaId);
      
      if (result.success) {
        console.log(`⚡ Zone ${zone} triggered in ${result.duration_ms?.toFixed(2) || 'N/A'}ms`);
        setError('');
        // Update only the tiles that were actually triggered
        updateTriggeredTiles(tilesWithDevices);
      } else {
        setError(result.error || 'Failed to trigger zone action');
      }
    } catch (error) {
      setError(`Failed to trigger zone action: ${error.message}`);
    }
    
    const endTime = performance.now();
    console.log(`✅ Trigger action completed in ${(endTime - startTime).toFixed(2)}ms`);
    setLoadingAction(false);
  };

  const handleBlackScreenAll = async () => {
    setLoadingAction(true);
    const result = await dashboardService.blackScreen();
    if (result.success) {
      await loadCurrentView();
      setError('');
    } else {
      setError(result.error);
    }
    setLoadingAction(false);
  };

  const handleRebootDevice = async (tileNumber) => {
    setLoadingAction(true);
    const result = await dashboardService.rebootDevice(tileNumber);
    if (result.success) {
      setError('');
    } else {
      setError(result.error);
    }
    setLoadingAction(false);
  };

  const handleSwitchSetup = async () => {
    setLoadingAction(true);
    const result = await dashboardService.switchSetup();
    if (result.success) {
      setError('');
    } else {
      setError(result.error);
    }
    setLoadingAction(false);
  };

  const handleTileClick = async (tileNumber) => {
    setSelectedTile(tileNumber);
    
    // Find device for this tile
    const device = (devices || []).find(d => d.tile_label === `A${tileNumber}`);
    if (device) {
      // Fetch device sensor data
      const sensorResult = await dashboardService.getDeviceSensorData(tileNumber);
      setDeviceInfo({
        tile: `A${tileNumber}`,
        device_id: device.device_id,
        name: device.name,
        status: 'Active',
        sensorData: sensorResult.success ? sensorResult.data : null
      });
    }
  };


  const handleSingleTileAction = async (tile, payload) => {
    const device = (devices || []).find(d => d.tile_label === `A${tile}`);
    if (device) {
      const result = await deviceService.triggerAction(device.device_id, payload);
      if (result.success) {
        setError('');
        // Update current view after action
        await loadCurrentView();
      } else {
        setError(result.error);
      }
    }
  };

  const handleReleaseControl = async () => {
    const result = await arenaService.releaseControl(arenaId);
    if (result.success) {
      navigate('/dashboard');
    } else {
      setError(result.error);
    }
  };



  const TileGrid = ({ title, viewType, onTileClick }) => {
    const viewData = viewType === 'current' ? currentView : previewView;
    
    return (
      <Paper sx={{ p: 2, mb: 3 }}>
        <Typography variant="h6" gutterBottom align="center">
          {title}
        </Typography>
        <Box
          sx={{
            display: 'grid',
            gridTemplateColumns: 'repeat(14, 1fr)',
            gap: 1,
            border: '1px solid #ccc',
            p: 2,
            minHeight: '150px',
          }}
        >
          {tileRange.map((tileNum) => {
            const device = (devices || []).find(d => d.tile_label === `A${tileNum}`);
            const isSelected = selectedTiles.has(tileNum) && viewType === 'preview';
            const hasDevice = !!device;
            const tileImage = viewData[tileNum];
            
            return (
              <Box key={tileNum} sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                <Typography variant="caption" sx={{ fontWeight: 'bold', mb: 0.5 }}>
                  A{tileNum}
                </Typography>
                <Box
                  sx={{
                    width: 60,
                    height: 60,
                    backgroundColor: isSelected ? '#ffeb3b' : '#e0e0e0',
                    border: hasDevice ? '2px solid #4caf50' : '1px solid #ccc',
                    cursor: hasDevice && onTileClick ? 'pointer' : 'default',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    borderRadius: 1,
                    backgroundImage: tileImage ? `url(${tileImage})` : 'none',
                    backgroundSize: 'cover',
                    backgroundPosition: 'center',
                    '&:hover': hasDevice && onTileClick ? { opacity: 0.8 } : {},
                  }}
                  onClick={() => hasDevice && onTileClick && onTileClick(tileNum)}
                >
                  {!tileImage && hasDevice && (
                    <Typography variant="caption" color="textSecondary" sx={{ fontWeight: 'bold' }}>
                      A{tileNum}
                    </Typography>
                  )}
                  {!hasDevice && (
                    <Typography variant="caption" color="textSecondary" sx={{ fontSize: '10px' }}>
                      No Device
                    </Typography>
                  )}
                </Box>
              </Box>
            );
          })}
        </Box>
      </Paper>
    );
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

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
            {arena?.arena_name} - Control Dashboard
          </Typography>
          <Typography variant="body2" sx={{ mr: 2 }}>
            {currentTime}
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
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Box>
                You do not have control of this arena.
                {arena?.active_controller?.username ? 
                  ` Currently controlled by: ${arena.active_controller.username}` :
                  ' This arena is available.'
                }
              </Box>
              {!arena?.active_controller?.username && (
                <Button
                  variant="contained"
                  size="small"
                  onClick={async () => {
                    const result = await arenaService.takeControl(arenaId);
                    if (result.success) {
                      loadArenaData(); // Reload to update control status
                      setError('');
                    } else {
                      setError(result.error);
                    }
                  }}
                >
                  Take Control
                </Button>
              )}
            </Box>
          </Alert>
        )}

        {/* Header Info */}
        <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Box>
            <Typography variant="h5" gutterBottom>
              Control Dashboard
            </Typography>
            <Box sx={{ display: 'flex', gap: 4 }}>
              <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                Zone: {firstParam || 'None'}
              </Typography>
              <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                Activation: {secondParam || 'None'}
              </Typography>
            </Box>
          </Box>
          <Box sx={{ textAlign: 'right' }}>
            <Chip 
              label={`Controller: ${arena?.active_controller?.username || 'None'}`}
              color={hasControl ? 'primary' : 'default'}
            />
          </Box>
        </Box>

        {/* Keyboard Instructions */}
        {hasControl && (
          <Alert severity="info" sx={{ mb: 3 }}>
            <Typography variant="subtitle2" gutterBottom>
              Keyboard Controls:
            </Typography>
            <Typography variant="body2">
              <strong>Zone Selection:</strong> 0 (all), a (A1-A4), b (A6-A9), c (A11-A14), d (A1-A7), e (A8-A14) |{' '}
              <strong>Activation:</strong> 1-24 |{' '}
              <strong>Apply:</strong> Enter |{' '}
              <strong>Clear:</strong> z |{' '}
              <strong>Special:</strong> m (black screen), i (device info), f+g (reboot), s (switch setup)
            </Typography>
          </Alert>
        )}

        {/* Current View */}
        <TileGrid 
          title="Current View"
          viewType="current"
          onTileClick={hasControl ? handleTileClick : null}
        />

        {/* Preview View */}
        <TileGrid 
          title="Preview View"
          viewType="preview"
          onTileClick={hasControl ? handleTileClick : null}
        />

        {/* Legend Section */}
        <Paper sx={{ p: 2, mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            Legend
          </Typography>
          
          <Box sx={{ mb: 2, display: 'flex', gap: 2, alignItems: 'center' }}>
            <Button
              variant="contained"
              startIcon={<Refresh />}
              onClick={loadLegendData}
              disabled={!hasControl}
            >
              Update Legend
            </Button>
            
            <FormControl size="small" sx={{ minWidth: 200 }}>
              <InputLabel>Setup</InputLabel>
              <Select
                value={selectedSetup}
                onChange={(e) => setSelectedSetup(e.target.value)}
                label="Setup"
                disabled={!hasControl}
              >
                <MenuItem value="254745">Main Setup</MenuItem>
                <MenuItem value="257842">Backup Setup</MenuItem>
              </Select>
            </FormControl>
          </Box>

          {/* Legend Table */}
          <Box sx={{ overflowX: 'auto' }}>
            <Table size="small">
              <TableBody>
                {/* Triggers Row */}
                <TableRow>
                  {legendData.map((item, index) => {
                    const triggersToReplace = ['59', '60', '61', '62'];
                    const displayTrigger = triggersToReplace.includes(String(item.trigger)) ? '20' : item.trigger;
                    return (
                      <TableCell key={index} align="center">
                        <Typography variant="caption" fontWeight="bold">
                          {displayTrigger || index + 1}
                        </Typography>
                      </TableCell>
                    );
                  })}
                </TableRow>
                
                {/* Thumbnails Row */}
                <TableRow>
                  {legendData.map((item, index) => (
                    <TableCell key={index} align="center">
                      {item.thumb ? (
                        <img 
                          src={item.thumb} 
                          alt="Thumbnail" 
                          style={{ width: 80, height: 'auto', maxHeight: 60 }}
                        />
                      ) : (
                        <Typography variant="caption" color="textSecondary">
                          No thumbnail
                        </Typography>
                      )}
                    </TableCell>
                  ))}
                </TableRow>
              </TableBody>
            </Table>
          </Box>
        </Paper>

        {/* Device Details Section */}
        {selectedTile && (
          <Paper sx={{ p: 2, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Device Details - Tile A{selectedTile}
            </Typography>
            
            {deviceInfo ? (
              <Grid container spacing={2}>
                <Grid item xs={12} md={6}>
                  <Typography variant="body2">
                    <strong>Device ID:</strong> {deviceInfo.device_id}
                  </Typography>
                  <Typography variant="body2">
                    <strong>Name:</strong> {deviceInfo.name}
                  </Typography>
                  <Typography variant="body2">
                    <strong>Status:</strong> {deviceInfo.status}
                  </Typography>
                  
                  {deviceInfo.sensorData && (
                    <Box sx={{ mt: 2 }}>
                      <Typography variant="subtitle2" gutterBottom>
                        Sensor Data:
                      </Typography>
                      <Typography variant="caption" display="block">
                        CPU Idle: {deviceInfo.sensorData['cpu idle']}%
                      </Typography>
                      <Typography variant="caption" display="block">
                        FPS: {deviceInfo.sensorData.fps}
                      </Typography>
                      <Typography variant="caption" display="block">
                        Temperature: {deviceInfo.sensorData['PI CPU temperature']}°C
                      </Typography>
                      <Typography variant="caption" display="block">
                        Network IP: {deviceInfo.sensorData['network ip address']}
                      </Typography>
                    </Box>
                  )}
                </Grid>
                <Grid item xs={12} md={6}>
                  <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                    <Button
                      variant="outlined"
                      size="small"
                      startIcon={<PowerSettingsNew />}
                      onClick={() => handleRebootDevice(selectedTile)}
                      disabled={!hasControl}
                    >
                      Reboot
                    </Button>
                    <Button
                      variant="outlined"
                      size="small"
                      onClick={() => handleSingleTileAction(selectedTile, 'm')}
                      disabled={!hasControl}
                    >
                      Black Screen
                    </Button>
                    <Button
                      variant="outlined"
                      size="small"
                      onClick={() => handleTileClick(selectedTile)}
                    >
                      Refresh Data
                    </Button>
                  </Box>
                </Grid>
              </Grid>
            ) : (
              <Typography variant="body2" color="textSecondary">
                No device assigned to this tile
              </Typography>
            )}
          </Paper>
        )}

        {/* Control Actions */}
        {hasControl && (
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Quick Actions
            </Typography>
            <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
              <Button
                variant="contained"
                color="warning"
                onClick={handleBlackScreenAll}
                disabled={loadingAction}
              >
                {loadingAction ? 'Processing...' : 'Black Screen All'}
              </Button>
              <Button
                variant="contained"
                color="primary"
                onClick={handleSwitchSetup}
                disabled={loadingAction}
              >
                {loadingAction ? 'Processing...' : 'Switch Setup'}
              </Button>
              <Button
                variant="outlined"
                onClick={() => {
                  loadDevices();
                  loadLegendData();
                }}
              >
                Refresh All Data
              </Button>
            </Box>
          </Paper>
        )}
      </Box>
    </Box>
  );
};

export default Dashboard;
