# @Author Emmitt Luhning

import socket
import sys
import struct 

server_port = sys.argv[2] 
multicast_ip = sys.argv[1] 

multicast_group = (multicast_ip, int(server_port))
#create spclet
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#add timeout
clientSocket.settimeout(11)

cars_cache = []
dates_cache = []

ttl = struct.pack('b', 1) 
clientSocket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

running = True
count = 0

#run while flag has not been set to false
while(running):
    message = input(f"Enter message in format: <command>:<car>, <command>:<car>:<date> if applicable, or quit to quit: ").split(":")
    #check how many arguments were given along with the command, get values appropriately
    if(len(message) == 3):
      command, car, date = message
    elif(len(message) == 2): 
        command, car = message
    elif(len(message) == 1):
        command = message[0]
    else:
        print("Please try again with valid input") 
    

    #Including sequence number, last value in message will be sequence number
    count = count + 1
    modified_mesage = ""
    #Format message depending on how many arguments it has
    if(len(message) == 3):
        print(f"Sending command: {command} for car: {car} on date: {date}\n\n")
        message = f"{command}:{car}:{date}:{count}"
    elif(len(message) == 2): 
        print(f"Sending command: {command} for car: {car}\n\n")
        message = f"{command}:{car}:{count}"
    elif(len(message) == 1):
        print(f"Sending command: {command}\n\n")
        message = f"{command}:{count}"
    
    #if command is associated with cached info, check to see if it has been cached 
    if(command == "cars" and len(cars_cache) > 0 ):
        print("Retrieving cars from cache")
        for i in cars_cache:
            print(i)
    elif(command == "dates" and len(dates_cache) > 0):
        print("Retrieving cars from cache")
        for i in dates_cache:
            print(i)
    else:
        #Send message
        clientSocket.sendto(message.encode(), multicast_group)
   
        #Send message, if timweout occurs, try again. 
        while(True):
            try:
                modified_message, server_address = clientSocket.recvfrom(2048) 
                message, sequenceID = modified_message.decode().split("_")
                intro, response = message.split(":")
                        #ignore residual messages from previous calls to server by checking against sequence number
                if int(sequenceID) == count:
                    break
            except socket.timeout:
                print("TImeout Occured")
        
        responses = response.split("\n") 
        #if the results are for cars or dates, add to cache 
        if command == "cars": 
            responses = response.split("\n")
            print("Cars available:")
            for i in responses:
                    cars_cache.append(i) 
        elif command == "dates":
            responses = response.split("\n")
            print("Dates available:")
            for i in responses:
                    dates_cache.append(i) 
        print(f"Reply from server: \n{message}\n")

clientSocket.close() 