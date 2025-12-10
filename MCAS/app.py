from bson import ObjectId
from flask import Flask, request, jsonify, render_template, send_file, session, redirect, url_for
from flask_pymongo import PyMongo
from pymongo import MongoClient
from flask_bcrypt import Bcrypt
from datetime import datetime, timezone
import subprocess
import json
import re
from fpdf import FPDF
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

# Configuration - In production, use environment variables
app.config["MONGO_URI"] = os.environ.get("MONGO_URI", "mongodb://localhost:27017/Multimedia-Content-Analysing-System")
app.config["UPLOAD_FOLDER"] = "static/uploads"
app.secret_key = os.environ.get("SECRET_KEY", "9b1c8c49d3c3e7e456f7ab97d8332a19")
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

mongo = PyMongo(app)
bcrypt = Bcrypt(app)
users_collection = mongo.db.users

# Validation helper functions
def validate_email(email):
    """Validate email format"""
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email) is not None

def validate_password(password):
    """Validate password strength - at least 8 characters"""
    return len(password) >= 8

def validate_username(username):
    """Validate username - alphanumeric and underscores, 3-20 characters"""
    return 3 <= len(username) <= 20 and re.match(r'^[a-zA-Z0-9_]+$', username) is not None

# Utility function to check allowed file types
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return render_template('Homepage.html')

@app.route('/Login', methods=['GET', 'POST'])
def Login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        # Validate inputs
        if not email or not password:
            error = "Error: Email and password are required."
            return render_template('Login.html', error=error)

        if not validate_email(email):
            error = "Error: Invalid email format."
            return render_template('Login.html', error=error)

        # Find the user in the database
        user = users_collection.find_one({"email": email})

        if user and bcrypt.check_password_hash(user["password"], password):
            # Store user info in session
            session['user_id'] = str(user["_id"])
            session['username'] = user["username"]
            session.permanent = True
            return redirect(url_for('homepageafterlogin'))
        else:
            error = "Error: Invalid email or password."
            return render_template('Login.html', error=error)

    return render_template('Login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        # Validate inputs
        if not username or not email or not password:
            return render_template('register.html', error="Error: All fields are required.")

        if not validate_username(username):
            return render_template('register.html', error="Error: Username must be 3-20 characters and contain only letters, numbers, and underscores.")

        if not validate_email(email):
            return render_template('register.html', error="Error: Invalid email format.")

        if not validate_password(password):
            return render_template('register.html', error="Error: Password must be at least 8 characters long.")

        if password != confirm_password:
            return render_template('register.html', error="Error: Passwords do not match.")

        # Check if the email or username is already registered
        existing_user = users_collection.find_one({"$or": [{"email": email}, {"username": username}]})
        if existing_user:
            if existing_user.get("email") == email:
                return render_template('register.html', error="Error: This email has already been registered.")
            else:
                return render_template('register.html', error="Error: This username is already taken.")

        # Hash the password before storing
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # Insert the new user into the database
        users_collection.insert_one({
            "username": username,
            "email": email,
            "password": hashed_password,
            "bio": "",
            "created_at": datetime.now(timezone.utc).isoformat()
        })

        # Redirect to the login page after successful registration
        return redirect(url_for('Login'))

    return render_template('register.html')


@app.route('/logout')
def logout():
    """Logout route to clear session"""
    session.clear()
    return redirect(url_for('home'))

@app.route('/homepageafterlogin', methods=['GET', 'POST'])
def homepageafterlogin():
    if 'user_id' not in session:
        return redirect(url_for('Login'))
    return render_template('homepageafterlogin.html')

@app.route('/textsummary')
def textsummary():
    return render_template('textsummary.html')

@app.route('/textsummaryafterlogin')
def textsummaryafterlogin():
    if 'user_id' not in session:
        return redirect(url_for('Login'))
    return render_template('textsummaryafterlogin.html')

@app.route('/savedsummarypage', methods=['GET'])
def savedsummarypage():
    if 'user_id' not in session:
        return redirect(url_for('Login'))  # Redirect if not logged in

    # Fetch saved summaries for the logged-in user
    user_id = ObjectId(session['user_id'])
    summaries = list(users_collection.find({"user_id": user_id, "input_type": "video"}))

    # Convert ObjectId to string for JSON serialization
    for summary in summaries:
        summary["_id"] = str(summary["_id"])

    return render_template('savedsummarypage.html', summaries=summaries)

@app.route('/summary')
def summary():
    return render_template('summary.html')

@app.route('/summaryafterlogin')
def summaryafterlogin():
    if 'user_id' not in session:
        return redirect(url_for('Login'))
    return render_template('summaryafterlogin.html')

@app.route('/summarypagefortext')
def summarypagefortext():
    return render_template('summarypagefortext.html')

@app.route('/summarypageafterloginfortext')
def summarypageafterloginfortext():
    if 'user_id' not in session:
        return redirect(url_for('Login'))
    return render_template('summarypageafterloginfortext.html')
@app.route('/user', methods=['GET', 'POST'])
def user():
    if 'user_id' not in session:
        return redirect(url_for('Login'))  # Redirect if not logged in

    user_id = ObjectId(session['user_id'])
    user = users_collection.find_one({"_id": user_id})

    return render_template('user.html', user=user)
# Update "About Me" section
@app.route('/update_about', methods=['POST'])
def update_about():
    if 'user_id' not in session:
        return redirect(url_for('Login'))  # Redirect if not logged in

    user_id = ObjectId(session['user_id'])
    about_me = request.form.get('aboutMe')

    # Update the "bio" field in the user's document
    result = users_collection.update_one({"_id": user_id}, {"$set": {"bio": about_me}})
    
    # Check if the update was successful (matched count > 0)
    if result.matched_count > 0:
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "error": "Failed to update the bio"}), 400


@app.route('/generate_text_summary', methods=['POST'])
def generate_text_summary():
    data = request.get_json()  # Get JSON data from the request
    user_text = data.get("text")  # Extract text from JSON

    if not user_text or not user_text.strip():
        return jsonify({"error": "Enter some text"}), 400

    try:
        # Run testsummary.py and send the text via stdin
        result = subprocess.run(
            ['python', 'testsummary.py'],
            input=user_text,  # Pass the text as input
            capture_output=True,
            text=True
        )

        summary = result.stdout.strip()

        return jsonify({"summary": summary}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/generate_summary', methods=['POST'])
def generate_summary():
    data = request.get_json()
    video_id = data.get("videoId")

    if not video_id:
        return jsonify({"error": "Invalid video ID"}), 400

    try:
        result  = subprocess.run(['python', 'summarytest.py', video_id], capture_output=True, text=True)
        summary = result.stdout.strip()  # Capture the output summary

        return jsonify({"summary": summary}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/store", methods=["POST"])
def store_analysis_results():
    data = request.json  # Get JSON data from request
    input_type = data.get("input_type")
    input_name = data.get("input_name")
    output_data = data.get("output_data")

    if not input_type or not input_name or not output_data:
        return jsonify({"error": "Missing required fields"}), 400

    document = {
        "user_id": ObjectId(session['user_id']),
        "input_type": input_type,
        "input_name": input_name,
        "output_data": output_data,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    inserted_id = users_collection.insert_one(document).inserted_id
    return jsonify({"message": "Data stored successfully", "id": str(inserted_id)})

@app.route('/download_pdf', methods=['GET'])
def download_pdf():
    try:
        # Read the content of summary.txt
        with open('summary.txt', 'r', encoding='utf-8') as file:
            summary_content = file.read()

        # Generate the PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, summary_content)

        # Save the PDF temporarily
        pdf_file_path = 'summary.pdf'
        pdf.output(pdf_file_path)

        # Send the PDF as a downloadable file
        return send_file(pdf_file_path, as_attachment=True)

    except FileNotFoundError:
        return "Summary file not found. Please generate a summary first.", 404
    except Exception as e:
        return f"An error occurred: {e}", 500

if __name__ == '__main__':
    
    app.run(debug=True)