import os

from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_restful import Api
from marshmallow import ValidationError

from blacklist import BLACKLIST
from ma import ma
from resources.item import Item, ItemList
from resources.store import Store, StoreList
from resources.user import UserRegister, User, UserLogin, TokenRefresh, UserLogout

database_url = os.getenv("DATABASE_URL", "sqlite:///data.db")
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["PROPAGATE_EXCEPTIONS"] = True
app.config["JWT_BLACKLIST_ENABLED"] = True
app.config["JWT_BLACKLIST_TOKEN_CHECK"] = ["access", "refresh"]
app.secret_key = "jose"
api = Api(app)


@app.errorhandler(ValidationError)
def handle_marshmallow_validation(err):
    return jsonify(err.messages), 400


@app.before_first_request
def create_tables():
    db.create_all()


jwt = JWTManager(app)


@jwt.additional_claims_loader
def add_claims_to_jwt(identity):
    if identity == 1:
        return {"is_admin": True}
    return {"is_admin": False}


@jwt.expired_token_loader
def expired_token_callback():
    return (
        jsonify({"description": "The token has expired", "error": "token_expired"}),
        401,
    )


@jwt.token_in_blocklist_loader
def check_if_token_in_blacklist(header_data, payload_data):
    return payload_data.get("sub") in BLACKLIST


api.add_resource(Store, "/store/<string:name>")
api.add_resource(StoreList, "/stores")
api.add_resource(Item, "/item/<string:name>")
api.add_resource(ItemList, "/items")
api.add_resource(UserRegister, "/register")
api.add_resource(User, "/user/<int:user_id>")
api.add_resource(UserLogin, "/login")
api.add_resource(UserLogout, "/logout")
api.add_resource(TokenRefresh, "/refresh")

if __name__ == "__main__":
    from db import db

    db.init_app(app)
    ma.init_app(app)
    app.run(port=5000, debug=True)
