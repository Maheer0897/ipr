#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import eventlet
from flask_socketio import SocketIO
from flask_bootstrap import Bootstrap
from flask_mail import Mail, Message
import json
from flask import Flask, render_template
from flask_mqtt import Mqtt



eventlet.monkey_patch()
app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['MQTT_BROKER_URL'] = 'broker.hivemq.com'
app.config['MQTT_BROKER_PORT'] = 1883
app.config['MQTT_CLEAN_SESSION'] = True
app.config['MQTT_USERNAME'] = ''
app.config['MQTT_PASSWORD'] = ''
app.config['MQTT_KEEPALIVE'] = 5
app.config['MQTT_TLS_ENABLED'] = False
app.config['MQTT_LAST_WILL_TOPIC'] = 'home/lastwill'
app.config['MQTT_LAST_WILL_MESSAGE'] = 'bye'
app.config['MQTT_LAST_WILL_QOS'] = 2



app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = "maheersk1997@gmail.com"
app.config['MAIL_PASSWORD'] = "mahiot@2020"
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

app.config.from_object(__name__)

mqtt = Mqtt(app)
socketio = SocketIO(app)

mail =  Mail(app)
bootstrap = Bootstrap(app)

CPU = 0
MEMORY = 0
email_notificcation = False

@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('publish')
def publisher(json_str):
    global CPU, MEMORY
    print("Publish is "+json.loads(json_str)['topic'])
    if(json.loads(json_str)['topic']=="topic/cpu_request"):
        mqtt.publish(json.loads(json_str)['topic'],'a')
        CPU = 1
        mqtt.subscribe('topic/cpu_reply')
    if(json.loads(json_str)['topic']=="topic/mem_request"):
        mqtt.publish(json.loads(json_str)['topic'],'a')        
        mqtt.subscribe('topic/mem_reply')
        MEMORY = 1
    

@socketio.on('subscribe')
def subscriber(json_str):
   
    print(json.loads(json_str))
    
    if(json.loads(json_str)['topic'=='topic/mem_reply']):
         mqtt.subscribe(json.loads(json_str)['topic'])
         print('Subscribing in '+json.loads(json_str)['topic'])
   
    elif(json.loads(json_str)['topic'=='topic/cpu_reply']):
         mqtt.subscribe(json.loads(json_str)['topic'])
         
         print('Subscribing in '+json.loads(json_str)['topic'])
    
         


@socketio.on('unsubscribe_all')
def unsub():
    mqtt.unsubscribe_all()


@mqtt.on_message()
def mqtt_msg(device, user, msg):
    print("Its on message")
    data_dict = dict(
        topic=msg.topic,
        payload=msg.payload.decode(),
        qos=msg.qos,
    )
    print("The topic is ",data_dict['topic'])
    socketio.emit('mqtt_message', data=data_dict)
    info = data_dict['payload']
    if(CPU == 1):
        print("Its in CPU")
        info = info[1:-1]
        info = info.split(',')
        print(info)
        for i in info:
            print(i)
            if(float(i)>50):
              email_notificcation = True
                 
            
    elif(MEMORY == 1):
        print("It is in memory")
        info = info[1:-1]
        info = info.split(',')
        print(info)
        for i in info:
            print(i)
            if(float(i)>80.00):
                email_notificcation = True
    
    print("For email it is "+str(email_notificcation))
    if(email_notificcation):
        
        msg =""
        if(CPU == 1):
            display = "warning !, cpu usage is more than 50%"
        elif(MEMORY == 1):
            display = "Warning !, Memory usage of IoT device is more than 70%"
        try:
            with app.app_context():
                email = Message("IPR MQTT",
                    sender="maheersk1997@gmail.com",
                    recipients=['maheerkbl@gmail.com'])
                email.body= display
                print(email)
                mail.send(email)
        except Exception as ex:
            print(str(ex))
            

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, use_reloader=False, debug=True)
    


