from threading import Thread
from flask import Flask, jsonify
from kombu import Connection
from queueComm.receiver import Receiver
import tasks.validar as servicioTasks
import sys

app = Flask(__name__)

@app.route("/")
def agendar_cita_medica():

    response = {}
    if worker_name == 'servicio_tres':
        response = servicioTasks.agendarCitaMedica('fail')
    else:
        response = servicioTasks.agendarCitaMedica()

    return jsonify(
            response
        )

if __name__ == '__main__':
    #Example execution: python app.py <NOMBRE-SERVICIO> <PUERTO>
    worker_name = sys.argv[1]
    connection = Connection('amqp://guest:guest@localhost:5672//')
    print(' [x] Awaiting messages')
    worker = Receiver(connection, worker_name)
    worker = Thread(target=worker.run)
    worker.start()
    app.run(port=sys.argv[2])


