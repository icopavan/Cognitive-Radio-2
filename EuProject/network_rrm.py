##################################################################################
# author: Anil Morab                                                             #
# email: anil.morab.vishwanath@aalto.fi                                          #
##################################################################################
# This acts as an interface to the outer world those who wish to use the CRN     #
# This also gets the frequencies from the FairSpectrum database (using XML, HTTP)#
# It prepares the database so that the local RRMs can read from it and manage    #
# resources between themselves                                                   #
##################################################################################

#!/usr/bin/python
import httplib
from xml.dom.minidom import parseString
import MySQLdb as mdb
import sys, threading
import EuProject

#Request to the Fairspectrum database
def spectrum_manager():
    conn = httplib.HTTPConnection(host='www.radiomikrofonit.fi',timeout=30)  
    # This is URL from which we access the data from the Fairspectrum Database
    req = '/FSService.svc/GetChannelsByCountry/ProVer/4/Country/FI/FCCID/37/SerNum/1/SeqNum/1/Latitude/60.59/Longitude/22.54/DevTyp/3'  
    try:
        conn.request('GET',req)
    except:
        print 'connection failure'  

    data = conn.getresponse().read()  
    
    #parse the xml you downloaded
    dom = parseString(data)

    #retrieve the first xml tag (<tag>data</tag>) that the parser finds with name tagName:
    xmlTag = dom.getElementsByTagName('TvCh')[0].toxml()
    
    xmlData=xmlTag.replace("<TvCh>", "")
    xmlData=xmlData.replace("</TvCh>", "")
    return xmlData

# Prepares database for local RRMs to manage resources from
# Currently we store the Frequency and Number of Resource blocks that are busy
def write_database(a):
        con = mdb.connect('localhost', 'testuser', 'comlab', 'My_Freqs');
        with con:
                cur = con.cursor()
                cur.execute("drop table Frequency")
                cur.execute("create table Frequency ( frequency int, busy int )")
                cur.execute("CREATE UNIQUE INDEX number ON Frequency (frequency)")

                # Set to 1 if values have to be written locally        
                local_value = 0        
                if (local_value==0):
                        # This will write values from fairspectrum database
                        for i in range(0, len(a)):
                                cur.execute("INSERT INTO Frequency (frequency, busy ) VALUES (%d, 0)"%a[i])
                else:
                        # This will write local values
                        for i in range(0, 30):
                                cur.execute("INSERT INTO Frequency (frequency, busy ) VALUES (2450, 0)")
                                cur.execute("INSERT INTO Frequency (frequency, busy ) VALUES (2455, 0)")
                                cur.execute("INSERT INTO Frequency (frequency, busy ) VALUES (2460, 0)")

# Function to prepare the list
def make_list(my_string):
    s=""
    a=[]
    for i in range (0, len(my_string)):
            if (my_string[i] == ','):
                    a.append(int(s))
                    s=""
                    i=i+1
            else:
                    s+= str(my_string[i])

    return a

#Main function starts here
def main():
    xmlData= spectrum_manager()
    xmlData+=str(",")
    a= make_list(xmlData)
    write_database(a)
    print "Inserted Frequencies from FairSpectrum Database"
            
if __name__=='__main__':
    main()
    # To interact with the outer world, in this case EuProject
    EuProject.EuProject()
