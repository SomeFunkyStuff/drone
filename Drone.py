import paho.mqtt.client as mqtt
import uuid;
import time;
import json
import subprocess
from sys import argv

class Drone(object):
    def __init__(self,configObj):
        print configObj
        self.config = configObj;
        self.id = uuid.uuid4().hex;


    def on_message(self,client, userdata, msg):
        cmd = json.loads(msg.payload)
        if cmd["executor"] != self.id:
            print "invalid id"
            return
        if "runcmd" == cmd["task"]:
            result = {}
            result["executor"] = self.id;
            result["body"] = subprocess.check_output(cmd["body"], shell=True)
            self.client.publish("status-t", json.dumps(result))



    def on_connect(self,client, userdata, flags, rc):
        print "connect"
        self.client.subscribe("command-t")

    def run(self):
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        self.client.username_pw_set(self.config['username'],self.config['passwd'])
        self.client.connect(self.config['host'],self.config['port'],60)

        while True:
            self.client.loop()
            time.sleep(1)
            status = {}
            status["id"] = self.id;
            status["state"] = "up"
            status["time"] = time.time()
            self.client.publish("status-t",json.dumps(status))




def getopts(argv):
    opts = {}  # Empty dictionary to store key-value pairs.
    while argv:  # While there are arguments left to parse...

        if argv[0][0:2] == '--':  # Found a "-name value" pair.
            opts[argv[0][2:]] = argv[1]  # Add key and value to the dictionary.
        argv = argv[1:]  # Reduce the argument list by copying it starting from index 1.
    return opts




myargs = getopts(argv)
Drone(myargs).run()