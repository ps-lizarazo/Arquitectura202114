# Experimento Arquitectura

## ¿Cuál es el punto de sensibilidad?
Queremos experimentar el uso de un validador para que rectifique el buen funcionamiento para cada una de las instancias del microservicio de Agendar Citas mediante comunicación asíncrona para reducir el acoplamiento en la comunicación.

## ¿Qué utiliza el experimento?
El experimento utiliza python junto a Flask para la creación del validador y del microservicio de Agendar Citas; para la comunicación asíncrona utiliza el servicio de mensajería RabbitMQ y para la integración con python utiliza la librería de Kombu que es la que utiliza Celery.

## ¿Cómo ejecuto el experimento?
Se necesita crear inicialmente un ambiente de python en la raiz del proyecto con
```bash
python -m .venv venv #Para windows
python3 -m .venv venv #Para sistemas basados en linux
```
Luego se debe activar dicho ambiente de python e instalar las dependencias mediante:

```bash
pip install -r requirements.txt
```

Para poder ejecutar el proyecto debemos tener una instancia de RabbitMQ en el puerto por default, la manera más sencilla para tener una instancia es con docker utilizando el comando:

```docker
docker run -d -p 5672:5672 rabbitmq
```

Ahora lo que sigue es ejecutar 3 instancias del microservicio de AgendarCitas, para ello ir a la ruta ``./servicio`` y desde allí correr los siguiente comandos en consolas independientes o como procesos independientes:

PD: el ``servicio_tres`` es el mas importante ya que es el que se simula para fallar, la syntax general para correr es: ``python app.py <NOMBRE_SERVICIO> <NUMERO_PUERTO>``

```
python app.py servicio_uno 4001
```

```
python app.py servicio_dos 4002
```

```
python app.py servicio_tres 4003
```
Así tendremos 3 instancias del microservicio a la cuales el validador les hará ejecutar una operación y evaluará su funcionamiento. Un ejemplo de respuesta de agendar cita se puede se puede consultar en ``http://127.0.0.1:<puerto>/``, cabe resaltar que la comunicación entre el validador y los servicios es por RabbitMQ usando el protocolo AMQP y no HTTP.

Ahora debemos ejecutar el validador, para el validador vamos a la ruta ``./validador`` y allí corremos

```
flask run
```

este correrá en el puerto por defecto ``5000``, y expone el endpoint ``/`` en un get para que ejecute la operación de validación, así que deberíamos poder ir a ``http://127.0.0.1:5000/`` y se ejecuta la operación de validación. Ya que existe un desacoplamiento no sabemos cuántos responderán así que existe un TTL de respuestas de 5-7 segundos que será lo que se demore en resolver la operación y a la final veremos un mensaje en formato JSON como este:
```JSON
{
    "message": "El servicio funcionando mal es: servicio_tres, esta info se envia al componente de correcion para que realice el enmascaramiento",
    "servicios_errores": [
        "servicio_tres"
    ],
    "task_responses": [
        {
            "validacion": {
                "error": false,
                "message": "La cita medica se agendo con exito",
                "message_error": ""
            },
            "worker_name": "servicio_dos"
        },
        {
            "validacion": {
                "error": true,
                "message": "No se pudo agendar la cita medica",
                "message_error": "Error al persistir en la base de datos"
            },
            "worker_name": "servicio_tres"
        },
        {
            "validacion": {
                "error": false,
                "message": "La cita medica se agendo con exito",
                "message_error": ""
            },
            "worker_name": "servicio_uno"
        }
    ]
}
```

La respuesta contiene un mensaje descriptivo en ``message`` de lo que ocurrió y cuáles serían los siguientes pasos, una lista de los microservicios que funcionan erroneamente ``servicios_errores`` y el contenido de lo que cada servicio o worker respondió al ejecutar la operación en ``task_responses``, el identificador de cada micro servicio es el ``worker_name``

De esa manera aseguramos la validación y el uso de comunicación asíncrona.