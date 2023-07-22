from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
import random

app = Flask(__name__)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/random")
def random_cafes():
    all_cafes = Cafe.query.all()
    random_cafe = random.choice(all_cafes)
    print(random_cafe)
    return jsonify(cafe=random_cafe.to_dict())

    # return jsonify(cafe={"id": random_cafe.id,
    #                      "name": random_cafe.name,
    #                      " map_url": random_cafe.map_url,
    #                      "img_url": random_cafe.img_url,
    #                      "location": random_cafe.location,
    #                      "seats": random_cafe.seats,
    #                      "has_toilet": random_cafe.has_toilet,
    #                      "has_wifi": random_cafe.has_wifi,
    #                      "has_sockets": random_cafe.has_sockets,
    #                      "can_take_calls": random_cafe.can_take_calls,
    #                      "coffee_price": random_cafe.coffee_price})


@app.route("/all")
def all_cafes():
    get_all_cafes = Cafe.query.all()
    cafes_list = []
    for cafe in get_all_cafes:
        json_cafe = cafe.to_dict()
        cafes_list.append(json_cafe)
    return jsonify(cafe=cafes_list)


@app.route("/search")
def cafe_position():
    cafes_with_location = []
    loc = request.args.get("loc")
    cafe_with_location = Cafe.query.filter_by(location=loc).all()
    if cafe_with_location:
        for cafe in cafe_with_location:
            cafes_with_location.append(cafe.to_dict())
        return jsonify(cafe=cafes_with_location)

    else:
        error_message = {"Not found": "Sorry,we don't have a cafe at this location"}
        return jsonify(error=error_message)


@app.route("/add", methods=["POST", "GET"])
def add_cafe():
    new_cafe = Cafe(
        name=request.form.get("name"),
        map_url=request.form.get("map_url"),
        img_url=request.form.get("img_url"),
        location=request.form.get("location"),
        seats=request.form.get("seats"),
        has_toilet=bool(request.form.get("has_toilet")),
        has_wifi=bool(request.form.get("has_wifi")),
        has_sockets=bool(request.form.get("has_sockets")),
        can_take_calls=bool(request.form.get("can_take_calls")),
        coffee_price=(request.form.get("coffee_price")))
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response={"success": "Successfully added the new Cafe."})


@app.route("/update-price/<price_id>", methods=['POST', 'GET', 'PATCH'])
def update_price(price_id):
    try:
        new_price = request.form.get("new_price")
        coffee_to_update = Cafe.query.get(price_id)
        coffee_to_update.coffee_price = new_price
        db.session.commit()
        return jsonify(success={"success": "Successfully updated the price"})

    except AttributeError:
        return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database"})

server_api_key = "ugonnachess"


@app.route("/cafe-closed/<int:column_id>", methods=['DELETE'])
def delete(column_id):
    try:
        api_key = request.args.get("api_key")
        print(api_key)
        if api_key == server_api_key:
            column_to_delete = Cafe.query.get(column_id)
            db.session.delete(column_to_delete)
            db.session.commit()
            return jsonify(response="message Deleted"), 200
        else:
            return jsonify(error="Sorry that's not allowed,Make sure you have the correct api_key"), 403

    except :
        return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database"}), 404


if __name__ == '__main__':
    app.run(debug=True)
