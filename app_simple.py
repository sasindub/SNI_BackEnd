"""
Simplified Flask app with JWT auth for admin
"""

from flask import Flask, jsonify
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix
from config import Config
from admin_routes import admin_bp

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Fix for Railway's reverse proxy
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

# Simple CORS - allow everything for admin routes
CORS(app, resources={
    r"/api/admin/*": {
        "origins": "*",  # Allow all origins for testing
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "expose_headers": ["Content-Type"],
        "supports_credentials": False  # No cookies needed!
    }
})

# Register admin blueprint
app.register_blueprint(admin_bp)

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

