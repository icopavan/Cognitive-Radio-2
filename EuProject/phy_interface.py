#####################################################################################
# author: Anil Morab                                                                #
# email: anil.morab.vishwanath@aalto.fi                                             #
#####################################################################################
# This program acts as an interface between the USP boxes and the local_rrm function#
# It receives commands and Data from the local RRM and Manages the USRPs accordingly#
#                                                                                   #
#####################################################################################

#!/usr/bin/env python

"""
Physical layer Client
"""

import socket, threading
import sys, os, time
import client

#Initializations
host = '130.233.158.164' # Should always know the IP address of the local_RRM
port = 6000
threadBreak = False

#Transmitter thread
def Transmitter():
    while not threadBreak: ## it will run this as long as threadBreak is false
        # Start transmitting in the first frequency
        print "Sending parameters to the physical layer"
        # If you want to use the USRP boxes, then uncomment the below line
        # The executable from the C++ program should be named as x for it to work
        #os.system("./x ")        
        return 0

def main():
    # local RRM socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    except socket.error, (value,message):
        if s:
            s.close()
            print "Could not open socket: " + message
            sys.exit(1)
    
    # Prepare the server
    server = (host, port)
    
    # Send request for center frequency
    print "Sending request for connection to the eNodeB"
    lis=["new_client", 0]
    s.sendto(repr(lis), server)
    
    try:       
        while 1:
              #Receive parameters from the server
              data2, addr = s.recvfrom(1024)   
              recv_data=eval(data2)
              data=recv_data[0]
              print "Received", data, "from", addr
              list1=recv_data[1]
              
              # Check for the received parameters
              if data=="got_req":
                  pass
              
              elif data=="para_list":
                    print "The received data is:", list1
              
                    # Start the thread for transmission
                    threading.Thread(target = Transmitter).start()
                                              
                    #TODO: Function to get feedback from the physical layer after every 20 seconds.
                    
                    # Transmit for 20 seconds using the initial parameters
                    #time.sleep(20)
                    
                    #TODO: Send the feedback to the server for processing
                    #lis=["feedback", 0]
                    #s.sendto(repr(lis), server)
                       
                    # Prepare socket and send new parameters to the physical layer
                    new_s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                  
              elif data=="new_para_list":      
                        list2=list1
                        print "Received from server, new parameters:", list2
                        new_freq= str (list2[0])
                        new_freq = new_freq + "000000"
                        freq=int(new_freq)                        
                        new_rate= list2[2]
                        new_gain=list2[3]
                        new_srb= list2[4]
                        #Write a function to check what changes have been made
                                                
                        #Send new parameters to the physical layer
                        new_s.sendto(("CMD SETFREQ %s")% freq, ('192.168.10.1', 5700))
                        time.sleep(1)
                        new_s.sendto(("CMD SETSRB %s")% new_srb, ('192.168.10.1', 5700))
                        time.sleep(1)
                        new_s.sendto(("CMD SETRATE %s")% new_rate, ('192.168.10.1', 5700))
                        time.sleep(1)
                        new_s.sendto(("CMD SETPWR %s")% new_gain, ('192.168.10.1', 5700))
                        time.sleep(1)
                                                          
              # For EUProject
              elif data=="Download_file":
              	# Send an acknowledgement, else send recv will not coordinate and results in overflows  
                s.sendto("Download_file_ack", addr)
              	s.setblocking(0)
              	ret=client.client()
              	if ret==0:
              		print "Received new file"
              	s.setblocking(1)
                        #Feedback is sent to the server after every 20 seconds
              time.sleep(20)
              #TODO: Send the feedback to the server for processing
              lis=["feedback", 0]
              s.sendto(repr(lis), server)                        
    
    except KeyboardInterrupt:
        print "Received signal"
        lis=["terminated_client", 0]
        bytes= s.sendto(repr(lis), server)
        s.close()
        sys.exit(0)

if __name__ == "__main__":
    main()
