import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  CardActions,
  Typography,
  Button,
  Grid,
  Alert,
  CircularProgress,
  Chip,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Container,
  Paper,
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { arenaService } from '../../services/arena';
import { useAuth } from '../../contexts/AuthContext';

const ArenaSelection = () => {
  const [arenas, setArenas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedArenaId, setSelectedArenaId] = useState('');
  const [takingControl, setTakingControl] = useState(false);

  const { user } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    loadArenas();
  }, []);

  const loadArenas = async () => {
    setLoading(true);
    const result = await arenaService.getArenas();
    if (result.success) {
      setArenas(Array.isArray(result.data) ? result.data : []);
    } else {
      setError('Failed to load arenas');
    }
    setLoading(false);
  };

  const handleContinue = async () => {
    if (!selectedArenaId) {
      setError('Please select an arena');
      return;
    }

    setTakingControl(true);
    
    // Find the selected arena to check its status
    const selectedArena = arenas.find(arena => arena.id === parseInt(selectedArenaId));
    
    // Debug logging
    console.log('User object:', user);
    console.log('Selected arena:', selectedArena);
    console.log('Arena controller:', selectedArena?.active_controller_username);
    console.log('User username:', user?.username);
    console.log('Comparison result:', selectedArena?.active_controller_username === user?.username);
    
    // Check if current user is the controller using multiple possible username fields
    const currentUsernames = [user?.username, user?.email?.split('@')[0]];
    const isCurrentUserController = currentUsernames.includes(selectedArena?.active_controller_username);
    
    if (isCurrentUserController) {
      // User already has control, go directly to dashboard
      console.log('User has control, navigating to dashboard');
      navigate(`/arena/${selectedArenaId}/dashboard`);
    } else if (selectedArena?.active_controller_username) {
      // Arena is controlled by someone else
      console.log('Arena controlled by someone else');
      setError(`Arena is currently controlled by ${selectedArena.active_controller_username}. Your username: ${user?.username}`);
    } else {
      // Arena is available, take control and go to dashboard
      console.log('Arena available, taking control');
      const result = await arenaService.takeControl(selectedArenaId);
      if (result.success) {
        navigate(`/arena/${selectedArenaId}/dashboard`);
      } else {
        setError(result.error);
      }
    }
    
    setTakingControl(false);
  };

  if (loading) {
    return (
      <Container maxWidth="sm" sx={{ mt: 8 }}>
        <Box sx={{ display: 'flex', justifyContent: 'center' }}>
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="sm" sx={{ mt: 8 }}>
      <Paper elevation={3} sx={{ p: 4 }}>
        <Typography variant="h4" gutterBottom align="center">
          Select an Arena
        </Typography>
        
        <Typography variant="body1" color="textSecondary" align="center" sx={{ mb: 3 }}>
          Welcome, {user?.first_name}! Choose an arena to control.
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        <Box component="form" onSubmit={(e) => { e.preventDefault(); handleContinue(); }}>
          <FormControl fullWidth sx={{ mb: 3 }}>
            <InputLabel id="arena-select-label">Choose an arena:</InputLabel>
            <Select
              labelId="arena-select-label"
              id="arena-select"
              value={selectedArenaId}
              label="Choose an arena:"
              onChange={(e) => {
                setSelectedArenaId(e.target.value);
                setError(''); // Clear any previous errors
              }}
            >
              {(arenas || []).map((arena) => (
                <MenuItem key={arena.id} value={arena.id}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', width: '100%', alignItems: 'center' }}>
                    <Typography>{arena.arena_name}</Typography>
                    <Box sx={{ ml: 2 }}>
                      {arena.active_controller_username ? (
                        <Chip
                          label={arena.active_controller_username === user?.username ? 'You' : arena.active_controller_username}
                          color={arena.active_controller_username === user?.username ? 'primary' : 'default'}
                          size="small"
                        />
                      ) : (
                        <Chip
                          label="Available"
                          color="success"
                          size="small"
                        />
                      )}
                    </Box>
                  </Box>
                </MenuItem>
              ))}
              {arenas.length === 0 && (
                <MenuItem disabled>No arenas available</MenuItem>
              )}
            </Select>
          </FormControl>

          <Button
            type="submit"
            fullWidth
            variant="contained"
            size="large"
            disabled={!selectedArenaId || takingControl}
            sx={{ py: 1.5 }}
          >
            {takingControl ? 'Processing...' : 'Continue'}
          </Button>
        </Box>

        {arenas.length === 0 && !loading && (
          <Alert severity="info" sx={{ mt: 3 }}>
            No arenas available. Contact your administrator.
          </Alert>
        )}

        {/* Arena Info Display */}
        {selectedArenaId && (
          <Box sx={{ mt: 3, p: 2, bgcolor: 'background.default', borderRadius: 1 }}>
            {(() => {
              const selectedArena = arenas.find(arena => arena.id === parseInt(selectedArenaId));
              return selectedArena ? (
                <Box>
                  <Typography variant="subtitle2" gutterBottom>
                    Arena Details:
                  </Typography>
                  <Typography variant="body2">
                    <strong>Name:</strong> {selectedArena.arena_name}
                  </Typography>
                  <Typography variant="body2">
                    <strong>Brightness:</strong> {selectedArena.brightness}%
                  </Typography>
                  <Typography variant="body2">
                    <strong>Controller:</strong> {selectedArena.active_controller_username || 'None'}
                  </Typography>
                </Box>
              ) : null;
            })()}
          </Box>
        )}
      </Paper>
    </Container>
  );
};

export default ArenaSelection;
