# run.py – Entry point for the Flask application
# This script creates the app instance and runs the development server.

from app import create_app  # Import the application factory

# Create the Flask app using the factory function
app = create_app()

if __name__ == "__main__":
    # Run the app in debug mode for development
    # In production, use a proper WSGI server (e.g., gunicorn)
    app.run(debug=True, host="0.0.0.0", port=1000)