# Application Proxy - Python Publisher [![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

This prototype demonstrates how HTTP requests can be wrapped into a message that is sent to a topic or
queue using different messaging technologies.
Therefore, it uses a generic driver approach, whereby drivers can be exchanged for each startup.
A driver implements the communication to a message broker such as [Mosquitto](https://mosquitto.org/)
or [RabbitMQ](https://rabbitmq.com/).

Currently, only a MQTT driver is implemented.

## Set Up

This prototype uses python 3.

1. Run `pip3 install ./drivermanager` to install the provided interface of a driver.
2. Run `pip3 install ./drivermqtt` to install the current MQTT driver.
3. Run `pip3 install -r requirements.txt` to download the dependencies of the Publisher application.
4. Configure your MQTT broker in the `driver-manager.yml`. For example:
   ````yaml
   requestReplyTopic:
     name: my/topic/id
     driver: drivermqtt.MqttDriver
     connection: 1.2.3.4:1883
   ````
5. Start the proxy using `python3 ./publisherProxy/main.py`
   1. You can optionally pass the port as the first argument.
      Default is `9993`.
   2. You can optionally pass the absolute path to the yaml-file that contains the config as the second argument.
      Default is `../driver-managmerr.yml`.

## Haftungsausschluss

Dies ist ein Forschungsprototyp.
Die Haftung für entgangenen Gewinn, Produktionsausfall, Betriebsunterbrechung, entgangene Nutzungen, Verlust von Daten und Informationen, Finanzierungsaufwendungen sowie sonstige Vermögens- und Folgeschäden ist, außer in Fällen von grober Fahrlässigkeit, Vorsatz und Personenschäden ausgeschlossen.

## Disclaimer of Warranty

Unless required by applicable law or agreed to in writing, Licensor provides the Work (and each Contributor provides its Contributions) on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied, including, without limitation, any warranties or conditions of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A PARTICULAR PURPOSE.
You are solely responsible for determining the appropriateness of using or redistributing the Work and assume any risks associated with Your exercise of permissions under this License.
