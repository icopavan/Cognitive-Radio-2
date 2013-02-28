################################################################################
# author: Anil Morab                                                           #
# email: anil.morab.vishwanath@aalto.fi                                        #
################################################################################
# The function 'EuProject()' in this file is called from the network_rrm.py    #
# This function acts as an interface between local_rrm.py and network_rrm.py   #
# and between network rrm.py and KTH client                                    #
################################################################################

#!/usr/bin/env python

import socket, select
import time, os, sys

# Port number for interacting with network rrm
LR_port= 7000

# port number of interacting with KTH client
KTH_port= 8000

# Network RRM should know the IP address of the local RRMs 
server=('', 7000)

# Function for interacting with the KTH client
def LR_Interface(k, data):    
    global server
    k.setblocking(1)
    k.sendto(repr(data), server)
    response, addr= k.recvfrom(1024)
    response=eval(response)
    k.setblocking(0)
    return response

# Function for interacting with the local_rrm    
def EuProject():    
    # local RRM socket
    try:
          s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
          s.bind(('',KTH_port))
    except socket.error, (value,message):
          if s:
              s.close()
          print "Could not open socket: " + message
          sys.exit(1)
    
    # KTH client socket
    try:
          k = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    except socket.error, (value,message):
          if k:
              k.close()
          print "Could not open socket: " + message
          sys.exit(1)
          
    try:
        while 1:      
                        try:
                                # Receive data function
                                recv_data, addr = s.recvfrom(1024)            
                                list1=eval(recv_data)
                                
                                # Control Plane
                                recv_data=list1[0]
                                print "Received", recv_data, "from", addr
                                
                                #Data Plane
                                data=list1[1]
                                
                                # Check the value of received data
                                if (recv_data=="ConnectionRequest"):               
                                    print "Sending IP address %s to all RRMs to check for its availability"%data
                                    #data will have IP adress
                                    list2=["Check_availability", data] 
                                    s.setblocking(0)
                                    response= LR_Interface(k, list2)
                                    s.setblocking(1)
                                    
                                    #Response will 1 or 0 based on whether IP is present within the network or not 
                                    if response[1]==1:                            
                                          print "IP address present in %s"%addr[0]
                                          #Send Ack to KTH Server
                                          list1=["Ack", 0]
                                          s.sendto(repr(list1), addr)
                                    else:
                                            print "The provided IP is not present in our system"
                            
                                elif (recv_data=="ConnectionEstablishmentInformation"):
                            
                                    #data will now have URL and IP adress
                                    tup=data
                                    URL=tup[0]
                                    IP_adress=tup[1]
                                    
                                    # Ask for measurement report from local RRM
                                    list2=["Measurement_Report", 0]
                                    s.setblocking(0)
                                    response= LR_Interface(k, list2)
                                    s.setblocking(1)
                                            
                                    # Response[1] will now have feedback, Prepare a list based on the feedback
                                    
                                    # Currently there is no feedback information taken, so preparing a dummy list        
                                    
                                    # Make a list of Connection plans
                                    plans=[('rate1', 'price1'), ('rate2', 'price2'), ('rate3', 'price3')]
                                    list1=["AvailableConnectionPlans", plans]
                                    print "Sending Connection plans to the KTH System"
                                    s.sendto(repr(list1), addr)
                            
                                elif (recv_data=="ConnectionChoice"):
                                    list1=["ConnectionChoiceAck", 0]
                                    s.sendto(repr(list1), addr)
                                    
                                    choice=data # Choice will now have the choice that has been selected by the KTH system
                            
                                    print "You have chosen this plan:"
                                    print choice
                                    # Send tup to local RRM
                                    list2=["ConnectionEstablishmentInformation", tup]
                                    s.setblocking(0)
                                    response= LR_Interface(k, list2)
                                    s.setblocking(1)
                                    
                                    # Once it is done, acknowledge
                                    if (response[0]=="TransferProvided"):
                                          list1=["TransferProvided", 0]
                                          s.sendto(repr(list1), addr)
                            
                                elif (recv_data=="TransferAck"):
                                    s.setblocking(0)
                                    list2=["TransferAck", 0]
                                    response= LR_Interface(k, list2)
                                    s.setblocking(1)            
                        except:
                            s.close()
    
    except KeyboardInterrupt:
                        sys.exit(0)
    
if __name__=='__main__':
    EuProject()
