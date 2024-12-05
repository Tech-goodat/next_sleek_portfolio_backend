from flask import Flask, request, make_response, jsonify, send_from_directory
from flask_restful import Api, Resource
from models import db, User
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token
from flask_migrate import Migrate
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///portfolio.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['JWT_SECRET_KEY'] = os.urandom(32).hex()  # Use a random secret key
app.json.compact = False

migrate = Migrate(app, db)
api = Api(app)
db.init_app(app)
cors = CORS(app)
jwt = JWTManager(app)


class Index(Resource):
    def get(self):
        return jsonify({"message": "Welcome to my Next.js Flask server!"}), 200

api.add_resource(Index, '/')


class Register(Resource):
    def post(self):
        data = request.json

        # Create a new user instance
        new_user = User(
            name=data['name'],
            email=data['email'],
            password=data['password'],
            image_url=data['image_url']  # In a real app, hash the password before storing
        )

        # Add the new user to the database
        db.session.add(new_user)
        db.session.commit()

        # Generate a JWT token for the new user
        access_token = create_access_token(identity=new_user.email)  # Use email or user ID as identity

        # Prepare the response data
        user_data = {
            "id": new_user.id,
            "name": new_user.name,
            "email": new_user.email,
            "image_url":new_user.image_url,
            "access_token": access_token  # Include the JWT token
        }

        # Return the user data and token as a response
        return make_response(jsonify(user_data), 201)

api.add_resource(Register, '/users/register')


class UserLogIn(Resource):
    def post(self):
        data = request.json
        email = data['email']
        password = data['password']

        # Check if the user exists
        user = User.query.filter_by(email=email).first()

        if user and user.password == password:  # Add password check (hash comparison should be done in a real app)
            # Generate JWT token
            access_token = create_access_token(identity=user.email)

            # Prepare the response data
            user_token = {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "image_url":user.image_url,
                "access_token": access_token  # Return the JWT token
            }

            return jsonify(user_token)

        return make_response(jsonify({"message": "Invalid credentials"}), 401)

api.add_resource(UserLogIn, '/user/login')


# Fetching user data based on the user ID
class UserData(Resource):
    def get(self, id):
        user = User.query.filter_by(id=id).first()

        if user:
            return make_response(jsonify(user.to_dict()), 200)

        return make_response(jsonify({"message": "User not found"}), 404)
    
    def patch(self, id):
        update_user=User.query.filter(User.id==id).first()

        for attr in request.json:
            setattr(update_user, attr, request.json[attr])

            db.session.add(update_user)
            db.session.commit()

        response_dict=update_user.to_dict()
        response=make_response(response_dict, 201)
        return response


api.add_resource(UserData, '/user/<int:id>')




# File download endpoints (optional)
class DownloadCert(Resource):
    def get(self):
        directory = 'static/files'
        filename = 'Felix Kiprotich Certificate.pdf'
        return send_from_directory(directory=directory, path=filename, as_attachment=True)

api.add_resource(DownloadCert, '/download/cert')


class DownloadResume(Resource):
    def get(self):
        directory = 'static/files'
        filename = "Felix kiprotich Resume.pdf"
        return send_from_directory(directory=directory, path=filename, as_attachment=True)

api.add_resource(DownloadResume, '/download/resume')


if __name__ == "__main__":
    app.run(port=5555, debug=True)
