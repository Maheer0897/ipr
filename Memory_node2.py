


import psutil
import time
import socket


def socket_con():
    socket_conn = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    addr = ("127.0.0.1",8080)
    socket_conn.connect(addr) 
    socket_conn.settimeout(60)
    while True:    
            virtual_memory = psutil.virtual_memory()
            virtual_memory = virtual_memory[2]
            virtual_memory  = str(virtual_memory)
            message  = "Virtual memory usage: "+ virtual_memory 
            print(message)
            mem_frame = {'Key':'Memory','Value': virtual_memory}
            socket_conn.send(str(mem_frame).encode())
            time.sleep(10)
    socket_conn.close()
        

socket_con()