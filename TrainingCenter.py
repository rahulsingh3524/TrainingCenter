from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import re

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///training_centers.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class TrainingCenter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    center_name = db.Column(db.String(40), nullable=False)
    center_code = db.Column(db.String(12), unique=True, nullable=False)
    detailed_address = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    pincode = db.Column(db.String(10), nullable=False)
    student_capacity = db.Column(db.Integer)
    courses_offered = db.Column(db.Text)
    created_on = db.Column(db.Integer, default=lambda: int(datetime.utcnow().timestamp()))
    contact_email = db.Column(db.String(100))
    contact_phone = db.Column(db.String(15), nullable=False)

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


def validate_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

def validate_phone(phone):
    return re.match(r"^\d{10}$", phone)

@app.errorhandler(400)
def handle_bad_request(e):
    return jsonify({"error": str(e)}), 400

@app.route('/')
def home():
    return jsonify({"message": "Traini8 Backend API is running"}), 200


# @app.route('/training-center', methods=['POST'])
# def create_training_center():
#     data = request.json
    
#     required_fields = ["center_name", "center_code", "address", "contact_phone"]
#     for field in required_fields:
#         if field not in data:
#             return jsonify({"error": f"{field} is required"}), 400

#     if len(data['center_name']) > 40:
#         return jsonify({"error": "CenterName should be less than 40 characters"}), 400

#     if len(data['center_code']) != 12:
#         return jsonify({"error": "CenterCode should be exactly 12 characters"}), 400

#     if "contact_email" in data and not validate_email(data["contact_email"]):
#         return jsonify({"error": "Invalid email format"}), 400
    
#     if not validate_phone(data["contact_phone"]):
#         return jsonify({"error": "Invalid phone number format"}), 400
    
#     address = data["address"]
#     if not all(k in address for k in ["detailed_address", "city", "state", "pincode"]):
#         return jsonify({"error": "Incomplete address details"}), 400
    
#     new_center = TrainingCenter(
#         center_name=data['center_name'],
#         center_code=data['center_code'],
#         detailed_address=address["detailed_address"],
#         city=address["city"],
#         state=address["state"],
#         pincode=address["pincode"],
#         student_capacity=data.get("student_capacity"),
#         courses_offered=','.join(data.get("courses_offered", [])),
#         contact_email=data.get("contact_email"),
#         contact_phone=data["contact_phone"],
#     )
#     db.session.add(new_center)
#     db.session.commit()
#     return jsonify(new_center.to_dict()), 201

@app.route('/training-center', methods=['POST'])
def create_training_center():
    data = request.json
    
    required_fields = ["center_name", "center_code", "address", "contact_phone"]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"{field} is required"}), 400

    if len(data['center_name']) > 40:
        return jsonify({"error": "CenterName should be less than 40 characters"}), 400

    if len(data['center_code']) != 12:
        return jsonify({"error": "CenterCode should be exactly 12 characters"}), 400

    if "contact_email" in data and not validate_email(data["contact_email"]):
        return jsonify({"error": "Invalid email format"}), 400
    
    if not validate_phone(data["contact_phone"]):
        return jsonify({"error": "Invalid phone number format"}), 400
    
    address = data["address"]
    if not all(k in address for k in ["detailed_address", "city", "state", "pincode"]):
        return jsonify({"error": "Incomplete address details"}), 400

    # Check if center_code already exists
    existing_center = TrainingCenter.query.filter_by(center_code=data["center_code"]).first()
    if existing_center:
        return jsonify({"error": "A training center with this CenterCode already exists"}), 400

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
    
    db.session.add(new_center)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Database error: " + str(e)}), 500
    
    return jsonify(new_center.to_dict()), 201


@app.route('/training-centers', methods=['GET'])
def get_training_centers():
    filters = request.args
    query = TrainingCenter.query
    
    if "city" in filters:
        query = query.filter_by(city=filters["city"])
    if "state" in filters:
        query = query.filter_by(state=filters["state"])
    if "pincode" in filters:
        query = query.filter_by(pincode=filters["pincode"])
    
    centers = query.all()
    return jsonify([center.to_dict() for center in centers]), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, use_reloader=False)

