from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from datetime import datetime

DATABASE_URL = "postgresql://postgres:Flight02!@flight-price-trends.c9y8o80emv53.us-east-2.rds.amazonaws.com:5432/FlightPriceDB"

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Airline(db.Model):
    __tablename__ = "airlines"
    airline_id = db.Column(db.String(100), primary_key=True)
    airline_name = db.Column(db.Text, nullable=False)

class CabinClass(db.Model):
    __tablename__ = "cabin_class"
    cabin_class_id = db.Column(db.String(5), primary_key=True)
    cabin_class = db.Column(db.String(20), nullable=False)

class Airport(db.Model):
    __tablename__ = "airports"
    airport_id = db.Column(db.String(100), primary_key=True)
    name = db.Column(db.Text, nullable=False)
    iata_code = db.Column(db.String(5), unique=True, nullable=False)
    city = db.Column(db.String(50), nullable=False)

class FlightNumber(db.Model):
    __tablename__ = "flight_numbers"
    flight_id = db.Column(db.Integer, primary_key=True)
    flight_number = db.Column(db.String(10), nullable=False)

class ItineraryDetails(db.Model):
    __tablename__ = "itinerary_details"
    itinerary_id = db.Column(db.String(100), primary_key=True)
    flight_id = db.Column(db.Integer, primary_key=True)
    departure_date_time = db.Column(db.DateTime, nullable=False)
    arrival_date_time = db.Column(db.DateTime, nullable=False)

class FlightPrice(db.Model):
    __tablename__ = "flight_price"
    flight_price_id = db.Column(db.Integer, primary_key=True)
    one_way_price_candollar = db.Column(db.Integer, nullable=False)
    itinerary_id = db.Column(db.String(100), nullable=False)

@app.route('/')
def welcome():
    return (
        f"Welcome to Your One Way Destination Flight Price Analysis API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/airlines - List of airlines<br/>"
        f"/api/v1.0/cabin_classes - Available cabin classes<br/>"
        f"/api/v1.0/airports - Show airports with the number of flights<br/>"
        f"/api/v1.0/flights - List all flights<br/>"
        f"/api/v1.0/itinerary - Show flight prices, and itinerary details<br/>"
        f"/api/v1.0/flights-by-date?start_date=<YYYY-MM-DD> - Flights available on a specific date with prices<br/>"
        f"/api/v1.0/flight_price_analysis - Top 3 Cheapest Months to Travel, Holiday Price Trends, Min/Avg/Max price per month<br/>"
    )

@app.route('/api/v1.0/airlines', methods=['GET'])
def get_airlines():
    airlines = Airline.query.all()
    return jsonify([{'airline_id': a.airline_id, 'airline_name': a.airline_name} for a in airlines])

@app.route('/api/v1.0/cabin_classes', methods=['GET'])
def get_cabin_classes():
    cabin_classes = CabinClass.query.all()
    return jsonify([{'cabin_class_id': c.cabin_class_id, 'cabin_class': c.cabin_class} for c in cabin_classes])

@app.route('/api/v1.0/airports', methods=['GET'])
def get_airports():
    airports = Airport.query.all()
    return jsonify([{'airport_id': a.airport_id, 'name': a.name, 'iata_code': a.iata_code} for a in airports])

@app.route('/api/v1.0/flights', methods=['GET'])
def get_flights():
    flights = FlightNumber.query.all()
    return jsonify([{'flight_id': f.flight_id, 'flight_number': f.flight_number} for f in flights])

@app.route('/api/v1.0/itinerary', methods=['GET'])
def get_itinerary():
    itinerary_data = db.session.query(ItineraryDetails, FlightPrice.one_way_price_candollar).outerjoin(
        FlightPrice, ItineraryDetails.itinerary_id == FlightPrice.itinerary_id
    ).order_by(ItineraryDetails.departure_date_time).all()
    
    result = []
    for itinerary, price in itinerary_data:
        result.append({
            'itinerary_id': itinerary.itinerary_id,
            'flight_id': itinerary.flight_id,
            'departure_date_time': itinerary.departure_date_time,
            'arrival_date_time': itinerary.arrival_date_time,
            'one_way_price_candollar': float(price) if price else None
        })
    return jsonify(result)

@app.route('/api/v1.0/flights-by-date', methods=['GET'])
def get_flights_by_date():
    start_date = request.args.get('start_date')
    if not start_date:
        return jsonify({'error': 'Please provide start_date in YYYY-MM-DD format'}), 400
    try:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    flights = db.session.query(ItineraryDetails, FlightPrice.one_way_price_candollar).outerjoin(
        FlightPrice, ItineraryDetails.itinerary_id == FlightPrice.itinerary_id
    ).filter(ItineraryDetails.departure_date_time >= start_date).order_by(ItineraryDetails.departure_date_time).all()
    
    result = []
    for details, price in flights:
        result.append({
            'flight_id': details.flight_id,
            'departure_date_time': details.departure_date_time,
            'one_way_price_candollar': float(price) if price else None
        })
    return jsonify(result)

@app.route('/api/v1.0/flight_price_analysis', methods=['GET'])
def flight_price_analysis():
    analysis = db.session.execute(text(
        """
        SELECT TO_CHAR(DATE_TRUNC('month', departure_date_time), 'YYYY-MM') AS month,
               ROUND(COALESCE(MIN(one_way_price_candollar), 0), 2) AS min_price,
               ROUND(COALESCE(AVG(one_way_price_candollar), 0), 2) AS avg_price,
               ROUND(COALESCE(MAX(one_way_price_candollar), 0), 2) AS max_price
        FROM flight_price
        JOIN itinerary_details ON flight_price.itinerary_id = itinerary_details.itinerary_id
        GROUP BY 1
        ORDER BY 1;
        """
    )).fetchall()

    best_months = sorted(analysis, key=lambda x: x[1] if x[1] is not None else float('inf'))[:3]
    best_months_text = f"The most affordable months to travel are: {', '.join([f'{row[0]} (CAD {row[1]:.2f})' for row in best_months])}."
    
    holiday_trends = [row for row in analysis if row[0][-2:] in ('03', '06', '10', '12')]
    holiday_trends_data = [{'month': row[0], 'avg_price': f"{row[2]:.2f}"} for row in holiday_trends]
    holiday_trends_summary = "Based on seasonal trends, the average flight prices for key holiday months (March, June, October, December) are:"
    
    monthly_prices_data = [{'month': row[0], 'min_price': f"{row[1]:.2f}", 'avg_price': f"{row[2]:.2f}", 'max_price': f"{row[3]:.2f}"} for row in analysis]
    
    response = [
        {'best_months': best_months_text},
        {'holiday_trends_summary': holiday_trends_summary},
        {'holiday_trends': holiday_trends_data},
        {'monthly_prices': monthly_prices_data}
    ]

    return jsonify(response)

if __name__ == "__main__":
    app.run(debug=True)



