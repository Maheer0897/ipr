
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import paho.mqtt.client as mqtt
import socket 
from threading import Thread 
import sqlite3

server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
connection = sqlite3.connect("MyDb.db", check_same_thread =False)
c = connection.cursor()

tlreadList = [] 
thread_process_list=list()
        
class nodes_thread(Thread): 
    def __init__(self,ip,port): 
        Thread.__init__(self) 
        self.ip = ip 
        self.port = port 
 
    def run(self): 
       server.listen(4) 
       (conn, (ip,port)) = server.accept() 
       while True : 
            data = conn.recv(2048)
            msg = data.decode()
            data_msg = eval(msg) 
            filter_store(data_msg,ip,port)
            if not data: 
                break
            conn.send(data) 
 
def filter_store(dt,ip,port):
     if(dt['Key']=='Memory'):
        if(float(dt['Value'])>40):
            list_mem = list()
            list_mem.append(dt['Key'])
            list_mem.append(dt['Value'])
            print("Memory Usage more than 40%")
            try:
                c.execute("Insert into MyDb ( Key, Value ) VALUES (?,?)",tuple(list_mem))
                list_mem.clear()
                connection.commit()
                print("Inserted Memory Usage")
            except sqlite3.Error as error:
                print(error)
     elif(dt['Key']=='CPU'):
            if(float(dt['Value'])>30):
                cpu_list = list()
                cpu_list.append(dt['Key'])
                cpu_list.append(dt['Value'])
                print("CPU Usage more than 30%")
                try:
                    c.execute("Insert into MyDb ( Key, Value ) VALUES (?,?)",tuple(cpu_list))
                    cpu_list.clear()
                    connection.commit()
                    print("Inserted CPU Usage")
                except sqlite3.Error as error:
                    print(error)
   
def on_message(client,userdata,message):
    print("On Message")
          
    if(str(message.topic)=="topic/mem_request" ):
        print("topic/mem_request")
   
        try:
            query = "Select * from MyDb Where Key = 'MEM' Order by id DESC LIMIT 10"
            print(query)
            
            datas = c.execute(query)
        except sqlite3.Error as error:
            print(error)
        myList = []
        for d in datas:
            myList.append(d[2])
        print(str(myList))
        
        client.publish("topic/mem_reply",str(myList))
        
    elif(str(message.topic)=="topic/cpu_request" ):
        print("topic/cpu_request")
        try:
            query = "Select * from MyDb Where Key = 'CPU' Order by id DESC LIMIT 10"
            print(query)
            
            datas = c.execute(query)
        except sqlite3.Error as error:
            print(error)
        myList = []
        for d in datas:
            print(d)
            myList.append(d[2])
        print(str(myList))
             
        client.publish("topic/cpu_reply",str(myList))
def on_publish(client,userdata,result): #create function for callback
  print("published data is : ",userdata)
     
class pubsub(Thread):
    def __init__(self,topic):
        Thread.__init__(self)
        self.topic = topic
    def run(self):
        client = mqtt.Client('Chippy')
        client.on_message = on_message  
        client.connect("broker.hivemq.com")
        client.subscribe('topic/mem_request')
        print("Subscribed here topic/mem_request")
        client.subscribe("topic/cpu_request")
        print("Subscribed here topic/cpu_request")
        client.loop_forever()     


if __name__ =="__main__":
    c.execute("CREATE TABLE IF NOT EXISTS MyDb (id INTEGER PRIMARY KEY AUTOINCREMENT,Key TEXT ,Value REAL)")
    server.bind( ("127.0.0.1",8080))
    server.listen(4) 
    (conn, (ip,port)) = server.accept() 
    tlreadList.append(pubsub("topic/cpu_request").start())
    while True: 
        message_recv = conn.recv(1024)
        dt = eval(message_recv)
        filter_store(dt,ip,port)

        newthread = nodes_thread(ip,port)
        newthread.start() 
        tlreadList.append(newthread) 
     
    for td in tlreadList: 
        td.join()
        
        
        