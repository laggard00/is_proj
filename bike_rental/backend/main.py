from flask import Flask, request, jsonify
from flask_cors import CORS
from pony.orm import *
from pony.orm.core import ObjectNotFound
import os
from datetime import datetime
from dateutil.parser import parse

app = Flask(__name__)
CORS(app)
db = Database()

class Bicikl(db.Entity):
    id = PrimaryKey(int, auto=True)
    serijskibroj = Required(str, max_len=500, unique=True)
    slika = Optional(str)
    naziv = Required(str, max_len=500)
    rezervacije = Set('Rezervacija')

class Rezervacija(db.Entity):
    id = PrimaryKey(int, auto=True)
    bicikl = Required(Bicikl)
    datumod = Required(datetime)
    datumdo = Required(datetime)
    rezervacijazavrsena = Required(int, default=0)  # 0 = active, 1 = finished
    telefonskibroj = Required(str, max_len=50)

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://bike_user:bike_password@localhost:5432/bike_rental')
db.bind('postgres', DATABASE_URL)
db.generate_mapping(create_tables=True)

def seed_data():
    with db_session:
        if Bicikl.select().count() == 0:
            bike1 = Bicikl(serijskibroj="BIKE-001", naziv="Mountain Bike", slika="mountain.jpg")
            bike2 = Bicikl(serijskibroj="BIKE-002", naziv="City Bike", slika="city.jpg")
            bike3 = Bicikl(serijskibroj="BIKE-003", naziv="Road Bike", slika="road.jpg")
            Rezervacija(
                bicikl=bike1,
                datumod=datetime(2025, 9, 6, 10, 0),
                datumdo=datetime(2025, 9, 6, 14, 0),
                telefonskibroj="123456789"
            )
            Rezervacija(
                bicikl=bike2,
                datumod=datetime(2025, 9, 7, 9, 0),
                datumdo=datetime(2025, 9, 7, 12, 0),
                telefonskibroj="987654321"
            )
            commit()

seed_data()


@app.route('/')
def index():
    return jsonify({"status": "ok", "message": "Api radi"})

@app.route('/api/bikes', methods=['GET'])
def list_bikes():
    with db_session:
        bikes = [b.to_dict() for b in Bicikl.select()]
        return jsonify(bikes)

@app.route('/api/bikes', methods=['POST'])
def add_bike():
    data = request.json
    try:
        with db_session:
            bike = Bicikl(
                serijskibroj=data['serijskibroj'],
                naziv=data['naziv'],
                slika=data.get('slika', '')
            )
            commit()
            return jsonify({"message": "Bike add success", "bike": bike.to_dict()}), 201
    except Exception as e:
        return jsonify({"error": "Greška kod dodavanja"}), 400


@app.route('/api/bikes/<int:bike_id>', methods=['PUT'])
def edit_bike(bike_id):
    data = request.json
    with db_session:
        try:
            bike = Bicikl[bike_id]
            bike.serijskibroj = data['serijskibroj']
            bike.naziv = data['naziv']
            bike.slika = data.get('slika', '')
            commit()
            return jsonify({"message": "Update uspjesan", "bike": bike.to_dict()})
        except ObjectNotFound:
            return jsonify({"error": "Bicikl ne postoji"}), 404
        except Exception as e:
            return jsonify({"error": "Greška u sustavu"}), 500


@app.route('/api/bikes/<int:bike_id>', methods=['DELETE'])
def delete_bike(bike_id):
    with db_session:
        try:
            bike = Bicikl[bike_id]
            bike.delete()
            commit()
            return jsonify({"message": "Bicikl izbrisan"})
        except ObjectNotFound:
            return jsonify({"error": "Bicikl nije pronađen"}), 404
        except Exception as e:
            return jsonify({"error": "Greška kod brisanja"}), 500

@app.route('/api/reservations', methods=['GET'])
def list_reservations():
    with db_session:
        reservations = [r.to_dict() for r in Rezervacija.select().order_by(desc(Rezervacija.datumod))]
        return jsonify(reservations)


@app.route('/api/reservations', methods=['POST'])
def add_reservation():
    data = request.json
    with db_session:
        try:
            bike_id = int(data['bike_id'])
            start = parse(data['datumod'])
            end = parse(data['datumdo'])
            if start >= end:
                return jsonify({"error": "Greška, krivi datumi"}), 400
            bike = Bicikl[bike_id]
            overlapping = Rezervacija.select(lambda r: r.bicikl == bike and r.rezervacijazavrsena == 0
                and ((r.datumod <= start and start < r.datumdo)
                     or (r.datumod < end and end <= r.datumdo)
                     or (start <= r.datumod and end >= r.datumdo))
            ).count()

            if overlapping > 0:
                return jsonify({"error": "Bicikl je već rezerviran"}), 400
            reservation = Rezervacija(
                bicikl=bike,
                datumod=start,
                datumdo=end,
                telefonskibroj=data['telefonskibroj']
            )
            commit()

            return jsonify({
                "message": "Rezervacija je dodana",
                "reservation": reservation.to_dict()
            }), 201

        except ObjectNotFound:
            return jsonify({"error": "Bicikl nije pronađen"}), 404
        except Exception as e:
            return jsonify({"error": f"Greška kod rezervacije: {str(e)}"}), 500


@app.route('/api/reservations/<int:reservation_id>/finish', methods=['PUT'])
def finish_reservation(reservation_id):
    with db_session:
        try:
            reservation = Rezervacija[reservation_id]
            reservation.rezervacijazavrsena = 1
            commit()
            return jsonify({"message": "Rezervacija je gotova", "reservation": reservation.to_dict()})
        except ObjectNotFound:
            return jsonify({"error": "Rezervacija nije pronađena"}), 404
        except Exception as e:
            return jsonify({"error": "Greška kod rezervacije"}), 400


@app.route('/api/reserved-bikes', methods=['GET'])
def get_reserved_bikes():
    with db_session:
        reserved_bikes = Rezervacija.select(lambda r: r.rezervacijazavrsena == 0)[:]
        result = []
        for reservation in reserved_bikes:
            result.append({
                'id': reservation.id,
                'bike_name': reservation.bicikl.naziv,
                'serial_number': reservation.bicikl.serijskibroj,
                'date_from': reservation.datumod.isoformat(),
                'date_to': reservation.datumdo.isoformat(),
                'phone': reservation.telefonskibroj
            })
        return jsonify(result)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
