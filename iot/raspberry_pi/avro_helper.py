import argparse, sys
from confluent_kafka import avro, KafkaError
from confluent_kafka.admin import AdminClient, NewTopic
from uuid import uuid4
import certifi

raspberry_pi_schema = """
{ 
    "name": "raspberrypi",
    "namespace": "com.hackathons.iot",
    "type": "record",
    "doc": "Raspberry Pi metadata.",
    "fields": [
        {
            "doc": "Unique pi identification number.",
            "name": "pi_id",
            "type": "int"
        },
        {
            "doc": "Highest temperature limit of the pi.",
            "name": "temperature_high",
            "type": "float"
        }
    ]
}
"""

class RaspberryPi(object):
    """Raspberry Pi stores the deserialized Avro record for the Kafka key."""
    # Use __slots__ to explicitly declare all data members.
    __slots__ = [
        "pi_id", 
        "temperature_high"
    ]
    
    def __init__(self, pi_id, temperature_high):
        self.pi_id            = pi_id
        self.temperature_high = temperature_high

    @staticmethod
    def dict_to_raspberry_pi(obj, ctx):
        return RaspberryPi(
                obj['pi_id'],   
                obj['temperature_high']   
            )

    @staticmethod
    def raspberry_pi_to_dict(raspberry_pi, ctx):
        return RaspberryPi.to_dict(raspberry_pi)

    def to_dict(self):
        return dict(
                    pi_id            = self.pi_id, 
                    temperature_high = self.temperature_high
                )


raspberry_pi_reading_schema = """
{ 
    "name": "reading",
    "namespace": "com.hackathons.iot",
    "type": "record",
    "doc": "Raspberry Pi measurements.",
    "fields": [
        {
            "doc": "Unique pi identification number.",
            "name": "pi_id",
            "type": "int"
        },
        {
            "doc": "Temperature in degrees C of the Raspberry Pi.",
            "name": "temperature",
            "type": "float"
        }
    ]
}
"""

class RaspberryPiReading(object):
    """Reading stores the deserialized Avro record for the Kafka key."""
    # Use __slots__ to explicitly declare all data members.
    __slots__ = [
        "pi_id",
        "temperature"
    ]
    
    def __init__(self, pi_id, temperature):
        self.pi_id       = pi_id
        self.temperature = temperature

    @staticmethod
    def dict_to_raspberry_pi_reading(obj, ctx):
        return RaspberryPiReading(
                obj['pi_id'],   
                obj['temperature'],    
            )

    @staticmethod
    def raspberry_pi_reading_to_dict(reading, ctx):
        return RaspberryPiReading.to_dict(reading)

    def to_dict(self):
        return dict(
                    pi_id       = self.pi_id,
                    temperature = self.temperature
                )


def read_ccloud_config(config_file):
    """Read Confluent Cloud configuration for librdkafka clients"""
    conf = {}
    with open(config_file) as fh:
        for line in fh:
            line = line.strip()
            if len(line) != 0 and line[0] != "#":
                parameter, value = line.strip().split('=', 1)
                conf[parameter] = value.strip()

    conf['ssl.ca.location']=certifi.where()
    return conf


def pop_schema_registry_params_from_config(conf):
    """Remove potential Schema Registry related configurations from dictionary"""
    conf.pop('schema.registry.url', None)
    conf.pop('basic.auth.user.info', None)
    conf.pop('basic.auth.credentials.source', None)
    
    return conf