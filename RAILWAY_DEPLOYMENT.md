# Railway Deployment Guide for SNI Laptops Backend

## Prerequisites
- GitHub account
- Railway account (https://railway.app)
- Your MongoDB is already on Railway ✅

## Deployment Steps

### Step 1: Push Your Code to GitHub

```bash
git add .
git commit -m "Prepare for Railway deployment"
git push origin main
```

### Step 2: Deploy to Railway

1. Go to [Railway.app](https://railway.app) and sign in
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose your `SNI_BackEnd` repository
5. Railway will automatically detect it's a Python app and start building

### Step 3: Configure Environment Variables

In your Railway project dashboard, go to **Variables** tab and add:

#### Required Variables:

```env
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=<generate-a-strong-random-key>
```

**To generate a strong SECRET_KEY, run this in Python:**
```python
import secrets
print(secrets.token_hex(32))
```

#### Optional (for Email Functionality):

```env
SENDGRID_API_KEY=<your-sendgrid-api-key>
FROM_EMAIL=noreply@yourcompany.com
FROM_NAME=SNI Laptops
ADMIN_EMAIL=admin@snilaptops.com
```

#### MongoDB Variables (Already Configured):
These have defaults in `config.py`, but you can override them:

```env
MONGODB_USERNAME=mongo
MONGODB_PASSWORD=UIKMSJBhHBiVyBzQibsBoFXhkjPyTgcj
MONGODB_HOST=yamanote.proxy.rlwy.net
MONGODB_PORT=18859
MONGODB_DATABASE=sni_laptops
```

### Step 4: Enable Public Domain

1. In Railway dashboard, go to **Settings** tab
2. Scroll to **Networking** section
3. Click **"Generate Domain"**
4. Your API will be available at: `https://your-app-name.up.railway.app`

### Step 5: Update CORS Origins

After getting your Railway domain, update the CORS origins in `app.py`:

```python
CORS(app, 
     origins=['http://localhost:3000', 'https://your-frontend-domain.com', 'https://your-backend.up.railway.app'],
     supports_credentials=True,
     allow_headers=['Content-Type', 'Authorization'],
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
```

Then commit and push:
```bash
git add app.py
git commit -m "Update CORS for production"
git push
```

Railway will automatically redeploy.

## Verify Deployment

### Test the Health Endpoint:

```bash
curl https://your-app-name.up.railway.app/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "message": "SNI Laptops API is running",
  "version": "1.0.0"
}
```

### Test Login:

```bash
curl -X POST https://your-app-name.up.railway.app/api/admin/login \
  -H "Content-Type: application/json" \
  -d '{"username":"Admin","password":"Admin123"}'
```

## Important Notes

### ✅ What's Already Configured:

- ✓ Gunicorn for production server
- ✓ MongoDB connection (already on Railway)
- ✓ Environment variable support
- ✓ Health check endpoint
- ✓ Auto-restart on failure
- ✓ Session management
- ✓ CORS enabled
- ✓ Error handling

### 🔒 Security Recommendations:

1. **Change the default admin password** after deployment:
   ```bash
   python reset_admin_password.py
   ```

2. **Use a strong SECRET_KEY** - never use the default in production

3. **Enable SendGrid** for email notifications (optional but recommended)

4. **Update CORS origins** to match your frontend domain

### 📊 Monitoring:

- Railway provides automatic logging - check the **Deployments** tab
- Monitor your API at: `https://your-app.up.railway.app/api/health`
- MongoDB metrics available in Railway MongoDB service

### 🔄 Updates:

To deploy updates:
```bash
git add .
git commit -m "Your update message"
git push
```

Railway will automatically detect changes and redeploy.

## Troubleshooting

### Issue: Build Fails
- Check the build logs in Railway dashboard
- Verify all dependencies in `requirements.txt` are correct

### Issue: App Crashes on Start
- Check environment variables are set correctly
- Verify MongoDB connection details
- Check logs in Railway dashboard

### Issue: 502 Bad Gateway
- App is probably crashing - check logs
- Verify `Procfile` and `railway.json` are correct
- Ensure `gunicorn` is in `requirements.txt`

### Issue: CORS Errors
- Update CORS origins in `app.py` to include your frontend domain
- Ensure `supports_credentials=True` is set

## Support

For Railway-specific issues:
- Railway Documentation: https://docs.railway.app
- Railway Discord: https://discord.gg/railway

For app-specific issues:
- Check application logs in Railway dashboard
- Verify all environment variables are set
- Test endpoints using curl or Postman

## Cost Estimate

Railway Free Tier:
- $5 credit per month (enough for small projects)
- Your MongoDB is already hosted on Railway
- Backend API can run within free tier

After free tier:
- Pay only for what you use (~$5-10/month for small traffic)

## Next Steps After Deployment

1. ✅ Test all API endpoints
2. ✅ Update frontend API URL to Railway domain
3. ✅ Change default admin password
4. ✅ Set up SendGrid for emails (optional)
5. ✅ Configure custom domain (optional)
6. ✅ Set up monitoring alerts (optional)

---

**Your backend is production-ready and can be deployed to Railway without any issues!** 🚀

