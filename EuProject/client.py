##############################################################################
# author: Anil Morab                                                         #
# email: anil.morab.vishwanath@aalto.fi                                      #
##############################################################################
# The function 'client()' present in this is called from the phy_interace.py #
# It is as a part of EUProject, It interacts with the server.py file inorder #
# to download a given URL and place it on the current directory              #
############################################################################## 

#!/usr/bin/python

import socket,os

def client():
	# Try making a new socket
	m= socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	try:
		m.bind(('130.233.158.165', 6001))
	except:
		print "Bind failed"

	try:
		      fname, addr = m.recvfrom(1024)
		      try:
		          print "Opening a new file %s"%fname
		          fp = open(fname,'w') 
		          
		          while True:
		              strng = m.recvfrom(1024)
		              if (strng[0]== "done"):
		                  break
		              else:
		                  fp.write(strng[0])
		          fp.close()
		      except:
		          pass
		      
		      # Logic to check if the entire data is received
		      # MD5 is calculated on the file and sent to the server to check if complete data has been received
		      try:
		          # Change the path of the directory according to where the files have been placed
		          command='md5sum /home/comlab/Desktop/'+ str(fname)
		          os.system(command)
		          fin, fout = os.popen4(command)
		          result=fout.read()
		          result=result.replace("\n", "")
		          result=result.split()
		          m.sendto(result[0], addr)
		      except:
		          pass        
		      m.close()
		      return 0
	except:
		  pass

if __name__=='__main__':
    client()
