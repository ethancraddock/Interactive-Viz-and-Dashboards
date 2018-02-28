import numpy as np
import pandas as pd
import OS

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect, desc

from flask import (
    Flask, 
    render_template,
    jsonify,
    request, 
    redirect)


#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Database Setup
#################################################

from flask_sqlalchemy import SQLAlchemy

engine = create_engine("sqlite:///DataSets/belly_button_biodiversity.sqlite")

# Reflecting db into a new model
Base = automap_base()

# reflect tables
Base.prepare(engine, reflect=True)


# Save to class
Mtadata = Base.classes.samples_metadata
Otu = Base.classes.otu
Samples = Base.classes.samples


session = Session(engine)

def __repr__(self):
    return '<Bio %r>' % (self.name)



# Create a route that renders the index.html homepage template
@app.route("/")
def home():
    return render_template("index.html")

#Create a route that renders a list of the sample names
@app.route("/names")
def names_list():

    # Create inspector and connect it to the engine
    inspector = inspect(engine)

    # Collect the names of the tables within the db
    tables = inspector.get_table_names()

    # using the inspector to print the column names of tables
    columns = inspector.get_columns('samples')

    names = []

    for column in columns[1:]:
        names.append(column['name'])

    return jsonify(names)

# List of OTU descriptions in the
# ex . "Archaea;Euryarchaeota;Halobacteria;Halobacteriales;Halobacteriaceae;Halococcus",
#        "Bacteria",

@app.route("/otu")
def description():
    results = session.query(Otu.lowest_taxonomic_unit_found).all()

    otu_results = []

    for result in results:
        otu_results.append(result[0])

    return jsonify(otu_results)

# Return jsonify dict of sample metadata
'''{
        AGE: 24,
        BBTYPE: "I",
        ETHNICITY: "Caucasian",
        GENDER: "F",
        LOCATION: "Beaufort/NC",
        SAMPLEID: 940
    }'''
@app.route('/metadata/<sample>')
def sample_meta(sample):
    sample_id = sample[3:]

    result = session.query(Mtadata.AGE, Mtadata.BBTYPE, Mtadata.ETHNICITY, Mtadata.GENDER, Mtadata.LOCATION,\
        Mtadata.SAMPLEID).filter(Mtadata.SAMPLEID==sample_id).first()

    metadict = {
        "AGE": result[0],
        "BBTYPE": result[1],
        "ETHNICITY": result[2],
        "GENDER": result[3],
        "LOCATION": result[4],
        "SAMPLEID": result[5]
    }

    return jsonify(metadict)


'''Args: Sample in the format: `BB_940`
Returns an integer value for the weekly washing frequency `WFREQ`
'''
@app.route('/wfreq/<sample>')
def wfreq(sample):
    sample_id = sample[3:]
    result = session.query(Mtadata.WFREQ, Mtadata.SAMPLEID)\
                    .filter(Mtadata.SAMPLEID == sample_id).first()
    return jsonify(result[0])


"""OTU IDs and Sample Values for a given sample.

    Sort your Pandas DataFrame (OTU ID and Sample Value)
    in Descending Order by Sample Value

    Return a list of dictionaries containing sorted lists  for `otu_ids`
    and `sample_values`

    [
        {
            otu_ids: [
                1166,
                2858,
                481,
                ...
            ],
            sample_values: [
                163,
                126,
                113,
                ...
            ]
        }
    ]
    """


# OTU IDs and sample values
@app.route('/samples/<sample>')
def samp(sample):
    sample_id_query = f"Samples.{sample}"
    results = session.query(Samples.otu_id, sample_id_query).order_by(desc(sample_id_query)).all()
    sampdict = {"otu_ids": [result[0] for result in results],
                "sample_values": [result[1] for result in results]}
    return jsonify(sampdict)



if __name__ == '__main__':
   port = int(os.environ.get('PORT', 5000))
   app.run(host='0.0.0.0', port = port, debug=True)






