from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging


app = Flask(__name__)


app.config['LOG_FILE'] = '/Users/user/Desktop/code/autoservice/autoservice.log'
file_handler = logging.FileHandler(app.config['LOG_FILE'])
file_handler.setLevel(logging.DEBUG)
app.logger.setLevel(logging.DEBUG)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///autoservice.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

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
            make = request.json['make']
            model = request.json['model']
            color = request.json['color']
            year = request.json['year']

            if make and model and color and year:
                new_car = Car(make=make, model=model, color=color, year=year)
                db.session.add(new_car)
                db.session.commit()
                print(request.form)
                app.logger.info("Received request (POST) to create a new car: %s", request.form)
                return jsonify({'message': 'success'})
            else:
                return jsonify({'error': 'Invalid car data.'}, 400)
        except Exception as e:
            db.session.rollback()
            app.logger.error("Error while processing the request (POST) to create a new car: %s", str(e))
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
        app.logger.info("Received request (GET) to retrieve the list of cars.")
        return jsonify({'cars': car_list})


@app.route("/cars/<int:car_id>", methods=["GET", "DELETE"])
def get_or_delete_car(car_id):
    car = Car.query.get(car_id)
    if car is None:
        return jsonify({'error': 'Car not found.'}, 404)

    if request.method == "GET":
        return jsonify({
            'make': car.make,
            'model': car.model,
            'color': car.color,
            'year': car.year
        })
    elif request.method == "DELETE":
        db.session.delete(car)
        db.session.commit()
        return jsonify({'message': 'Car deleted.'})


customer_car_association = db.Table(
    'customer_car_association',
    db.Column('customer_id', db.Integer, db.ForeignKey('customer.id')),
    db.Column('car_id', db.Integer, db.ForeignKey('car.id'))
)


class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    cars = db.relationship('Car', secondary=customer_car_association, backref=db.backref('customers', lazy='dynamic'))

    def assign_car(self, car):
        if car not in self.cars:
            self.cars.append(car)

    def unassign_car(self, car):
        if car in self.cars:
            self.cars.remove(car)


@app.route("/customers", methods=["POST", "GET"])
def get_customers():
    if request.method == "POST":
        try:
            name = request.json['name']
            phone = request.json['phone']

            if name and phone:
                new_customer = Customer(name=name, phone=phone)
                db.session.add(new_customer)
                db.session.commit()
                app.logger.info("Received request (POST) to create a new customer: %s", request.form)
                return jsonify({'message': 'success'})
            else:
                return jsonify({'error': 'Invalid customer data.'}, 400)
        except Exception as e:
            db.session.rollback()
            app.logger.error("Error while processing the request (POST) to create a new customer: %s", str(e))
            return jsonify({'error': str(e)}, 500)

    elif request.method == "GET":
        customers_data = Customer.query.all()
        customer_list = [
            {
                'id': customer.id,
                'name': customer.name,
                'phone': customer.phone
            }
            for customer in customers_data
        ]
        app.logger.info("Received request (GET) to retrieve the list of customers.")
        return jsonify({'customers': customer_list})


@app.route("/customers/<int:customer_id>", methods=["GET", "PUT", "DELETE"])
def get_update_delete_customer(customer_id):
    customer = Customer.query.get(customer_id)
    if customer is None:
        return jsonify({'error': 'Customer not found.'}, 404)

    if request.method == "GET":
        return jsonify({
            'id': customer.id,
            'name': customer.name,
            'phone': customer.phone
        })
    elif request.method == "PUT":
        try:
            name = request.json.get('name', customer.name)
            phone = request.json.get('phone', customer.phone)

            if name and phone:
                customer.name = name
                customer.phone = phone
                db.session.commit()
                app.logger.info("Received request (PUT) to update customer data: %s", request.form)
                return jsonify({'message': 'Customer data updated.'})
            else:
                return jsonify({'error': 'Invalid customer data.'}, 400)
        except Exception as e:
            db.session.rollback()
            app.logger.error("Error while processing the request (PUT) to update customer data: %s", str(e))
            return jsonify({'error': str(e)}, 500)

    elif request.method == "DELETE":
        db.session.delete(customer)
        db.session.commit()
        return jsonify({'message': 'Customer deleted.'})


if __name__ == "__main__":
    app.run(debug=True, port=5001)
