from flask import Flask, request, jsonify
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'your-secret-key'  # Change this!
jwt = JWTManager(app)

# Login route to get token
@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username', None)
    password = request.json.get('password', None)
    
    # Validate credentials (in real app, check against database)
    if username != 'test' or password != 'test':
        return jsonify({"msg": "Bad username or password"}), 401
    
    # Create and return the token
    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token)

# Protected route that requires token
@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200