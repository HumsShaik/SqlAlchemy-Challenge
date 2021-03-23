import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
from dateutil.relativedelta import relativedelta
from datetime import timedelta
import numpy as np


engine = create_engine('sqlite:///Resources/hawaii.sqlite')
Base = automap_base()
Base.prepare(engine, reflect=True)
measurement = Base.classes.measurement
station = Base.classes.station

app = Flask(__name__)

 
@app.route("/")
def home():
    print("Server recieved request for climate app home page...")
    return (
        f"Welcome to the home page of Climate App!<br/>"       
        f"All Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/startdate<br/>"
        f"/api/v1.0/startdate-enddate<br/>"
        f"<br>"
        #f"Note: Replace 'start_date' and 'end_date' with your query dates. Format for querying is 'YYYY-MM-DD'"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    print("Server recieved request of Precipitation page")

    session = Session(engine)

    prcp_data = session.query(measurement.date, measurement.prcp).all()

    session.close()

    prcp_dict = {} 
    for date, prcp in prcp_data:
        prcp_dict[date] = prcp
    
    return jsonify(prcp_dict)


@app.route("/api/v1.0/stations")
def stations():
    print("Server recieved request of Station data page")

    session = Session(engine)
    
    results = session.query(station.id, station.station, station.name).all()

    session.close()

    list_station = []

    for st in results:
        station_dict = {}

        station_dict["id"] = st[0]
        station_dict["station"] = st[1]
        station_dict["name"] = st[2]

        list_station.append(station_dict)

    return jsonify(list_station)


@app.route("/api/v1.0/tobs")
def temp():
       
    session = Session(engine)
    
   
    last_date = session.query(measurement.date).order_by(measurement.date.desc()).first().date

   
    last_date = dt.datetime.strptime(last_date, "%Y-%m-%d")

    
    first_date = last_date - timedelta(days=365)
   
    station_counts = session.query(measurement.station, func.count(measurement.station)).group_by(measurement.station).order_by(func.count(measurement.station).desc()).all()
   
    top_station = (station_counts[0])
    top_station = (top_station[0])
   
    session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)).\
    filter(measurement.station == top_station).all()
    
    top_station_year_obs = session.query(measurement.tobs).\
    filter(measurement.station == top_station).filter(measurement.date >= first_date).all()
    session.close()
    
    return jsonify(top_station_year_obs)
    
    
@app.route("/api/v1.0/startdate")
def tobs_by_date(startdate):
    
    session = Session(engine)
    
    tobs_date = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
         filter(measurement.date >= startdate).all()
   
    session.close()
        
    return jsonify(tobs_date)
    
    
@app.route("/api/v1.0/startdate-enddate")
def tobs_by_date_range(startdate, enddate):
    
    session = Session(engine)
    
    temp_by_date = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= startdate).filter(measurement.date <= enddate).all()
    
    session.close()
    
    return jsonify(temp_by_date)
    

if __name__ == "__main__":
    app.run(debug=True)