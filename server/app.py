from flask import Flask, request, session, jsonify
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from models import db, User

# ----------------------------
# Resources
# ----------------------------
class Login(Resource):
    def post(self):
        data = request.get_json()
        username = data.get("username")

        if not username:
            return {"error": "Username required"}, 400

        user = User.query.filter_by(username=username).first()
        if not user:
            return {"error": "User not found"}, 404

        session['user_id'] = user.id
        return jsonify(user.to_dict())

class Logout(Resource):
    def delete(self):
        session.pop('user_id', None)
        return '', 204

class CheckSession(Resource):
    def get(self):
        user_id = session.get('user_id')
        if not user_id:
            return {}, 401
        user = db.session.get(User, user_id)
        if not user:
            return {}, 401
        return jsonify(user.to_dict())

class Clear(Resource):
    def get(self):
        db.drop_all()
        db.create_all()
        db.session.add_all([
            User(username="alice"),
            User(username="bob"),
            User(username="charlie")
        ])
        db.session.commit()
        return '', 200

# ----------------------------
# App factory
# ----------------------------
def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = "supersecretkey"
    CORS(app, supports_credentials=True)

    db.init_app(app)
    api = Api(app)

    # Add resources
    api.add_resource(Login, '/login')
    api.add_resource(Logout, '/logout')
    api.add_resource(CheckSession, '/check_session')
    api.add_resource(Clear, '/clear')

    # Create tables using app context
    with app.app_context():
        db.create_all()
        # Seed users if none exist
        if User.query.count() == 0:
            db.session.add_all([
                User(username="alice"),
                User(username="bob"),
                User(username="charlie")
            ])
            db.session.commit()

    return app

# ----------------------------
# Create app instance for testing
# ----------------------------
app = create_app()

# ----------------------------
# Run
# ----------------------------
if __name__ == "__main__":
    app.run(port=5555, debug=True)
