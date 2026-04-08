# BetVision Pro - React Frontend

Modern React frontend for the BetVision Pro sports betting monitoring platform.

## Features

- 🎨 Modern, responsive UI with styled-components
- 🔐 JWT-based authentication
- 📊 Real-time dashboard with analytics
- 📱 Mobile-friendly design
- ⚡ Fast and optimized React app
- 🎭 Smooth animations with Framer Motion
- 🔔 Toast notifications for user feedback

## Tech Stack

- **React 18** - Modern React with hooks
- **React Router** - Client-side routing
- **Styled Components** - CSS-in-JS styling
- **Axios** - HTTP client for API calls
- **Framer Motion** - Smooth animations
- **React Hot Toast** - Beautiful notifications

## Getting Started

### Prerequisites

- Node.js 16+ and npm
- Django backend running on port 8000

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm start
```

The app will open at http://localhost:3000

### Environment Variables

Create a `.env` file in the root directory:

```env
REACT_APP_API_URL=http://localhost:8000
```

## Project Structure

```
src/
├── components/          # Reusable components
│   ├── Header.js       # Navigation header
│   ├── Sidebar.js      # Dashboard sidebar
│   ├── Layout.js       # Main layout wrapper
│   └── ...
├── pages/              # Page components
│   ├── LandingPage.js  # Marketing landing page
│   ├── Login.js        # Login form
│   ├── Register.js     # Registration form
│   ├── Dashboard.js    # Main dashboard
│   └── ...
├── contexts/           # React contexts
│   └── AuthContext.js  # Authentication state
├── services/           # API services
│   └── api.js          # Axios configuration
└── App.js              # Main app component
```

## Available Scripts

- `npm start` - Start development server
- `npm build` - Build for production
- `npm test` - Run tests
- `npm eject` - Eject from Create React App

## API Integration

The frontend communicates with the Django backend via REST API:

- Authentication: `/api/auth/`
- Monitoring: `/api/monitoring/`
- Analytics: `/api/analytics/`

## Deployment

```bash
# Build for production
npm run build

# Serve static files
npx serve -s build
```

## Contributing

1. Follow React best practices
2. Use styled-components for styling
3. Implement proper error handling
4. Add loading states for async operations
5. Ensure mobile responsiveness