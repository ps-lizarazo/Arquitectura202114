from flask import Flask, jsonify
import validador.queueComm.tasks as queueTasks

app = Flask(__name__)

@app.route("/")
def validacion():
    tasks_responses = queueTasks.solicitarValidacion(5)
    workers_error = []

    for task_response in tasks_responses:
        if task_response['validacion']['error']:
            workers_error.append(task_response['worker_name'])
            
    response = {
        "task_responses" : tasks_responses,
        "servicios_errores": workers_error,
        "message": f"El servicio funcionando mal es: {(', ').join(workers_error)}, esta info se envia al componente de correcion para que realice el enmascaramiento"
    }

    return jsonify( 
            response
        )