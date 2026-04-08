# 🎯 BetVision Pro - Professional Sports Betting Monitoring Platform

## 🌟 Overview

BetVision Pro is a comprehensive sports betting monitoring platform that combines real-time web scraping, advanced screenshot capture, AI-powered predictions, and professional user management. The system has evolved from a simple scraping tool to a full-featured Django-based platform with user authentication, beautiful UI, and enterprise-grade monitoring capabilities.

## 🚀 Key Features

### 🔐 User Management
- **Professional Landing Page** with modern design
- **User Registration & Authentication** with JWT tokens
- **Subscription Plans** (Free, Pro, Enterprise)
- **User Dashboard** with analytics and session management
- **Profile Management** with preferences and settings

### 📸 Advanced Monitoring
- **High-Quality Screenshot Capture** (1920x1080 resolution)
- **Real-time Change Detection** with visual diff analysis
- **Odds Extraction** using AI pattern recognition
- **Multi-site Support** with site-specific optimizations
- **Selenium Integration** for JavaScript-heavy sites

### 🤖 AI & Analytics
- **Score Prediction Engine** based on real-time data
- **Pattern Analysis** for betting trends
- **User Analytics** with detailed statistics
- **Platform Metrics** for admin insights
- **Alert System** for important changes

### 🎨 Professional UI
- **Beautiful Landing Page** with pricing tiers
- **Responsive Dashboard** with modern design
- **Real-time Updates** via WebSocket-like polling
- **Mobile-Friendly** interface
- **Dark/Light Theme** support

## 🏗️ System Architecture

```
BetVision Pro Architecture
├── Django Backend (Port 8000)
│   ├── Authentication App (User management)
│   ├── Monitoring App (Session management)
│   ├── Analytics App (Statistics & insights)
│   └── REST API (All endpoints)
├── Real-time System (Port 5001)
│   ├── Live Score Scraping
│   ├── AI Prediction Engine
│   └── Enhanced Scraper with Selenium
├── Visual Monitor (Port 5002)
│   ├── Screenshot Capture
│   ├── Change Detection
│   └── Thumbnail Generation
└── Frontend Templates
    ├── Landing Page (/)
    ├── Dashboard (/dashboard)
    └── Admin Panel (/admin)
```

## 📦 Installation & Setup

### Prerequisites
- Python 3.8+
- Chrome/Chromium browser (for Selenium)
- 4GB+ RAM recommended

### Quick Start
```bash
# 1. Navigate to DataMiner directory
cd my-portfolio/DataMiner

# 2. Install dependencies (optional - script will auto-install)
pip install -r betvision_backend/requirements.txt

# 3. Start complete system
python start_betvision_complete.py
```

### Manual Setup
```bash
# 1. Install dependencies
pip install django djangorestframework django-cors-headers
pip install pillow requests selenium beautifulsoup4 webdriver-manager
pip install flask flask-cors

# 2. Initialize Django backend
cd betvision_backend
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser  # Optional

# 3. Start services individually
python manage.py runserver 8000  # Django backend
python ../real_time_system.py     # Real-time system
python ../improved_visual_monitor.py  # Visual monitor
```

## 🌐 Service URLs

After starting the system, access these URLs:

### Main Platform
- **Landing Page**: http://localhost:8000
- **User Dashboard**: http://localhost:8000/dashboard
- **Admin Panel**: http://localhost:8000/admin

### API Endpoints
- **Authentication**: http://localhost:8000/api/auth/
- **Monitoring**: http://localhost:8000/api/monitoring/
- **Analytics**: http://localhost:8000/api/analytics/
- **Health Check**: http://localhost:8000/api/health/

### Monitoring Services
- **Real-time System**: http://localhost:5001
- **Visual Monitor**: http://localhost:5002

## 📚 API Documentation

### Authentication Endpoints
```
POST /api/auth/register/          # User registration
POST /api/auth/login/             # User login
POST /api/auth/logout/            # User logout
GET  /api/auth/profile/           # Get user profile
PUT  /api/auth/profile/update/    # Update profile
POST /api/auth/change-password/   # Change password
```

### Monitoring Endpoints
```
POST /api/monitoring/sessions/start/              # Start monitoring
POST /api/monitoring/sessions/{id}/stop/          # Stop monitoring
GET  /api/monitoring/sessions/                    # List sessions
GET  /api/monitoring/sessions/{id}/               # Session details
GET  /api/monitoring/sessions/{id}/screenshots/   # Session screenshots
GET  /api/monitoring/stats/                       # User statistics
```

### Analytics Endpoints
```
GET /api/analytics/user/          # User analytics
GET /api/analytics/dashboard/     # Dashboard data
GET /api/analytics/platform/      # Platform metrics (admin)
```

## 🎯 Usage Guide

### 1. User Registration
1. Visit http://localhost:8000
2. Click "Sign Up" 
3. Fill registration form
4. Verify email (if configured)
5. Access dashboard

### 2. Starting Monitoring
1. Login to dashboard
2. Click "Start Monitoring"
3. Enter website URL
4. Configure settings:
   - Monitoring interval (30s - 5min)
   - Duration (10min - 4hrs)
   - Screenshot quality
5. Click "Start Monitoring"

### 3. Viewing Results
1. Go to "Sessions" tab
2. Click on active session
3. View screenshots and changes
4. Check analytics for insights

### 4. Managing Alerts
1. Go to "Alerts" tab
2. View notifications for:
   - Odds changes
   - New matches
   - System errors
3. Mark as read/dismiss

## 🔧 Configuration

### Django Settings
Edit `betvision_backend/betvision_backend/settings.py`:

```python
# Database (default: SQLite)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'betvision_pro',
        'USER': 'your_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your_email@gmail.com'
EMAIL_HOST_PASSWORD = 'your_app_password'
```

### Monitoring Settings
```python
BETVISION_SETTINGS = {
    'MAX_MONITORING_SESSIONS_FREE': 5,
    'MAX_MONITORING_SESSIONS_PRO': 50,
    'MAX_SCREENSHOTS_PER_SESSION': 1000,
    'DEFAULT_MONITORING_INTERVAL': 30,
    'MAX_MONITORING_DURATION': 120,
}
```

## 📊 Subscription Plans

### Free Plan
- 5 monitoring sessions
- Basic screenshot capture
- Change detection
- Email support

### Pro Plan ($29/month)
- 50 monitoring sessions
- High-quality screenshots
- Advanced change detection
- AI predictions
- Advanced analytics
- Priority support

### Enterprise Plan ($99/month)
- 200 monitoring sessions
- Ultra-quality screenshots
- Custom integrations
- API access
- White-label options
- Dedicated support

## 🛠️ Development

### Project Structure
```
DataMiner/
├── betvision_backend/           # Django backend
│   ├── authentication/         # User management
│   ├── monitoring/             # Session management
│   ├── analytics/              # Statistics
│   ├── templates/              # HTML templates
│   └── betvision_backend/      # Django settings
├── real_time_system.py         # Live monitoring
├── improved_visual_monitor.py  # Screenshot system
├── enhanced_scraper.py         # Web scraping
└── start_betvision_complete.py # Startup script
```

### Adding New Features
1. Create Django app: `python manage.py startapp feature_name`
2. Add models in `models.py`
3. Create serializers in `serializers.py`
4. Add views in `views.py`
5. Configure URLs in `urls.py`
6. Run migrations: `python manage.py makemigrations && python manage.py migrate`

### Testing
```bash
# Run Django tests
python manage.py test

# Test API endpoints
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@example.com","password":"testpass123"}'
```

## 🚨 Troubleshooting

### Common Issues

**Port Already in Use**
```bash
# Find process using port
lsof -i :8000
# Kill process
kill -9 <PID>
```

**Chrome Driver Issues**
```bash
# Update webdriver
pip install --upgrade webdriver-manager
```

**Database Errors**
```bash
# Reset database
rm betvision_backend/db.sqlite3
python manage.py migrate
```

**Permission Errors**
```bash
# Fix file permissions
chmod +x start_betvision_complete.py
```

## 📈 Performance Optimization

### Database
- Use PostgreSQL for production
- Add database indexes for frequently queried fields
- Implement database connection pooling

### Caching
- Add Redis for session caching
- Implement API response caching
- Cache screenshot thumbnails

### Monitoring
- Limit concurrent sessions per user
- Implement rate limiting
- Add monitoring service health checks

## 🔒 Security

### Authentication
- JWT token-based authentication
- Password validation and hashing
- Session timeout management

### API Security
- CORS configuration
- Rate limiting
- Input validation and sanitization

### Data Protection
- Secure file uploads
- Database encryption
- HTTPS in production

## 🚀 Deployment

### Production Setup
1. Use PostgreSQL database
2. Configure Redis for caching
3. Set up Nginx reverse proxy
4. Use Gunicorn WSGI server
5. Configure SSL certificates
6. Set up monitoring and logging

### Docker Deployment
```dockerfile
# Dockerfile example
FROM python:3.11
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["gunicorn", "betvision_backend.wsgi:application"]
```

## 📞 Support

### Documentation
- API Reference: `/api/` endpoint
- Admin Guide: Django admin panel
- User Guide: Dashboard help section

### Contact
- Technical Support: Create GitHub issue
- Feature Requests: Submit enhancement request
- Bug Reports: Use issue tracker

## 📄 License

This project is proprietary software. All rights reserved.

## 🎉 Conclusion

BetVision Pro represents a complete evolution from a simple web scraping tool to a professional-grade sports betting monitoring platform. With its Django backend, beautiful UI, comprehensive API, and advanced monitoring capabilities, it provides everything needed for professional sports betting analysis and monitoring.

The system is designed to scale from individual users to enterprise deployments, with robust authentication, analytics, and monitoring features that rival commercial solutions.

---

**Ready to start monitoring? Run `python start_betvision_complete.py` and visit http://localhost:8000!** 🚀