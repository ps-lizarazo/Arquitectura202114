def agendarCitaMedica(behaviour_param = ''):
    response = {}
    if behaviour_param == 'fail':
        response = {
                "message" : "No se pudo agendar la cita medica",
                "message_error": "Error al persistir en la base de datos",
                "error" : True
            }
    else:
        response = {
            "message": "La cita medica se agendo con exito",
            "message_error" : "",
            "error": False,
        }

    return response