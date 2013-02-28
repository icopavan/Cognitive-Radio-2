################################################################################
# author: Anil Morab                                                           #
# email: anil.morab.vishwanath@aalto.fi                                        #
################################################################################
# This is a sample client program written for the EUProject. Any system that   #
# wishes to interact with the Cognitive Radio network should write a client    #
# program such as this based on the signalling information provided            #
################################################################################

#!/usr/bin/env python

import socket
import os, sys, time

# IP address of the network RRM, the interface point
host = '130.233.158.164'

#Control plane port
control_port= 8000
        
def main():
    try:
          s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    except socket.error, (value,message):
          if s:
              s.close()
          print "Could not open socket: " + message
          sys.exit(1)

    # Send connection Request asking for data to be sent to an UE
    server = (host, control_port)
    list1=["ConnectionRequest", '130.233.158.165']
    print "Requesting for connection from Cognitive Radio Network"
    s.sendto(repr(list1), server)
    
    while 1:
        try:
                # Recv data function
                recv_data, addr = s.recvfrom(1024)
                list1=eval(recv_data)
                # Control Plane
                recv_data=list1[0]
                print "Received", recv_data, "from", addr                
                
                #Data Plane
                data=list1[1]            
                
                # Check for the received data
                if (recv_data=="Ack"):
                    
                    #URL of the video to be downloaded
                    print "Enter URL"
                    URL = raw_input()
                    
                    # IP adress of the system where data has to be transferred to
                    Ip_adress= '130.233.158.165' 
                    data=(URL, Ip_adress)
                    list1=["ConnectionEstablishmentInformation", data]
                    s.sendto(repr(list1), addr)
                
                elif (recv_data=="AvailableConnectionPlans"):
                    print "This is the List of Connection Plans received from Cognitive Radio Network:"
                    print data
                    #data will now have the Connection plans
                    choice=[]
                    #Choose the best plan possible
                    # Currently there is no algorithm for choosing the plan, so the first plan is always selected
                    choice=data[0]
                    list1=["ConnectionChoice", choice]
                    s.sendto(repr(list1), addr)
                
                elif(recv_data=="ConnectionChoiceAck"):
                    pass
                
                elif (recv_data=="TransferProvided"):
                    list1=["TransferAck", 0]
                    s.sendto(repr(list1), addr)
                    sys.exit(0)

        except KeyboardInterrupt:
            s.close()
            sys.exit(0)

if __name__=='__main__':
    main()
