from flask import Flask, request, redirect, jsonify, url_for
from utils import *
from threading import Thread
from werkzeug import secure_filename
app = Flask(__name__)
from modules.exposure.exposure_mod import ExposureMod as Exposure
from modules.qsar.qsar_mod import QSARmod as QSAR
from modules.lcia.net_prediction import NetPrediction as LCIA
from modules.ft.fate_and_transport_lvl4 import FateAndTransport as FAT
import copy


ALLOWED_EXTENSIONS = set(['txt'])
exp = Exposure()
qsar = QSAR()
lcia = LCIA()
fat = FAT()

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/run_job', methods=['POST'])
def run_job():
    if request.method == 'POST':
        if 'file' in request.files and allowed_file(request.files['file'].filename):
            chemical = request.files['file']
        else:
            chemical = request.form['file']

        qsar_results = qsar.run(chemical)[0]
        chem = copy.copy(qsar_results)
        # chem['MD'] = request.form['MD']
        print chem
        fat_results = fat.run(chem)
        print 'fat complete'
        exposure_results = exp.run(fat_results['exposure_inputs'])
        return jsonify({'results':  {
            'exposure': exposure_results,
            'fat': fat_results['fat_outputs'],
            'qsar': qsar_results
            }})
        # do a full test run


# deprecated until basic functionality is more polished
# @app.route('/upload_epi_result', methods=['POST'])
# def upload_file():
#     if request.method == 'POST':
#         epi_file = request.files['file']
#         if epi_file and allowed_file(epi_file.filename):
#             filename = secure_filename(epi_file.filename)
#             chems_array = qsar.run(epi_file)
#             for chem in chems_array:
#                 for module in [ft, exp]:
#                     chem.update(module.run(chem))
#             return jsonify({'parsed_results':chems_array})

#chemspider interaction deprecated until smiles generation solved
# @app.route('/search', methods=['POST'])
# def search_cs():
#     query = request.form['query']
#     chem = chem_spider.get_chem(query)
#     return jsonify(chem)

@app.route('/server_test')
def index():
    return 'Hello'

@app.route('/sikuli_test', methods=['GET'])
def run_sikuli_test():
    result = qsar.run()
    return jsonify(result)

@app.route('/exposure_test', methods=['GET'])
def run_exposure_default_values():
    result = exp.run()
    return jsonify(result)

@app.route('/qsar_test', methods=['GET'])
def run_qsar_default_values():
    result = qsar.run()
    return jsonify({'parsed_results':result})

@app.route('/lcia_test', methods=['GET'])
def run_lcia_default_values():
    result = lcia.predict()
    return jsonify({'parsed_results':result})

@app.route('/test_ft_exposure', methods=['GET'])
def test_ft_exposure():
        fat_outs = fat.run({})
        exposure_results = exp.run(fat_outs['exposure_inputs'])
        return jsonify({'results': exposure_results})

if __name__ == '__main__':
    app.run(debug = True)
