from flask import Flask, request, jsonify
import pymysql
import os
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database connection parameters from environment variables
DB_HOST = os.environ.get('DB_HOST')
DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_NAME = os.environ.get('DB_NAME')
DB_PORT = int(os.environ.get('DB_PORT', 3306))

def get_db_connection():
    """Create and return a connection to the RDS database"""
    try:
        connection = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            port=DB_PORT,
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        return None

@app.route('/post-form', methods=['POST'])
def post_form():
    """Handle POST requests to store form data in RDS"""
    if request.method != 'POST':
        return jsonify({"error": "Method not allowed"}), 405
    
    # Get form data from the request
    form_data = request.form.to_dict() if request.form else {}
    
    # If no form data but JSON data exists in the request
    if not form_data and request.is_json:
        form_data = request.get_json()
    
    # Check if we have any data to store
    if not form_data:
        return jsonify({"error": "No data provided"}), 400
    
    # Connect to the database
    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "Could not connect to database"}), 500
    
    try:
        with connection.cursor() as cursor:
            # Assume we have a "form_submissions" table
            # Adjust the table name and columns according to your schema
            columns = ', '.join(form_data.keys())
            placeholders = ', '.join(['%s'] * len(form_data))
            values = tuple(form_data.values())
            
            # Create the SQL query
            sql = f"INSERT INTO form_submissions ({columns}) VALUES ({placeholders})"
            
            # Execute the query
            cursor.execute(sql, values)
            
        # Commit the changes to the database
        connection.commit()
        
        return jsonify({
            "status": "success",
            "message": "Data stored successfully",
            "data": form_data
        }), 201
    
    except Exception as e:
        logger.error(f"Error storing data: {e}")
        return jsonify({"error": f"Failed to store data: {str(e)}"}), 500
    
    finally:
        connection.close()

@app.route('/', methods=['GET'])
def home():
    """Home route to verify the server is running"""
    return jsonify({"status": "Server is running", "endpoints": ["/post-form"]})


@app.route('/test', methods=['GET'])
def test():
    """Home route to verify the server is running"""
    return jsonify({"status": "Server is running", "endpoints": ["/post-form"]})

if __name__ == '__main__':
    # For development only - use a production WSGI server in production
    app.run(host='0.0.0.0', port=5000, debug=False)

