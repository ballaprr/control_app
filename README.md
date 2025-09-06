# Courtside Control System

A modern web application for controlling arena systems with Django REST Framework backend and React frontend with JWT authentication.

## Architecture

- **Backend**: Django REST Framework with JWT authentication
- **Frontend**: React with Material-UI components
- **Authentication**: JWT-based with refresh tokens
- **Database**: PostgreSQL (configurable)

## Project Structure

```
show_courtside/
├── backend/
│   └── control_app/           # Django project
│       ├── control_app/       # Main settings
│       ├── user/              # User management with JWT auth
│       ├── arena/             # Arena models and API
│       ├── devices/           # Device management
│       └── dashboard/         # Legacy dashboard (can be removed)
└── frontend/                  # React application
    ├── src/
    │   ├── components/        # React components
    │   ├── services/          # API service layers
    │   └── contexts/          # React contexts
    └── public/
```

## Setup Instructions

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend/control_app
   ```

2. **Activate virtual environment:**
   ```bash
   source show-courtside-env/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   Create a `.env` file in the `control_app` directory with:
   ```
   DB_NAME=your_database_name
   DB_USER=your_database_user
   DB_PASSWORD=your_database_password
   DB_HOST=your_database_host
   EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
   EMAIL_HOST=your_smtp_host
   EMAIL_HOST_USER=your_email
   EMAIL_HOST_PASSWORD=your_email_password
   ```

5. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser (optional):**
   ```bash
   python manage.py createsuperuser
   ```

7. **Start the development server:**
   ```bash
   python manage.py runserver 8000
   ```

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Create environment file:**
   ```bash
   echo "REACT_APP_API_URL=http://localhost:8000/api" > .env
   ```

4. **Start the development server:**
   ```bash
   npm start
   ```

The React app will start on `http://localhost:3000` and automatically proxy API requests to the Django backend on `http://localhost:8000`.

## API Endpoints

### Authentication
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login (returns JWT tokens)
- `POST /api/auth/logout/` - User logout
- `POST /api/auth/token/refresh/` - Refresh JWT token
- `GET /api/auth/profile/` - Get user profile
- `PUT /api/auth/profile/` - Update user profile
- `POST /api/auth/change-password/` - Change password
- `POST /api/auth/forgot-password/` - Request password reset

### Arena Management
- `GET /api/arenas/` - List all arenas
- `POST /api/arenas/` - Create new arena
- `GET /api/arenas/{id}/` - Get specific arena
- `PUT /api/arenas/{id}/` - Update arena
- `DELETE /api/arenas/{id}/` - Delete arena
- `POST /api/arenas/{id}/take-control/` - Take control of arena
- `POST /api/arenas/{id}/release-control/` - Release control of arena
- `PUT /api/arenas/{id}/brightness/` - Update arena brightness

### Device Management
- `GET /api/devices/` - List all devices
- `POST /api/devices/` - Create new device
- `GET /api/devices/{id}/` - Get specific device
- `PUT /api/devices/{id}/` - Update device
- `DELETE /api/devices/{id}/` - Delete device
- `GET /api/devices/arena/{arena_id}/` - Get devices by arena
- `POST /api/devices/reboot/` - Reboot specific device
- `POST /api/devices/action/` - Trigger device action

## Frontend Features

### Authentication Flow
1. **Registration**: Users can register with email verification
2. **Login**: JWT-based authentication with automatic token refresh
3. **Protected Routes**: Automatic redirect to login for unauthenticated users

### Dashboard Features
1. **Arena Selection**: View available arenas and their current controllers
2. **Arena Control**: 
   - Take/release control of arenas
   - Adjust brightness levels
   - View connected devices
   - Reboot devices
   - Trigger device actions

### Modern UI
- Material-UI components for consistent design
- Responsive layout for desktop and mobile
- Loading states and error handling
- Real-time updates for arena control status

## Development

### Backend Development
- Django REST Framework for API development
- JWT authentication with refresh token rotation
- CORS configured for React frontend
- Email verification system for new users
- Admin approval workflow

### Frontend Development
- React with functional components and hooks
- Context API for state management
- Axios for API communication with automatic token refresh
- Material-UI for consistent styling
- React Router for navigation

## Security Features

- JWT authentication with secure token storage
- Automatic token refresh
- CORS protection
- Email verification for new accounts
- Admin approval for new users
- Protected API endpoints
- Secure password requirements (minimum 12 characters)

## Deployment Considerations

### Backend
- Use environment variables for sensitive data
- Configure CORS for production domains
- Set up proper database connections
- Configure email backend for production
- Use HTTPS in production

### Frontend
- Build for production: `npm run build`
- Serve static files through web server
- Configure API URL for production environment
- Enable HTTPS

## Migration from Legacy System

The new system maintains the existing database structure but adds:
- JWT authentication instead of session-based auth
- RESTful API endpoints
- Modern React frontend
- Improved security and user experience

Legacy template views are still available during transition but can be removed once the React frontend is fully deployed.

## Troubleshooting

### Common Issues

1. **CORS Errors**: Ensure the frontend URL is added to `CORS_ALLOWED_ORIGINS` in Django settings
2. **JWT Token Issues**: Check token expiration and refresh logic
3. **Database Connection**: Verify database settings in `.env` file
4. **Email Issues**: Configure SMTP settings for email verification

### Development Tips

1. Use browser developer tools to inspect API calls
2. Check Django logs for backend errors
3. Verify CORS configuration if API calls fail
4. Test authentication flow thoroughly
5. Use Django admin interface for debugging user accounts

## Testing

### Backend Testing
```bash
cd backend/control_app
python manage.py test
```

### Frontend Testing
```bash
cd frontend
npm test
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

[Your License Here]
