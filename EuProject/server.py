#####################################################################################
# author: Anil Morab                                                                #
# email: anil.morab.vishwanath@aalto.fi                                             #
#####################################################################################
# The function 'server()' present in this is called from the local_rrm.py           #
# It is as a part of EUProject, It interacts with the client.py file inorder        #
# to download a given URL and send it to the external client                        #
# Currently requested URL is downloaded, broken into binary files & transmitted     #
# over sockets, Hence Maximum size of file should not exceed 1Mb at this point      # 
##################################################################################### 

#!/usr/bin/python

import socket, os, time, subprocess

# Function called from local_RRM to send a URL file to the specified IP address
def server(URL, ip_address):
	m = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	m.bind(('130.233.158.164', 6001))
	client=(ip_address, 6001)

	try:
		      data=URL
		      subprocess.call(["youtube-dl", data])
		      command='youtube-dl --get-filename '+'"'+data+'"'
		      res=os.system(command)
		      if res==0:
		            #Get file name here
		            fin, fout = os.popen4(command)              
		            filename=fout.read()
		            
		            #Open file and start transmitting
		            filename=filename.replace("\n", "")
		            m.sendto(filename, client)
		            vid = open (filename, 'r')
		            while True:
		                chunk = vid.readline(1024)
		                if not chunk: 
		                    m.sendto("done", client)
		                    break  # EOF
		                m.sendto(chunk, client)
		            vid.close()
		            
		            #Logic to check if the entire data has been transmitted
		            # Receives MD5 from the client and checks it with the original to see it if matches or not
		            try:
		            	result1, addr = m.recvfrom(1024)
		            	result1=str(result1)
		            	command='md5sum /home/comlab/Desktop/EuProject/'+str(filename)
		            	os.system(command)
		            	fin, fout = os.popen4(command)
		            	result2=fout.read()
		            	result2=result2.replace("\n", "")
		            	result2=result2.split()
		            	result2=result2[0]
		            	result2=str(result2)
		            	if (result1==result2):
		            		print "Data sent successfully"            
		            	else:
		            		print "Partial data transferred"
		            except:
		            	pass
		            m.close()
		            return 0
	except:
		  return 1
