from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///autoservice.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

with app.app_context():
    db = SQLAlchemy(app)
    db.create_all()
    migrate = Migrate(app, db, directory='db/migrations')


class Car(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    make = db.Column(db.String(20))
    model = db.Column(db.String(20))
    color = db.Column(db.String(20))
    year = db.Column(db.Integer)


@app.route("/cars", methods=["POST", "GET"])
def get_cars():
    if request.method == "POST":
        try:
            make = request.form['make']
            model = request.form['model']
            color = request.form['color']
            year = request.form['year']

            if make and model and color and year:
                new_car = Car(make=make, model=model, color=color, year=year)
                db.session.add(new_car)
                db.session.commit()
                return jsonify({'message': 'success'})
            else:
                return jsonify({'error': 'Навления автомобиля.'}, 400)
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}, 500)

    elif request.method == "GET":
        cars_data = Car.query.all()
        car_list = [
            {
                'make': car.make,
                'model': car.model,
                'color': car.color,
                'year': car.year
            }
            for car in cars_data
        ]
        return jsonify({'cars': car_list})


if __name__ == "__main__":
    app.run(debug=True, port=5001)
