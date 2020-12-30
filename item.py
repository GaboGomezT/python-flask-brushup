import sqlite3
from flask_jwt import jwt_required
from flask_restful import Resource, reqparse

class Item(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument("price",
        type=float,
        required=True,
        help="This field cannot be left blank")

    @jwt_required()
    def get(self, name):
        item = self.find_by_name(name)
        if item:
            return item
        return {"message": "Item not found"}, 404

    @classmethod
    def find_by_name(cls, name):
        connection = sqlite3.connect("data.db")
        cursor = connection.cursor()

        query = "SELECT * FROM items WHERE name=?"
        result = cursor.execute(query, (name,))
        row = result.fetchone()
        connection.close()

        if row:
            return {
                "item":{
                    "name": row[0],
                    "price": row[1]
                }
            }

    def post(self, name):
        if self.find_by_name(name):
            return {"message": f"Item with name {name}, already exists"}, 400
        
        data = Item.parser.parse_args()
        item = {"name": name, "price": data["price"]}
        
        connection = sqlite3.connect("data.db")
        cursor = connection.cursor()

        query = "INSERT INTO items VALUES (?, ?)"
        cursor.execute(query, (item["name"], item["price"]))
        
        connection.commit()
        connection.close()

        return item, 201

    def delete(self, name):
        connection = sqlite3.connect("data.db")
        cursor = connection.cursor()

        query = "DELETE FROM items WHERE name=?"
        cursor.execute(query, (name,))
        
        connection.commit()
        connection.close()
        return {"message": f"Item with name {name} deleted"}

    def put(self, name):
        data = Item.parser.parse_args()
        item = next(filter(lambda  x: x["name"] == name, items), None)
        if not item:
            item = {"name": name, "price": data["price"]}
            items.append(item)
        else:
            item.update(data)
        return item, 201

class ItemList(Resource):
    def get(self):
        return {"items": items}