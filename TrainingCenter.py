from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import re

# Initialize Flask application
app = Flask(__name__)

# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///training_centers.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy ORM
db = SQLAlchemy(app)

# Define TrainingCenter model representing the training center entity
class TrainingCenter(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Primary key
    center_name = db.Column(db.String(40), nullable=False)  # Name of the training center (max 40 characters)
    center_code = db.Column(db.String(12), unique=True, nullable=False)  # Unique 12-character alphanumeric code
    detailed_address = db.Column(db.String(255), nullable=False)  # Detailed address
    city = db.Column(db.String(100), nullable=False)  # City name
    state = db.Column(db.String(100), nullable=False)  # State name
    pincode = db.Column(db.String(10), nullable=False)  # Pincode
    student_capacity = db.Column(db.Integer)  # Capacity of students that can be accommodated
    courses_offered = db.Column(db.Text)  # List of courses offered (stored as a comma-separated string)
    created_on = db.Column(db.Integer, default=lambda: int(datetime.utcnow().timestamp()))  # Timestamp when created
    contact_email = db.Column(db.String(100))  # Optional email field
    contact_phone = db.Column(db.String(15), nullable=False)  # Contact phone number (validated format)

    # Convert model instance to dictionary format for JSON responses
    def to_dict(self):
        return {
            "center_name": self.center_name,
            "center_code": self.center_code,
            "address": {
                "detailed_address": self.detailed_address,
                "city": self.city,
                "state": self.state,
                "pincode": self.pincode,
            },
            "student_capacity": self.student_capacity,
            "courses_offered": self.courses_offered.split(',') if self.courses_offered else [],
            "created_on": self.created_on,
            "contact_email": self.contact_email,
            "contact_phone": self.contact_phone,
        }

# Utility function to validate email format
def validate_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

# Utility function to validate phone number (10 digits)
def validate_phone(phone):
    return re.match(r"^\d{10}$", phone)

# Global error handler for bad requests (400)
@app.errorhandler(400)
def handle_bad_request(e):
    return jsonify({"error": str(e)}), 400

# Home route to confirm API is running
@app.route('/')
def home():
    return jsonify({"message": "Traini8 Backend API is running"}), 200

# API endpoint to create a new training center
@app.route('/training-center', methods=['POST'])
def create_training_center():
    data = request.json  # Retrieve JSON data from request

    # Check if all required fields are present
    required_fields = ["center_name", "center_code", "address", "contact_phone"]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"{field} is required"}), 400

    # Validate center name length
    if len(data['center_name']) > 40:
        return jsonify({"error": "CenterName should be less than 40 characters"}), 400

    # Validate center code length
    if len(data['center_code']) != 12:
        return jsonify({"error": "CenterCode should be exactly 12 characters"}), 400

    # Validate email format if provided
    if "contact_email" in data and not validate_email(data["contact_email"]):
        return jsonify({"error": "Invalid email format"}), 400

    # Validate phone number format
    if not validate_phone(data["contact_phone"]):
        return jsonify({"error": "Invalid phone number format"}), 400

    # Validate address fields
    address = data["address"]
    if not all(k in address for k in ["detailed_address", "city", "state", "pincode"]):
        return jsonify({"error": "Incomplete address details"}), 400

    # Check if center_code already exists in the database
    existing_center = TrainingCenter.query.filter_by(center_code=data["center_code"]).first()
    if existing_center:
        return jsonify({"error": "A training center with this CenterCode already exists"}), 400

    # Create a new TrainingCenter instance
    new_center = TrainingCenter(
        center_name=data['center_name'],
        center_code=data['center_code'],
        detailed_address=address["detailed_address"],
        city=address["city"],
        state=address["state"],
        pincode=address["pincode"],
        student_capacity=data.get("student_capacity"),
        courses_offered=','.join(data.get("courses_offered", [])),
        contact_email=data.get("contact_email"),
        contact_phone=data["contact_phone"],
    )

    # Add the new center to the database session and commit
    db.session.add(new_center)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()  # Rollback in case of error
        return jsonify({"error": "Database error: " + str(e)}), 500

    # Return the newly created training center details in JSON format
    return jsonify(new_center.to_dict()), 201

# API endpoint to retrieve all training centers with optional filters
@app.route('/training-centers', methods=['GET'])
def get_training_centers():
    filters = request.args  # Get query parameters from the request
    query = TrainingCenter.query

    # Apply filtering based on query parameters
    if "city" in filters:
        query = query.filter_by(city=filters["city"])
    if "state" in filters:
        query = query.filter_by(state=filters["state"])
    if "pincode" in filters:
        query = query.filter_by(pincode=filters["pincode"])

    # Retrieve all matching training centers from the database
    centers = query.all()
    return jsonify([center.to_dict() for center in centers]), 200

# Run the application
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Ensure database tables are created
    app.run(debug=True, use_reloader=False)
