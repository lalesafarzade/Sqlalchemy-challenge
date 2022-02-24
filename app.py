import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify


# Database Setup
database_path = "Resources/hawaii.sqlite"
engine = create_engine(f"sqlite:///{database_path}")
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Flask Setup
app = Flask(__name__)

# Flask Routes
@app.route("/")
def welcome():
    
    return (
        f'<h1 style="text-align:center">Welcome to the Surfs_up API!<br/></h1>'
        f'<h2 style="text-align:center">Available Routes(Clickable icons):<br/></h2>'
        f'<h3 style="text-align:center"><a href="/api/v1.0/precipitation">👉</a>/api/v1.0/precipitation<br/></h3>'
        f'<h3 style="text-align:center"><a href="/api/v1.0/stations">👉</a>/api/v1.0/stations<br/></h3>'
        f'<h3 style="text-align:center"><a href="/api/v1.0/tobs">👉</a>/api/v1.0/tobs<br/></h3>'
        f'<h3 style="text-align:center"><a href="/api/v1.0/2015-03-14">(You can change the date!)👉</a>/api/v1.0/2015-03-14<br/></h3>'
        f'<h3 style="text-align:center"><a href="/api/v1.0/2011-03-14/2015-03-28">(You can change the dates!)👉</a>/api/v1.0/2011-03-14/2015-03-28<br/></h3>'
        
    )

@app.route("/api/v1.0/precipitation")
def prcp_date():
    session = Session(engine)
    res=session.query(Measurement.date, Measurement.prcp)
    session.close()

    result=[]
    for date,prcp in res:
        prcp_dict={}
        prcp_dict["date"]=date
        prcp_dict["prcp"]=prcp
        result.append(prcp_dict)
    return jsonify(result)


@app.route("/api/v1.0/stations")
def station_list():
    session = Session(engine)
    res=session.query(Station.name).all()
    session.close()
    all_names = list(np.ravel(res))
    
    return jsonify(all_names)

@app.route("/api/v1.0/tobs")
def tob():
    session = Session(engine)
    most_recent_date=dt.datetime.strptime(session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0], '%Y-%m-%d')
    last_12_months=most_recent_date - dt.timedelta(days=365)
    last_12_months=last_12_months.date()

    most_active_station = session.query(Measurement.station).filter(Measurement.date >= last_12_months)\
       .group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).first()[0] 

    TOBS_ =session.query(Measurement.tobs).filter(Measurement.station == most_active_station).all()
    session.close()
    TOBS = list(np.ravel(TOBS_))
    return jsonify(TOBS)
    
    
@app.route("/api/v1.0/<start>")
def start_day(start):
    session = Session(engine)
    query_ = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).all()
    start_list=list(np.ravel(query_))
    session.close()
    return jsonify(start_list)

@app.route("/api/v1.0/<start>/<end>")
def start_end_day(start,end):
    session = Session(engine)
    query_ = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start,Measurement.date<= end).all()
    start_list=list(np.ravel(query_))
    session.close()
    return jsonify(start_list)        



if __name__ == '__main__':
    app.run(debug=True)