import datetime as dt

# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

# API from Flask
from flask import Flask, jsonify

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

# Create Routes for Climate App API
app = Flask(__name__)

@app.route('/')
def welcome():
    return (
        f"Welcome to the Hawaiian Weather API!<br><br>"
        f"Available Routes:<br>"
        f"/api/v1.0/precipitation<br>"
        f"/api/v1.0/stations<br>"
        f"/api/v1.0/tobs<br>"
        f"/api/v1.0/tobs/yyyy-mm-dd &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(start date only)<br>"
        f"/api/v1.0/tobs/yyyy-mm-dd/yyyy-mm-dd &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(start and end dates)<br>"
    )


@app.route('/api/v1.0/precipitation')
def precipitation():
    year_prior_date = dt.date.today() + dt.timedelta(days=-365)
    precip_data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= year_prior_date).all()
    precip_dict = []
    
    for row in precip_data:
        precip_dict.append({row[0]:row[1]})
    
    return jsonify(precip_dict)

@app.route('/api/v1.0/stations')
def stations():
    station_data = session.query(Station.id, Station.station, Station.name).all()
    station_dict = []

    for row in station_data:
        station_dict.append({'id':row[0], 'station':row[1], 'name':row[2]})
    
    return jsonify(station_dict)

@app.route('/api/v1.0/tobs')
def tobs():
    year_prior_date = dt.date.today() + dt.timedelta(days=-365)
    tobs_data = session.query(Measurement.date, Measurement.station,Measurement.tobs).filter(Measurement.date >= year_prior_date).all()
    tobs_dict = []
    
    for row in tobs_data:
        tobs_dict.append({'date':row[0], 'station':row[1], 'tobs':row[2]})
    
    return jsonify(tobs_dict)

@app.route('/api/v1.0/tobs/<start>')
def temp_hla_start(start):
    temp_data = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), \
    func.round(func.avg(Measurement.tobs),1)).filter(Measurement.date >= start).all()
    temp_dict = {'TMIN':temp_data[0][0], 'TMAX':temp_data[0][1], 'TAVG':temp_data[0][2]}
    if temp_dict['TMIN'] != None:
        return jsonify(temp_dict)

    return jsonify({"error": f"Temperature data after {start} not found."}), 404

@app.route('/api/v1.0/tobs/<start>/<end>')
def temp_hla_startend(start, end):
    temp_data = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), \
    func.round(func.avg(Measurement.tobs),1)).filter(Measurement.date >= start)\
    .filter(Measurement.date <= end).all()
    temp_dict = {'TMIN':temp_data[0][0], 'TMAX':temp_data[0][1], 'TAVG':temp_data[0][2]}
    if temp_dict['TMIN'] != None:
        return jsonify(temp_dict)

    return jsonify({"error": f"Temperature data between {start} and {end} not found."}), 404    

if __name__ == "__main__":
    app.run(debug=False)

