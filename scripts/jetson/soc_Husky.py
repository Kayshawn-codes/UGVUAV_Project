import socket
import pickle

HEADERSIZE = 8
#Encoding
#pose = []

#pose.append([420.5/1000, -261.9/1000, 75.9/1000, 2.34, 2.34, 0])

#pose.append([-507.9/1000, -446.5/1000, -205.7/1000, 2.34, 2.34, 0])


def send_data(soc: socket, data, protocol):
        bit_data = pickle.dumps(data, protocol=protocol)
        message = '{:<{}}'.format(len(bit_data), HEADERSIZE).encode('utf-8') + bit_data
        soc.send(message)


Husky_IP = "192.168.1.118"
Husky_PORT = 11234      # Port collision. Change Port.

def pose_send(pose):
     sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
     sock.connect((Husky_IP, Husky_PORT))
     print ("Connected to Husky")
     send_data(sock, pose, protocol=2)
     sock.close()
