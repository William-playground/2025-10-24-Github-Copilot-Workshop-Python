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
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
