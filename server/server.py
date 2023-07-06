import socket 
import sys 
import threading 
import time 
import random 
import struct 

reservation_dictionary = {}
cars = []
dates = []

#Create a UDP socket  
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 

#Class for the individual threads
class ServerThread(threading.Thread):
    def __init__(self, ID, message, serverSocket, address):
        #initialize thread
        threading.Thread.__init__(self)
        self.ID = ID 
        self.message = message 
        self.serverSocket = serverSocket
        self.address = address 
    
    #run the thread
    def run(self): 
        print(f"starting thread {self.ID}")
        command = "none"
        car = "none"
        date = "none"
        new_message = f"error, command not processed"
        print(self.message)
        #Get message arguments based off how many were recieved
        if(len(self.message) == 4):
            command, car, date, sequenceID = self.message
        elif(len(self.message) == 3): 
            command, car, sequenceID = self.message
        elif(len(self.message) == 2):
            command, sequenceID = self.message
       

        if(command == "none"):
            pass 
        elif(command == "check"):
            new_message = return_reservations(car, reservation_dictionary); 
        elif(command == "cars"):
            new_message = return_cars(cars)
        elif(command == "dates"):
            new_message = return_dates(dates)
        elif(command == "reserve"): 
            new_message = add_reservation(car, date, reservation_dictionary, cars, dates)
        elif(command == "delete"):
            new_message = remove_reservation(car, date, reservation_dictionary, cars, dates) 
        else:
            new_message = f"error, command not processed"

        final_message = f"{new_message}_{sequenceID}"
        random_val = random.randint(5, 10)   
        time.sleep(random_val)

        serverSocket.sendto(final_message.encode(), self.address)
        print(f"Terminating thread {self.ID}")

def main():
    #Get command line argument
       
    server_port = sys.argv[2] 
    multicast_group = sys.argv[1] 
    
    #Assign port to socket
   
    server_address = ('', int(server_port))
   
    serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    serverSocket.bind(server_address)
    group = socket.inet_aton(multicast_group)
    mreq = struct.pack('4sL', group, socket.INADDR_ANY)
    serverSocket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    
    #get existing reservations, save a list of cars for each date 
    f = open("reservations.txt", 'r')
    for line in f:
        car, date= line.split(" ") 
        if date.strip() in reservation_dictionary: 
            reservation_dictionary[date.strip()].append(car)
        else:  
            reservation_dictionary[date.strip()] = []
            reservation_dictionary[date.strip()].append(car) 
    f.close() 

    #Get available cars and save to list
    f = open("cars.txt", "r")
    for line in f:
        cars.append(line.strip())
    f.close()

    #Get available dates and save to list
    f = open("dates.txt", "r")
    for line in f:
        dates.append(line.strip())
    f.close()

    
    #Wait for commands until server has been quit
    running = True 
    counter = 0 
    while(running):
        #Update file
        make_reservations(reservation_dictionary)

        # Receive the client packet along with the address it is coming from 
        message, address = serverSocket.recvfrom(1024)
        # Decode the message
        message = message.decode().split(":")
        
        serverThread = ServerThread(counter, message, serverSocket, address)
        serverThread.start()
        
        counter = counter + 1 

#return all existing reservations for a given car
def return_reservations(car, reservations):
    message = f"Reservations for {car} are as follow: "
    #get list of cars associated with a date
    for reserved_date, reserved_cars in reservations.items(): 
        #check if any cars reserved on that date are the one provided
        for reserved_car in reserved_cars: 
                if(car == reserved_car):
                    #add that date to list of dates for that car
                    message = message + "\n" + reserved_date.strip()
    return message 

#add a reservation for a given car and date
def add_reservation(car, date, reservations, cars, dates): 
    #check that given car and date are valid
    if(car in cars and date in dates): 
        #check if the date has already been reserved
        if date in reservations:
            reserved_cars = reservations[date]
            #check if given car has been reserved on that date, if it has, return an error message, else, add it
            if car in reserved_cars:
                return f"{car} already reserved on {date}"
            else: 
                reservations[date].append(car)
                return f"{car} reserved for {date}"
        #If date isn't already in use, just add the car
        else:
            reservations[date] = [] 
            reservations[date].append(car)
            return f"{car} reserved for {date}"
    else:
        return "Error. Please enter an available car and date."

#return the list of cars available for rent
def return_cars(cars):
    message = "Cars Available: " 
    for car in cars:
        message = message + f"\n{car}"
    return message

#Return the list of possible dates
def return_dates(dates): 
    message = "Dates Available: " 
    for date in dates:
        message = message + f"\n{date}"
    return message

#Add reservations to reservations file
def make_reservations(reservations): 
    #open file for writing
    f = open("reservations.txt", "w")
    for date, cars in reservations.items():
        for car in cars:
            f.write(f"{car} {date}\n")
    f.close()

#Remove a reservation for a given car and date
def remove_reservation(car, date, reservations, cars, dates): 
    #check that car and date given are valid
    if(car in cars and date in dates): 
        #Check if date has any reservations, if not, return an error message
        if date in reservations:
            reserved_cars = reservations[date]
            #if date is reserved, check if any of reservations are for provided car, if so, remove it 
            if car in reserved_cars:
                reservations[date].remove(car)
                return f"reservation of {car} removed for {date}"
            else: 
                return f"No reservation of {car} for {date} on record"
        else:
            return f"No reservation of {car} for {date} on record"
    else:
        return f"Please enter a valid car and date"

if __name__ == "__main__": 
    main()


        

