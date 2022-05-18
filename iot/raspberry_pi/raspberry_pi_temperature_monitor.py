import time
import json
import logging

import gpiozero as gz

from confluent_kafka import SerializingProducer
from confluent_kafka.serialization import StringSerializer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer

import avro_helper


# set up configs
conf = avro_helper.read_ccloud_config("./librdkafka.config")
schema_registry_conf = {
        'url': conf['schema.registry.url'],
        'basic.auth.user.info': conf['basic.auth.user.info']
}

# set up schema registry
schema_registry_client = SchemaRegistryClient(schema_registry_conf)

reading_avro_serializer = AvroSerializer(
        schema_registry_client = schema_registry_client,
        schema_str = avro_helper.raspberry_pi_reading_schema,
        to_dict = avro_helper.RaspberryPiReading.raspberry_pi_reading_to_dict
)

# set up Kafka producer
producer_conf = avro_helper.pop_schema_registry_params_from_config(conf)
producer_conf['value.serializer'] = reading_avro_serializer
producer = SerializingProducer(producer_conf)

topic = 'raspberry-pi-readings'
pi_id = '0' # assign any ID

# loop to capture temperature readings
while True:
    try:
        # read temperature
        cpu_temp = gz.CPUTemperature().temperature
    
        # send data to Kafka
        reading = avro_helper.RaspberryPiReading(int(pi_id), round(cpu_temp, 3))

        producer.produce(topic, key=pi_id, value=reading) 
        producer.poll()

    except Exception as e:
        print(str(e))

    time.sleep(5)
