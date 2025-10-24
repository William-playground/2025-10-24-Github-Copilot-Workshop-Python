from flask import Flask, render_template

def create_app():
    """Flask application factory"""
    app = Flask(__name__)
    
    @app.route('/')
    def index():
        """Main page"""
        return render_template('index.html')
    
    return app

if __name__ == '__main__':
    import os
    app = create_app()
    # Debug mode is enabled for development/workshop purposes only
    # In production, set FLASK_DEBUG=False or remove debug parameter
    debug_mode = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)
