"""
Simplified Flask app with JWT auth for admin
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix
from config import Config
from admin_routes import admin_bp
from public_warranty_routes import warranty_public_bp
from order_routes import order_bp

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Fix for Railway's reverse proxy
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

# Simple CORS - allow everything for all API routes
CORS(app, 
     resources={
         r"/api/*": {"origins": "*"}  # Allow all API routes
     },
     allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     expose_headers=["Content-Type"],
     supports_credentials=False,
     send_wildcard=True,
     always_send=True)

# Handle OPTIONS requests globally
@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = app.make_default_options_response()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        return response

# Register blueprints
app.register_blueprint(admin_bp)
app.register_blueprint(warranty_public_bp)
app.register_blueprint(order_bp)

# Health check
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'message': 'SNI Admin API is running'
    })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'message': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'message': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=app.config['PORT'],
        debug=app.config['DEBUG']
    )

