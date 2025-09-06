import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { CssBaseline, AppBar, Toolbar, Typography, Button, Box } from '@mui/material';
import { AuthProvider, useAuth } from './contexts/AuthContext';

// Components
import LoginForm from './components/auth/LoginForm';
import RegisterForm from './components/auth/RegisterForm';
import ArenaSelection from './components/dashboard/ArenaSelection';
import ArenaControl from './components/dashboard/ArenaControl';
import Dashboard from './components/dashboard/Dashboard';
import ProtectedRoute from './components/common/ProtectedRoute';

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

const AppContent = () => {
  const { user, logout, isAuthenticated } = useAuth();

  const handleLogout = async () => {
    await logout();
  };

  return (
    <Box sx={{ flexGrow: 1 }}>
      {isAuthenticated && (
        <AppBar position="static">
          <Toolbar>
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              Courtside Control System
            </Typography>
            {user && (
              <>
                <Typography variant="body2" sx={{ mr: 2 }}>
                  Welcome, {user.first_name}
                </Typography>
                <Button color="inherit" onClick={handleLogout}>
                  Logout
                </Button>
              </>
            )}
          </Toolbar>
        </AppBar>
      )}

      <Routes>
        <Route path="/login" element={<LoginForm />} />
        <Route path="/register" element={<RegisterForm />} />
        
        <Route path="/dashboard" element={
          <ProtectedRoute>
            <ArenaSelection />
          </ProtectedRoute>
        } />
        
        <Route path="/arena/:arenaId/control" element={
          <ProtectedRoute>
            <ArenaControl />
          </ProtectedRoute>
        } />
        
        <Route path="/arena/:arenaId/dashboard" element={
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        } />
        
        <Route path="/" element={
          isAuthenticated ? <Navigate to="/dashboard" replace /> : <Navigate to="/login" replace />
        } />
        
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Box>
  );
};

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AuthProvider>
        <Router>
          <AppContent />
        </Router>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;
