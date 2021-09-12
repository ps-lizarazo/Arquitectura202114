from operator import countOf
from kombu import Exchange, Connection, Producer, uuid, Queue


exchange = Exchange('task_validador', type='fanout')
callback_queue = Queue('reply')


responses = {}

def callback_handler(body, message):
    correlation_id = message.properties["correlation_id"]
    
    if correlation_id not in responses:
        responses[correlation_id] = []

    responses[correlation_id].append(body)
    print(f'{body} + { correlation_id  }')

    message.ack()

def solicitarValidacion(time_to_live = 7):
    correlation_id = uuid()
    responses[correlation_id] = []
    with Connection('amqp://guest:guest@localhost:5672//') as conn:
        with conn.channel() as channel:
            producer = Producer(channel)

            producer.publish(
                {'task_request': 'validar_agendar_cita_medica'}, # message to send
                exchange=exchange, # destination exchange
                routing_key='', # destination routing key,
                declare=[exchange], # make sure exchange is declared,
                reply_to=callback_queue.name,
                correlation_id=correlation_id,
                retry=True,
            )
            # fecha = tiempo_espera_segundos
            with conn.Consumer([callback_queue],
                            callbacks=[callback_handler]) as consumer:
                while True:
                    try:
                        conn.drain_events(timeout=5)
                    except:
                        break
                
                return responses[correlation_id]


                # TODO: Aca chequear los datos consolidados


        

