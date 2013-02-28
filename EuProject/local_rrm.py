################################################################################
# author: Anil Morab                                                           #
# email: anil.morab.vishwanath@aalto.fi                                        #
################################################################################
# This is the heart of Cognitive Radio network. It performs functions such as  #
# managing the UEs that connect to this, Interaction over the X2 interface,    #
# interacting with the network RRM to do functions such as downloading a file  #
# and transferring to the specified IP address (EUProject) etc.                #
################################################################################
#!/usr/bin/env python

import socket, threading, select
import sys, os, time, subprocess
import MySQLdb as mdb
import server


# Port number for UE interface 
phy_port = 6000

# Port number for NW RRM
NR_port = 7000

# Port number for X2 interface 
X2_port = 6500

# Parameters that we are able to handle with the USRP boxes
Datarate= [2000000, 2000000]
TxPower=[20, 30, 40, 50]
Modulation = ['2-QAM', '4-QAM', '16-QAM', '64-QAM']
TDD_config = [0, 1, 2, 3]
ResourceBlock=["000011", "110000", "001100"] # Currently each frequency is divided into 3 resource blocks
control_freq =['set_freq', 'fb_freq']

#Global variables
count = 0
i = 0
deleted_Freq = 0
client_list={}
addr_list={}

#Database function: Important for managing the UEs connected
# This function gets the data from the database and updates the data according to many algorithms that are to be implemented 
def database_freq(str1, control):
            global count
            global i
            global deleted_Freq
            global last_old_freq
            
            i=(count%3)
            # Check if the request is ask_freq
            if (str1==control_freq[0]):
                con = None
                try:
                # Connect to the database which is on a local machine using the given credentials
                    con = mdb.connect('localhost', 'testuser', 'comlab', 'My_Freqs');        
                    cur = con.cursor()
                    cur.execute("SELECT * FROM Frequency")
                    
                # Get the first frequency from the database
                    row = cur.fetchone()
                    centre_freq=row[0]             
                    
                    # One frequency can be used by 3 clients
                    if (control==0):
                            sql = "UPDATE Frequency SET busy=%d WHERE frequency=%d"%(i, centre_freq)
                        
                    # If client terminates add the frequency back
                    elif (control==1):
                            
                            try:
                                    sql1 = "INSERT INTO Frequency (frequency, busy ) VALUES (%s, %d)"%(deleted_Freq, 3)                                    
                                    cur.execute(sql1)                                   
                            except:
                                    pass
                            sql="UPDATE Frequency SET busy=busy-1 WHERE frequency=%d"%deleted_Freq                   
                    
                    try:
                        cur.execute(sql)
                        con.commit()
                    except:
                        con.rollback()
                                            
                    if(i==0 and count!=0):
                            sql = "DELETE from Frequency LIMIT 1"            
                            try:
                                cur.execute(sql)
                                con.commit()
                            except:
                                con.rollback() 
        
                except mdb.Error, e: 
                    print "Error %d: %s" % (e.args[0],e.args[1])
                    sys.exit(2)
                # Close the connection with the database
                finally:    
                    if con:    
                        con.close()
            # Return the required centre_freq to the caller    
            return centre_freq            

# Defining a class for Managing the UEs connected to this NE
class phy_client():
    
    #Class variables
    addr=0
    centre_freq=0
    datarate=0
    txpw=0
    modulation=0
    tdd=0
    rb=0
    
    def __init__(self):
        pass
    
    # Function that sets the initial parameters for transmission    
    def initial_parameter(self):
        # Set all the parameters for the client                            
                    
        #1. Frequency: Get frequency from the database
        self.centre_freq = database_freq(control_freq[0], 0)
                            
        #2. Modulation: Set the modulation based on some parameters 
        self.modulation= Modulation[0]
                            
        #3. Data rate
        self.datarate= Datarate[0]
                            
        #4. Transmit Power: Set based on X2
        self.txpw = TxPower[0]
                            
        #5. Resource blocks: Set an Ascii value now
        global i
        self.rb = ResourceBlock[i]
                            
        #6. TDD frame configuration
        self.tdd = TDD_config[0]
                            
        #Make a list1 of all these parameters
        list1=[self.centre_freq, self.modulation, self.datarate, self.txpw, self.rb, self.tdd]
        return list1
    
    # Function that sets the parameters based on received feedback
    def feedback_parameter(self):
        # Now process the feedback and decide what all parameters need to be changed
        # Set flags to 1 based on feedback received 
        # Have to implement different algorithms that decides whether or not parameters have to be changed
            
        # Assuming that this feedback changes all the parameters

            new_req_freq =1
            new_req_mod =1
            new_req_rate =1
            new_req_txpower =1
            new_req_rb =1
            new_config=1
            
            global ResourceBlock
            #Check for frequency
            if (new_req_freq == 1):     
                new_req_freq=0
            
            #Check for Modulation
            if (new_req_mod== 1):     
                self.modulation = Modulation[1]
                new_req_mod =0
            
             #Check for Datarate
            if (new_req_rate ==1):     
                self.datarate= Datarate[1]
                new_req_rate =0
            
             #Check for TxPower
            if (new_req_txpower==1):     
                self.txpw= TxPower[1]
                new_req_txpower =0
            
             #Check for ResourceBlock
            if (new_req_rb==1):      
                new_req_rb =0
            
            # Check for Fram configuration
            if (new_config==1):     
                self.tdd = TDD_config[1]
                new_config =0       
            
            #Make a list1 of all these parameters
            list2=[self.centre_freq, self.modulation, self.datarate, self.txpw, self.rb, self.tdd]
            return list2
            
    # Function that updates the database if UE terminates
    def delete(self):
        global deleted_Freq
        global count
        count=count-1
        deleted_Freq=self.centre_freq
        database_freq(control_freq[0], 1)

# Main function starts here
def main():            
    global count
    global client_list
    
    #Socket s for UE interface
    try:
          s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
          s.bind(('',6000))
    except socket.error, (value,message):
          if s:
              s.close()
          print "Could not open socket: " + message
          sys.exit(1)

    #socket l for X2 interface
    try:
          l = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
          l.bind(('',6500))
    except socket.error, (value,message):
          if l:
              l.close()
          print "Could not open socket: " + message
          sys.exit(1)    
    
    #socket k for NW RRM interface
    try:
          k = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
          k.bind(('',7000))
    except socket.error, (value,message):
          if k:
              k.close()
          print "Could not open socket: " + message
          sys.exit(1)
    
    # Toggle between these sockets  
    inputs=[s,k,l]
    try:
        while 1:                
            print "Waiting for requests from UEs"
            # Switch sockets based on data received 
            readable, writable, exceptional = select.select(inputs, [], [])
            for sock in readable:
                    recv_data, addr= sock.recvfrom(1024)      
                    try:
                        list1=eval(recv_data)
                        # Control Plane
                        recv_data=list1[0]
                        print "Received", recv_data, "from", addr
                        address=sock.getsockname()
 
                        #Data Plane
                        data=list1[1]  
                    except:
                        pass

                    # If connection from UE Interface                                         
                    if address[1]==6000:
                          
                          # Check the contents of received data
                          if recv_data== ("new_client"):           
                                  # Create an object here
                                  count=count+1
                                  client_list[count]=phy_client()                   
                                  addr_list[addr]=count                                 
                                  value =client_list.get(count)
                                  value.addr=addr
                                  
                                  #Send ACK
                                  my_list=["got_req", 0]
                                  sock.sendto(repr(my_list), value.addr)
                                      
                                  # Call initial paremeter list method
                                  list1= value.initial_parameter()  
                                          
                                  #Send the parameters back to Client
                                  my_list=["para_list", list1]
                                  sock.sendto(repr(my_list), value.addr)
                                  s.setblocking(0)
                                              
                          
                          elif (recv_data =="feedback"):
                                  s.setblocking(1)
                                  #Set to 1 if you want feedback
                                  feed=1
                                  if (feed==1):                        
                                      # Call the feedback function
                                      temp=addr_list.get(addr)
                                      value=client_list.get(temp)
                                      list2= value.feedback_parameter()
                                      #Send the parameters back to Client
                                      my_list=["new_para_list", list2]
                                      sock.sendto(repr(my_list), value.addr)
                                  else:
                                      pass
                                  s.setblocking(0)            
                          
                          elif (recv_data =="terminated_client"):
                                  temp=addr_list.get(addr)
                                  value=client_list.get(temp)
                                  value.delete()
                    
                    # If connection from X2 interface           
                    # Currently the interface is ready but no negotiations are being done
                    # Different algorithms to be implemented
                    elif address[1]==6500:
                        l.setblocking(1)
                        print "Message from X2 interface"
                        l.setblocking(0)
                                            
                    # If connection from Network RRM
                    elif address[1]==7000:                                                
                        print "Request for connection from Network RRM"
                        network_addr=addr
                        #Make this a blocking socket, so that data from Phy layer will be stopped until this is processed
                        k.setblocking(1)              
                        # Check for the received data
                        if (recv_data=="Check_availability"):
                            
                            #data will have UE IP address
                            print "Checking for this IP address: %s"%data
                            
                            # Check if the data is present in the client_list
                            # Inverse the list, Now It contains the IP address of all the UEs that have connected to our system 
                            inverse_address={v:k for k,v in addr_list.items()}
                            # Check if present
                            IPs= [inverse_address[x][0] for x in range(1, len(inverse_address)+1)]
                            
                            if (data in IPs):
                                # Send Ack to NW RRM if data is present
                                print "IP adress %s present"%data
                                list2=["Ack", 1]
                                sock.sendto(repr(list2), addr)
                            else:
                                # Send NACK
                                list2=["NAck", 0]
                                sock.sendto(repr(list2), addr)   
                                        
                        elif (recv_data== "Measurement_Report"):
                            #TODO: Get measurement report from the database
                            # Since No feedback is received from phy layer yet, 0 is being sent
                            # Forward the same to the Network RRM
                            print "Sending feedback to Network RRM"
                            list2=["feedback", 0]
                            sock.sendto(repr(list2), addr)
                            
                        elif (recv_data== "ConnectionEstablishmentInformation"):
                            #data will have URL and IP adress
                            URL=data[0]
                            ip_address=data[1]
                            
                            print "Transferring %s data to %s"%(URL, ip_address)
                            
                            #Download the data and Send the data to the ip address specified                
                            
                            my_list=["Download_file", 0]
                            sock.sendto(repr(my_list), value.addr)
                            ack, addr=sock.recvfrom(1024)
                            if (ack=="Download_file_ack"):
                                k.setblocking(0)
                                # Call the interface function to download the file and send it to the specified IP address
                                ret=server.server(URL, ip_address)
                                k.setblocking(1)
                                if ret==0:
                                      print "Done transferring data"
                                list2=["TransferProvided", 0]
                                sock.sendto(repr(list2), network_addr) 
                      
                        elif (recv_data =="TransferAck"):
                           print "Releasing resources"           
                        
                        # Make this a non blocking socket again
                        k.setblocking(0)
                              
    except KeyboardInterrupt:
        s.close()
        k.close()
        l.close()
        sys.exit(0)

if __name__ == "__main__":
    main()          
