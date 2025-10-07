# SNI Laptops Backend Setup Guide

## Quick Start

### 1. Navigate to Backend Directory
```bash
cd backend
```

### 2. Run Setup Script
```bash
./start.sh
```

### 3. Configure Environment Variables
Copy the example environment file and update with your credentials:

```bash
cp .env.example .env
```

Then edit `.env` with your actual SendGrid API key and other configuration values.

**Important**: Make sure to verify your sender email address in SendGrid dashboard before testing.

### 4. Start the API
```bash
python app.py
```

## Manual Setup

### 1. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Create Environment File
```bash
cp .env.example .env
```

Then edit `.env` with your actual SendGrid API key and other configuration values.

### 4. Configure SendGrid

1. **Sign up for SendGrid**: Go to https://sendgrid.com/
2. **Create API Key**: 
   - Go to Settings > API Keys
   - Create a new API key with "Full Access"
   - Copy the API key
3. **Verify Sender Email**:
   - Go to Settings > Sender Authentication
   - Verify your sender email address
4. **Update .env file** with your API key

### 5. Test the API
```bash
python test_api.py
```

## API Endpoints

### Health Check
```bash
curl http://localhost:5000/api/health
```

### Create Order
```bash
curl -X POST http://localhost:5000/api/orders \
  -H "Content-Type: application/json" \
  -d '{
    "product": {
      "id": "laptop-1",
      "name": "SNI Gaming Laptop",
      "basePrice": 2000,
      "selectedColor": "black",
      "selectedRam": "16GB",
      "selectedStorage": "512GB",
      "finalPrice": 2249
    },
    "customer": {
      "firstName": "John",
      "lastName": "Doe",
      "address": "123 Main Street",
      "city": "New York",
      "mobile": "1234567890",
      "email": "john@example.com",
      "zipCode": "10001"
    }
  }'
```

## Troubleshooting

### Common Issues

1. **Port 5000 already in use**
   ```bash
   # Kill process using port 5000
   lsof -ti:5000 | xargs kill -9
   ```

2. **SendGrid API Key Issues**
   - Verify API key is correct
   - Check SendGrid account status
   - Ensure sender email is verified

3. **Import Errors**
   ```bash
   pip install --upgrade -r requirements.txt
   ```

4. **CORS Issues**
   - Update CORS origins in `app.py`
   - Check frontend URL

### Testing Email Functionality

1. **Check SendGrid Logs**: Go to SendGrid dashboard > Activity
2. **Test with Real Email**: Use a real email address in test
3. **Check Spam Folder**: Emails might go to spam initially

## Production Deployment

### Using Gunicorn
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Environment Variables for Production
```env
FLASK_ENV=production
FLASK_DEBUG=False
SENDGRID_API_KEY=your_production_api_key
```

## File Structure
```
backend/
├── app.py                 # Main Flask application
├── config.py              # Configuration
├── requirements.txt       # Dependencies
├── start.sh              # Startup script
├── test_api.py           # API tests
├── .env.example          # Environment template
├── .env                  # Your environment variables
├── README.md             # Documentation
├── SETUP.md              # This file
└── services/
    ├── email_service.py   # Email handling
    └── order_service.py   # Order processing
```

## Support

If you encounter issues:
1. Check the logs in the terminal
2. Verify all environment variables are set
3. Test with the provided test script
4. Check SendGrid dashboard for email delivery status
