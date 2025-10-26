# Testing Railway API

## The Fix

Added your Railway domain to CORS allowed origins in `app.py`.

## Deploy the Fix

```bash
git add app.py
git commit -m "Add Railway domain to CORS origins"
git push origin main
```

Railway will auto-deploy (wait ~30 seconds).

## Test the API

### Using curl (Command Line):

```bash
# Health Check
curl https://snibackend-production.up.railway.app/api/health

# Login (POST request)
curl -X POST https://snibackend-production.up.railway.app/api/admin/login \
  -H "Content-Type: application/json" \
  -d '{"username":"Admin","password":"Admin123"}'
```

### Using Browser Console or JavaScript:

```javascript
// Health Check
fetch('https://snibackend-production.up.railway.app/api/health')
  .then(r => r.json())
  .then(console.log);

// Login
fetch('https://snibackend-production.up.railway.app/api/admin/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  credentials: 'include',
  body: JSON.stringify({
    username: 'Admin',
    password: 'Admin123'
  })
})
.then(r => r.json())
.then(console.log);
```

### Using Postman:

1. **Method**: POST
2. **URL**: `https://snibackend-production.up.railway.app/api/admin/login`
3. **Headers**: 
   - `Content-Type: application/json`
4. **Body** (raw JSON):
   ```json
   {
     "username": "Admin",
     "password": "Admin123"
   }
   ```

## Important Notes:

✅ **Use HTTPS** not HTTP (Railway provides SSL automatically)  
✅ **Method must be POST** for login endpoint  
✅ **Content-Type must be application/json**  

## Expected Responses:

### Health Check:
```json
{
  "status": "healthy",
  "message": "SNI Laptops API is running",
  "version": "1.0.0"
}
```

### Login Success:
```json
{
  "success": true,
  "message": "Login successful",
  "user": {
    "username": "Admin",
    "role": "admin"
  }
}
```

## When You Deploy Your Frontend:

Add your frontend domain to the CORS origins list in `app.py`:

```python
"origins": [
    "http://localhost:3000",
    "http://localhost:5000",
    "https://snibackend-production.up.railway.app",
    "http://snibackend-production.up.railway.app",
    "https://your-frontend-domain.com",  # Add this
    "https://your-frontend.vercel.app"   # Or this
],
```

Then commit and push again.

