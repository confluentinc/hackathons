import time
import logging

from confluent_kafka import SerializingProducer
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

raspberry_pi_avro_serializer = AvroSerializer(
        schema_registry_client = schema_registry_client,
        schema_str = avro_helper.raspberry_pi_schema,
        to_dict = avro_helper.RaspberryPi.raspberry_pi_to_dict
)

# set up Kafka producer
producer_conf = avro_helper.pop_schema_registry_params_from_config(conf)
producer_conf['value.serializer'] = raspberry_pi_avro_serializer
producer = SerializingProducer(producer_conf)

topic = 'raspberry-pi-metadata'

# existing pis
pis = {
    # assign any ID
    '0': {
        "pi_id": 5,
        "temperature_high": 26.66667
    }
}

for k,v in pis.items():
    # send data to Kafka
    pi = avro_helper.RaspberryPi(
            v["pi_id"], 
            v["temperature_high"]
        )
    producer.produce(topic, key=k, value=pi) 
    producer.poll()