"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin 
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, jwt_required
from werkzeug.security import generate_password_hash, check_password_hash
from models import *
import json

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)


# GET users
@app.route('/users', methods=['GET'])
def get_users():

    users = User.query.all()
    users = list(map(lambda user: user.serialize(), users))

    return jsonify(users), 200

# GET a single user
@app.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    user = User.query.get(id)
    if not user: return jsonify({"error":"user not found"}), 404
    if user:
        user = user.serialize()
        return jsonify(user), 200

#POST a new user
@app.route('/users', methods=['POST'])
def add_new_user():
    first_name = request.json.get('first_name')
    last_name = request.json.get('last_name')
    email = request.json.get('email')
    password = request.json.get('password')

    if not email: return jsonify({"error":"email is required!"}), 400
    if not password: return jsonify({"error":"please enter a password"}), 400

    newUser = User()
    newUser.first_name = first_name
    newUser.last_name = last_name
    newUser.email = email
    newUser.password = password
    newUser.save()

    return jsonify(newUser.serialize()), 201

# DELETE a user
@app.route('/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    user = User.query.get(id)
    if not user: return jsonify({"status": False, "msg":"User doesn't exist"}), 404
    user.delete()
    return jsonify({"status": True, "msg":"User deleted"}), 200

# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
