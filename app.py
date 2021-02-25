import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

from flask import Flask, jsonify

# Creating engine
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

#  Reflecting database into model
Base = automap_base()

# Reflecting tables
Base.prepare(engine, reflect=True)

# References to tables
Measurement = Base.classes.measurement
Station = Base.classes.station


# Flast Setup
app = Flask(__name__)

@app.route("/")
def welcome():
    print("homepage requested")
    return(
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    print("precipitation requested")
    session = Session(engine)
    results = session.query(Measurement.date, Measurement.prcp).all()
    session.close()

    # Creating dictionary
    all_dates = []
    for date, prcp in results:
        rain_dict = {}
        rain_dict["date"] = date
        rain_dict["prcp"] = prcp
        all_dates.append(rain_dict)

    return jsonify(all_dates)


@app.route("/api/v1.0/stations")
def stations():
    print("stations requested")
    session = Session(engine)
    station_list = session.query(Station.station).all()
    session.close()

    # Creating list
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def temps():
    print("temps requests")
    session = Session(engine)

    # Getting year ago date
    latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    latest_date_dt = dt.datetime.strptime(latest_date[0], "%Y-%m-%d")
    year_earlier = dt.date(latest_date_dt.year-1, latest_date_dt.month, latest_date_dt.day)


    # Getting most active station
    active_stations = session.query(Measurement.station, func.count(Measurement.id)).\
    group_by(Measurement.station).order_by(func.count(Measurement.id).desc()).all()
    most_active_station = active_stations[0][0]
    
    
    # Query for weather at most active station in last year
    temp_obs = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active_station).\
        filter(Measurement.date >= (year_earlier)).all()
    session.close()
    return jsonify(temp_obs)


@app.route("/api/v1.0/<start>")
def start_temp(start):
    session = Session(engine)
    start = dt.datetime.strptime(start, "%Y-%m-%d")
    min_temp = session.query(func.min(Measurement.tobs)).filter(Measurement.date >= start).all()
    max_temp = session.query(func.max(Measurement.tobs)).filter(Measurement.date >= start).all()
    avg_temp = session.query(func.avg(Measurement.tobs)).filter(Measurement.date >= start).all()
    session.close()

    temp_calcs = []

    temp_dict = {}
    temp_dict["Min Temp"] = min_temp
    temp_dict["Max Temp"] = max_temp
    temp_dict["Avg Temp"] = avg_temp
    temp_calcs.append(temp_dict)

    return jsonify(temp_calcs)



@app.route("/api/v1.0/<start>/<end>")
def start_end_temp(start, end):
    session = Session(engine)
    start = dt.datetime.strptime(start, "%Y-%m-%d")
    end = dt.datetime.strptime(end, "%Y-%m-%d")
    min_temp = session.query(func.min(Measurement.tobs)).\
        filter(Measurement.date.between(start, end)).all()
    max_temp = session.query(func.max(Measurement.tobs)).\
        filter(Measurement.date.between(start, end)).all()
    avg_temp = session.query(func.avg(Measurement.tobs)).\
        filter(Measurement.date.between(start, end)).all()

    start_end_temp_calcs = []

    start_end_temp_dict = {}
    start_end_temp_dict["Min Temp"] = min_temp
    start_end_temp_dict["Max Temp"] = max_temp
    start_end_temp_dict["Avg Temp"] = avg_temp
    start_end_temp_calcs.append(start_end_temp_dict)

    return jsonify(start_end_temp_calcs)

if __name__ == "__main__":
    app.run(debug=True)