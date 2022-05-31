from flask import Flask, jsonify, render_template, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
import random

app = Flask(__name__)
Bootstrap(app)

# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Cafe TABLE Configuration
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
        dictionary = {}
        # Loop through each column in the data record
        for column in self.__table__.columns:
            dictionary[column.name] = getattr(self, column.name)
        return dictionary


@app.route("/")
def home():
    return render_template("index.html")
    

# HTTP GET - Read Record
@app.route("/random")
def get_random_cafe():
    cafes = db.session.query(Cafe).all()
    random_cafe = random.choice(cafes)
    # Simply convert the random_cafe data record to a dictionary of key-value pairs.
    return jsonify(cafe=to_dict(random_cafe))


@app.route('/all')
def get_all_cafe():
    data = []
    cafes = db.session.query(Cafe).all()
    for cafe in cafes:
        data.append(to_dict(cafe))
    return jsonify(data)


@app.route('/search')
def search_location():
    # request.args.get is a get method which passes parameters in url, after question mark
    list = []
    location = request.args.get('location')
    searched_cafe = Cafe.query.filter_by(location=location).all()
    # if there is any cafe at this location it will loop through all of them to return all
    if searched_cafe:
        for cafe in searched_cafe:
            list.append(to_dict(cafe))
        return jsonify(cafe=list)
    else:
        return jsonify(error={
            "Not Found": "Sorry, we dont have a cafe at that location"
        })


# HTTP POST - Create Record
@app.route('/add', methods=['POST'])
def adding_data():
    # So i have to create new request in postman of "POST" and added all the which we're passing
    # parameters in columns of database, than i pressed run on postman, without the url of this method,
    # and it added new cafe in database, so basically this method is runned in postman
    new_cafe = Cafe(
        name=request.form.get("name"),
        map_url=request.form.get("map_url"),
        img_url=request.form.get("img_url"),
        location=request.form.get("location"),
        has_sockets=bool(request.form.get("has_sockets")),
        has_toilet=bool(request.form.get("has_toilet")),
        has_wifi=bool(request.form.get("has_wifi")),
        can_take_calls=bool(request.form.get("can_take_calls")),
        seats=request.form.get("seats"),
        coffee_price=request.form.get("coffee_price"),
    )
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response={"success": "Successfully added the new cafe."})


# HTTP PUT/PATCH - Update Record
@app.route('/update-price', methods=['PATCH'])
def update_price():
    # we're passing cafe_id and new_price as a parameter
    new_price = request.args.get('new_price')
    cafe_id = request.args.get("cafe_id")
    # than searching cafe through id
    cafe = db.session.query(Cafe).filter_by(id=cafe_id).first()
    if cafe:
        # and finally updating the price through patch
        cafe.coffee_price = new_price
        db.session.commit()
        return jsonify(response={"success": "Successfully updated the price in database."}), 200
    else:
        return jsonify(Error={"Not Found": "Sorry a Cafe with the ID is not found in database."}), 404


# HTTP DELETE - Delete Record
@app.route('/report-closed', methods=["DELETE"])
def delete():
    cafe_id = request.args.get("cafe_id")
    api_key = request.args.get("api_key")
    if api_key == "bojbfjbsofnnovcbsdvncofbabco":
        cafe = db.session.query(Cafe).filter_by(id=cafe_id).first()
        if cafe:
            db.session.delete(cafe)
            db.session.commit()
            return jsonify(response={"success": "Successfully updated the price in database."}), 200
        else:
            return jsonify(Error={"Not Found": "Sorry a Cafe with the ID is not found in database."}), 404
    else:
        return jsonify(Error={"Not Found": "Sorry that's not allowed make sure you have a correct api key."}), 403


if __name__ == '__main__':
    app.run(debug=True)
