# IoT hackathon

This is boiler-plate code for a Raspberry Pi-based, temperature-monitoring IoT project. As is, the pipeline measures the temperature of Raspberry Pi and sends it to a Confluent Cloud Kafka Cluster. It should give you a good starting point for your own IoT+Kafka projects.

## Confluent Cloud Setup

We'll be using a Confluent Cloud Kafka Cluster for this project. To begin, sign up for a [Confluent Cloud](https://confluent.cloud) account and follow the prompts to create a Basic Cluster.

### Create Topics
Two topics are required in order to get started with this demo.

From the Confluent Cloud landing page, select the `Topics` tab on the left-hand side of the screen, then choose `Create topic`. Name the topic 'raspberry-pi-readings' and `Create with defaults`. Next, create another topic called 'raspberry-pi-metadata', but, this time, select `Show advanced settings`. Set the cleanup policy to compact. (This will ensure that our raspberry pi metadata topic will always keep at least one copy of a given key.)

### Accessing the Cluster
To access the Kafka Cluster, we'll need a bootstrap server, and an API Key and Secret.

From the Confluent Cloud landing page, select `Cluster overview->Cluster settings`. Copy the `Bootstrap server` field and use it on line 1 of the provided `librdkafka.config` file.

Then select `Data Integration->API Keys`. In the upper right hand corner, select `Add Key`. Follow the prompts to create a key and save the newly created Key and Secret for use on lines 6 and 7 of the provided `librdkafka.config` file.

### Schema Registry
This demo pipeline makes use of Confluent Schema Registry. To enable Schema Registry, navigate to the Confluent Cloud Console and select `Schema Registry` from the lower left-hand corner. Continue by selecting `Set Up On My Own`. Then follow the prompts.

Once the Schema Registry has been set up, from the Schema Registry landing page, scroll down to the `API credentials` section. In order to access Schema Registry from a Raspberry Pi, you need to configure an API key and secret. Select the edit icon. Then select `Create key` and follow the prompt. Save the API Key and Secret for use on Line 15 of the provided librdkafka.config file. Also make note of the Schema Registry API endpoint.

## Raspberry Pi
To run this demo pipeline, you'll obviously need a Raspberry Pi. It should be equipped with librdkafka as well as the confluent_kafka Python library.

### Provided Files

* `librdkafka.config`: Contains Kafka configurations as well as keys and secrets for accessing the Confluent Cloud Cluster.
* `raspberry_pi_metadata.py`: Serializes a Raspberry Pi metadata object, and produces it as a Kafka message.
* `raspberry_pi_temperature_monitor.py`: Captures CPU temperature readings from the Raspberry Pi, serializes the reading object, and writes it to Kafka.
* `avro_helper.py`: Assists with the serialization of objects.

### Running
1. Clone this repository from the Raspberry Pi. Enter the API Keys, Secrets, and Schema Registry API Endpoint from above in the provided `librdkafka.config` file.
2. From the cluster landing page, select `Cluster overview` and then `Cluster settings`. Copy the `bootstrap server` and paste it on line 2 of the config file.
3. Execute `raspberry_pi_metadata.py` to write a metadata message to Kafka and ensure that all configurations are correct. You should see a message in the Confluent Cloud Console.
4. Execute `raspberry_pi_temperature_monitor.py` to take readings every 5 seconds. Verify that the readings are making it to the Kafka cluster.

## ksqlDB Analysis
We have also provided some additional sql statements for use in a ksqlDB analysis component of the pipeline. The statements load the readings and metadata datasets, enrich them with one another, and create alerting messages when the Raspberry Pi temperature is too high. To use, create a ksqlDB application on Confluent Cloud and execute the statements one by one.

## Alerting
Once the ksqlDB application is running, you can choose to set up a Telegram bot and send the alerts to your phone using a Kafka Connect HTTP Sink Connector. We have provided a sample Kafka Connect configuration that you may use to bring up a fully-managed Kafka Connect HTTP Sink Connector in Confluent Cloud. Note that you will have to [create your own Telegram bot](https://core.telegram.org/bots/api) in order to make use of this step.

## Web Frontend

Also included in this repo is a simple webserver and client to display readings in a webpage. Again, it should be a good starting point for a more fully-featured project.

### Running The WebServer

First set up a python environment:

```sh
cd webserver
virtualenv env 
source env/bin/activate
pip install -r requirements.txt
```

Next edit `librdkafka.config` with the same values as the Raspberry Pi installation.

Then run the webserver:

```sh
./webserver.py
```

## Web Client

First install the required node packages:

```sh
cd webclient
npm install
```

Then run the development frontend:

```sh
yarn start
```

This should automatically open a webpage that connects to the webserver and streams live readings.

