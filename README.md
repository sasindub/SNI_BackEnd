# SNI Laptops Backend API

A Flask-based backend API for handling laptop orders and email notifications using SendGrid.

## Features

- Order processing and validation
- Email notifications using SendGrid
- Customer order confirmation emails
- Admin notification emails
- CORS enabled for frontend communication
- Proper error handling and logging

## Setup Instructions

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Environment Configuration

Create a `.env` file in the backend directory:

```env
# SendGrid Configuration
SENDGRID_API_KEY=your_sendgrid_api_key_here
FROM_EMAIL=noreply@yourcompany.com
FROM_NAME=Your Company Name

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
PORT=5000

# Email Templates
ADMIN_EMAIL=admin@yourcompany.com
```

### 3. SendGrid Setup

1. Sign up for a SendGrid account at https://sendgrid.com/
2. Create an API key in your SendGrid dashboard
3. Add the API key to your `.env` file
4. Verify your sender email address in SendGrid

### 4. Run the Application

```bash
python app.py
```

The API will be available at `http://localhost:5000`

## API Endpoints

### Health Check
- **GET** `/api/health` - Check if the API is running

### Orders
- **POST** `/api/orders` - Create a new order

#### Order Request Format:
```json
{
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
    "address": "123 Main St",
    "city": "New York",
    "mobile": "1234567890",
    "email": "john@example.com",
    "zipCode": "10001"
  },
  "orderDate": "2024-01-01T00:00:00.000Z"
}
```

#### Order Response Format:
```json
{
  "success": true,
  "message": "Order created successfully",
  "order_id": "ABC12345",
  "customer_email_sent": true,
  "admin_email_sent": true
}
```

## File Structure

```
backend/
├── app.py                 # Main Flask application
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── .env.example          # Environment variables template
└── services/
    ├── __init__.py
    ├── email_service.py   # Email handling with SendGrid
    └── order_service.py   # Order processing logic
```

## Email Templates

The system sends two types of emails:

1. **Customer Confirmation Email**: Sent to the customer with order details
2. **Admin Notification Email**: Sent to admin with new order information

Both emails include:
- Order details (product, specifications, price)
- Customer information
- Order ID for tracking

## Error Handling

The API includes comprehensive error handling:
- Input validation
- Email sending errors
- Database errors (when implemented)
- Proper HTTP status codes
- Detailed error messages

## Development

### Running in Development Mode
```bash
export FLASK_ENV=development
export FLASK_DEBUG=True
python app.py
```

### Production Deployment
For production deployment, use a WSGI server like Gunicorn:

```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## Security Notes

- Never commit the `.env` file to version control
- Use environment variables for all sensitive data
- Implement proper authentication for production use
- Add rate limiting for API endpoints
- Use HTTPS in production

## Troubleshooting

### Common Issues

1. **SendGrid API Key Issues**
   - Verify the API key is correct
   - Check SendGrid account status
   - Ensure sender email is verified

2. **CORS Issues**
   - Update CORS origins in `app.py`
   - Check frontend URL configuration

3. **Email Not Sending**
   - Check SendGrid logs
   - Verify email addresses
   - Check API key permissions

## Support

For issues or questions, please check the logs and ensure all environment variables are properly configured.
