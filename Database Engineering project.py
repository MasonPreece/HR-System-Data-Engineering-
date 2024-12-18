from flask import Flask, request, jsonify
import psycopg2
import openai
import logging

# Set up OpenAI API key
openai.api_key = "your_openai_api_key"

# Initialize Flask app
app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Database connection function
def get_db_connection():
    try:
        conn = psycopg2.connect(
            dbname="hr_finance_data",
            user="postgres",
            password="Gloomis12.",
            host="localhost",
            port="5432",
            connect_timeout=5  # Timeout for hanging connections
        )
        return conn
    except Exception as e:
        logging.error(f"Database connection failed: {e}")
        raise Exception(f"Database connection failed: {e}")

# AI Response Function
def mason_bot_response(prompt):
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=150
        )
        return response['choices'][0]['text'].strip()
    except Exception as e:
        logging.error(f"OpenAI API error: {e}")
        return "Error: Unable to process your request with AI."

# Define a route for the root URL
@app.route("/")
def home():
    return "Welcome to the MasonBot API! Use the /chat endpoint to interact with the bot."

# Chat endpoint
@app.route("/chat", methods=["POST"])
def chat():
    data = request.json  # Get JSON payload
    conn = None
    cursor = None  # Declare the cursor for safety
    try:
        logging.debug(f"User Input: {data}")  # Debug log

        # Check if the message is for adding an employee
        if data.get("message", "").lower() == "add employee":
            # Extract employee details from the JSON payload
            employee_id = data.get("employee_id")
            name = data.get("name")
            position = data.get("position")
            department_id = data.get("department_id")
            hire_date = data.get("hire_date")

            # Validate input
            if not all([employee_id, name, position, department_id, hire_date]):
                return jsonify({"response": "Error: Missing required employee details."}), 400

            logging.debug(f"Parsed Employee Data: {employee_id}, {name}, {position}, {department_id}, {hire_date}")

            # Connect to the database
            conn = get_db_connection()
            cursor = conn.cursor()

            # Insert into the database (include employee_id in the query)
            cursor.execute("""
                INSERT INTO employee_table (employee_id, name, position, department_id, hire_date)
                VALUES (%s, %s, %s, %s, %s);
            """, (employee_id, name, position, department_id, hire_date))
            conn.commit()

            response = f"Employee {name} with ID {employee_id} added successfully."
            return jsonify({"response": response}), 200

        else:
            response = "Error: Command not recognized or invalid input format."
            return jsonify({"response": response}), 400

    except psycopg2.Error as db_error:
        logging.error(f"Database Error: {db_error}")  # Debug log
        return jsonify({"error": f"Database error: {str(db_error)}"}), 500
    except Exception as e:
        logging.error(f"Error: {e}")  # Debug log
        return jsonify({"error": str(e)}), 500

    finally:
        # Ensure database connection and cursor are properly closed
        if cursor:
            cursor.close()
            logging.debug("Cursor closed.")  # Debug log
        if conn:
            conn.close()
            logging.debug("Database connection closed.")  # Debug log

# Main entry point
if __name__ == "__main__":
    try:
        app.run(debug=True)
    except Exception as e:
        logging.error(f"Failed to start server: {e}")
