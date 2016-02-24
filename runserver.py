from flask import Flask, request, redirect, jsonify, url_for, g
from utils import *
import copy
from random import randint
from threading import Thread
from werkzeug import secure_filename
from modules.exposure.exposure_mod import ExposureMod as Exposure
from modules.qsar.qsar_mod import QSARmod as QSAR
from modules.lcia.net_prediction import NetPrediction as LCIA
from modules.ft.fate_and_transport_lvl4 import FateAndTransport as FAT
from celery import Celery
from flask.ext.sendmail import Mail, Message




app = Flask(__name__)
mail = Mail(app)
app.config.update(
    CELERY_BROKER_URL='amqp://guest:guest@localhost:5672//'
)

def make_celery(app):
    celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task
    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery

celery = make_celery(app)

ALLOWED_EXTENSIONS = set(['txt'])
exp = Exposure()
qsar = QSAR()
lcia = LCIA()
fat = FAT()

app.tickets = {}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def after_this_request(func):
    if not hasattr(g, 'call_after_request'):
        g.call_after_request = []
    g.call_after_request.append(func)
    return func

@app.after_request
def per_request_callbacks(response):
    for func in getattr(g, 'call_after_request', ()):
        response = func(response)
    return response

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

def test_run():
    qsar_results = qsar.run()[0]
    chem = copy.copy(qsar_results)
    print(chem)
    fat_results = fat.run()
    chem.update(fat_results['exposure_inputs'])
    exposure_results = exp.run(chem)
    return {'results':  {
        'exposure': exposure_results,
        'fat': fat_results['fat_outputs'],
        'qsar': qsar_results
        }}


@celery.task(name='__main__.send_status_email')
def send_status_email(ticket):
    # send an email regarding ticket status
    msg = Message("CLiCC Tool Result Status", sender=("no-reply","no-reply"))
    msg.body = """Hello, the results of {0}, ticket {1}, have returned with a
        status of {2}. Please submit your ticket number for more
        information.""".format(ticket['smiles'], ticket['number'], ticket['status'])
    msg.add_recipient(ticket['email'])
    mail.send(msg)

@celery.task(name='__main__.run_async_job')
def run_async_job(ticket_num):
    # runs the clicc tool asyncronously
    ticket = app.tickets[ticket_num]
    ticket['status'] = 'In Progress'
    print "running celery task."
    chemicals = test_run()
    if chemicals:
        ticket['status'] = 'Complete'
        ticket['results'] = chemicals
        if 'email' in ticket:
            send_status_email.wait(ticket)
    else:
        app.tickets[ticket]['status'] = 'Failed'

@app.route('/get_ticket', methods=['POST'])
def give_ticket():
    # takes a smiles and optional email in form and returns a ticket number
    smiles = {'smiles_in': request.form['smiles']}
    ticket_num = None
    while not ticket_num or ticket_num in app.tickets:
        ticket_num = str(randint(1, 9999))
    app.tickets[ticket_num] = {'status': 'Queued',
                               'smiles': smiles,
                               'number': ticket_num}
    try:
        email = 'email': request.form['email']
        app.tickets[ticket_num]['email'] = emailS
    run_async_job.delay(ticket_num)
    return ticket


@app.route('/check_ticket', methods=['POST'])
def check_ticket():
    # check status of a ticket.
    ticket_num = str(request.form['ticket'])
    print ticket
    print app.tickets
    try:
        ticket = app.tickets[ticket_num]
        if ticket['status'] == 'Complete':
            result = app.tickets.pop(ticket, None)
            return jsonify(result)
        elif ticket:
            return ticket['status']
    except:
        return "Ticket not found."



if __name__ == '__main__':
    app.run(debug = True)
    # celery -A your_application worker
