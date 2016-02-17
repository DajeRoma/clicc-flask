from flask import Flask, request, redirect, jsonify, url_for
from utils import *
import copy
from threading import Thread
from werkzeug import secure_filename
from modules.exposure.exposure_mod import ExposureMod as Exposure
from modules.qsar.qsar_mod import QSARmod as QSAR
from modules.lcia.net_prediction import NetPrediction as LCIA
from modules.ft.fate_and_transport_lvl4 import FateAndTransport as FAT

app = Flask(__name__)

ALLOWED_EXTENSIONS = set(['txt'])
exp = Exposure()
qsar = QSAR()
lcia = LCIA()
fat = FAT()

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/run_job', methods=['POST','GET'])
def run_job():
    if request.method == 'POST':
        if 'file' in request.files and allowed_file(request.files['file'].filename):
            chemical = {'file_in': request.files['file']}
        else:
            chemical = {'smiles_in': request.form['smiles']}

        try:
            qsar_results = qsar.run(chemical)
            if not qsar_results:
                raise ModuleError("Qsar Module Failed")
            chem = copy.copy(qsar_results)
            # chem['MD'] = request.form['MD']
            fat_results = fat.run(chem)
            if not fat_results:
                raise ModuleError("FaT Module Failed")
            exposure_results = exp.run(fat_results['exposure_inputs'])
            if not exposure_results:
                raise ModuleError("Exposure Module Failed")
        except ModuleError:
            return jsonify()

        else:
            return jsonify({'results':  {
                'exposure': exposure_results,
                'fat': fat_results['fat_outputs'],
                'qsar': qsar_results
                }})
    else:
        # Do a test run if method is GET. This wont trigger sikuli scripts, but
        # runs everything else as normal.
        qsar_results = qsar.run()[0]
        chem = copy.copy(qsar_results)
        print(chem)
        fat_results = fat.run()
        chem.update(fat_results['exposure_inputs'])
        exposure_results = exp.run(chem)
        return jsonify({'results':  {
            'exposure': exposure_results,
            'fat': fat_results['fat_outputs'],
            'qsar': qsar_results
            }})

@app.route('/qsar_batch', methods=['POST'])
def qsar_batch():
    # import pdb; pdb.set_trace()
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





# Test routes using seed data
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

@app.route('/ft_exposure_test', methods=['GET'])
def test_ft_exposure():
        fat_outs = fat.run({})
        exposure_results = exp.run(fat_outs['exposure_inputs'])
        return jsonify({'results': exposure_results})

if __name__ == '__main__':
    app.run(debug = True)
