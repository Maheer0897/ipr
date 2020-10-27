
import socket
import psutil
import time

def socket_con():
    addr = ("127.0.0.1",8080)
    socket_conn = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    socket_conn.connect(addr) 
    socket_conn.settimeout(60)
    while True:    
            CPU_usage = psutil.cpu_percent()
            CPU_usage = str(CPU_usage)
            message = "CPU usage is: "+ CPU_usage
            print(message)     
            cpu_frame = {'Key':'CPU','Value': CPU_usage}
            socket_conn.send(str(cpu_frame).encode())
            time.sleep(5)
      
socket_con()