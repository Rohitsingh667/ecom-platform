# 🚀 Deploy AI Shop India to Render

## Prerequisites
- GitHub account with your project repository
- Render account (free tier available)

## Step 1: Prepare Your Repository
✅ All files have been created and configured for Render deployment.

## Step 2: Create Render Account & Connect GitHub
1. Go to https://render.com and sign up
2. Connect your GitHub account
3. Give Render access to your repository

## Step 3: Create PostgreSQL Database
1. In Render dashboard, click "New +"
2. Select "PostgreSQL"
3. Configuration:
   - **Name**: `ai-shop-india-db`
   - **Region**: Choose closest to your users (Singapore for India)
   - **PostgreSQL Version**: 15
   - **Plan**: Free (for development)
4. Click "Create Database"
5. **Copy the Internal Database URL** - you'll need this

## Step 4: Create Web Service
1. Click "New +" → "Web Service"
2. Connect your repository
3. Configuration:
   - **Name**: `ai-shop-india`
   - **Region**: Same as database
   - **Branch**: `main`
   - **Runtime**: `Python 3`
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn ecommerce_project.wsgi:application --bind 0.0.0.0:$PORT --settings=ecommerce_project.render_settings`
   - **Plan**: Free (for development)

## Step 5: Set Environment Variables
In the "Environment" section, add:

```
DATABASE_URL=<paste-internal-database-url-here>
SECRET_KEY=your-super-secret-key-change-this-in-production
DJANGO_SETTINGS_MODULE=ecommerce_project.render_settings
PYTHON_VERSION=3.11.0
```

## Step 6: Deploy
1. Click "Create Web Service"
2. Render will automatically:
   - Install dependencies
   - Run migrations
   - Load Indian data
   - Train ML models
   - Collect static files
3. Wait for deployment (5-10 minutes)

## Step 7: Post-Deployment Setup
1. Once deployed, visit your app URL
2. Add `/admin/` to access admin panel
3. Login credentials:
   - **Username**: `admin`
   - **Password**: `SecureAdmin@2024`

## Step 8: (Optional) Create Background Worker
For ML model retraining:
1. Click "New +" → "Background Worker"
2. Connect same repository
3. Configuration:
   - **Name**: `ai-shop-worker`
   - **Command**: `python render_deploy_setup.py`
   - **Region**: Same as web service

## 🎉 Your AI Shop India is Live!

### URLs:
- **Website**: `https://ai-shop-india.onrender.com`
- **Admin**: `https://ai-shop-india.onrender.com/admin/`
- **API**: `https://ai-shop-india.onrender.com/api/`

### Features Available:
- 🛍️ Product catalog with Indian products
- 🤖 AI-powered recommendations
- 🛒 Shopping cart functionality
- 💳 Checkout process
- 👤 User authentication
- 🇮🇳 Indian localization (₹ INR, Asia/Kolkata timezone)

### Admin Features:
- 📊 Product management
- 👥 User management
- 📈 Order tracking
- 🤖 ML model status

## Troubleshooting

### Build Fails?
- Check build logs in Render dashboard
- Ensure all dependencies in requirements.txt are compatible

### Database Issues?
- Verify DATABASE_URL is correctly set
- Check database connection in PostgreSQL dashboard

### Static Files Not Loading?
- WhiteNoise is configured to serve static files
- Ensure collectstatic ran successfully in build logs

### ML Models Not Working?
- Check if Cython compilation succeeded in build logs
- Models train automatically during deployment

## Auto-Deployment
- Every push to main branch will trigger auto-deployment
- Render will rebuild and redeploy automatically
- Database and static files persist between deployments

## Scaling
- Upgrade to paid plans for:
  - More compute resources
  - Custom domains
  - SSL certificates
  - Advanced monitoring
