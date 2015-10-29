from flask import Flask
from flask import request
from flask import jsonify
from utils import *
from modules import *
app = Flask(__name__)


@app.route('/submit', methods=['POST'])
def run_job():
    query = request.form['query']
    chem = chem_spider.get_chem(query)
    if chem:
        results = modules.run(chem)[0]
        return jsonify(results)
    else:
        return 204




@app.route('/search', methods=['POST'])
def search_cs():
    query = request.form['query']
    # hooks=dict(response=print_url)
    chem = chem_spider.get_chem(query)
    return jsonify(chem)



if __name__ == '__main__':
    app.run(debug=True)
