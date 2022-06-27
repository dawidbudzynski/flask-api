from flask_jwt_extended import jwt_required, get_jwt
from flask_restful import Resource, reqparse

from models.item import ItemModel

BLANK_ERROR = "This field cannot be left blank"
NAME_ALREADY_EXISTS_ERROR = "An item with this name already exists"
ITEM_NOT_FOUND_ERROR = "Item not found"


class Item(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument(
        "price", type=float, required=True, help=BLANK_ERROR
    )
    parser.add_argument(
        "store_id", type=int, required=True, help=BLANK_ERROR
    )

    @classmethod
    def get(cls, name: str):
        item = ItemModel.find_by_name(name)
        if item:
            return item.json()
        return {"message": ITEM_NOT_FOUND_ERROR}, 404

    @classmethod
    @jwt_required(fresh=True)
    def post(cls, name: str):
        if ItemModel.find_by_name(name):
            return {
                       "message": NAME_ALREADY_EXISTS_ERROR
                   }, 400

        data = Item.parser.parse_args()

        item = ItemModel(name, **data)

        try:
            item.save_to_db()
        except Exception as e:
            return {"message": f"An error occurred inserting the item: {e}"}, 500

        return item.json(), 201

    @classmethod
    @jwt_required()
    def delete(cls, name: str):
        claims = get_jwt()
        if not claims["is_admin"]:
            return {"message": "Admin privilege requires"}, 401
        item = ItemModel.find_by_name(name)
        if item:
            item.delete_from_db()
            return {"message": "Item deleted."}
        return {"message": ITEM_NOT_FOUND_ERROR}, 404

    @classmethod
    def put(cls, name: str):
        data = Item.parser.parse_args()

        item = ItemModel.find_by_name(name)

        if item:
            item.price = data["price"]
        else:
            item = ItemModel(name, **data)

        item.save_to_db()

        return item.json()


class ItemList(Resource):
    @classmethod
    def get(cls):
        return {"items": [item.json() for item in ItemModel.find_all()]}, 200
