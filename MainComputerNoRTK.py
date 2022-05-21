from array import array
from syslog import LOG_NDELAY
import numpy as np
import math
#from gps import *
import time
from distutils.log import error
from gps3 import gps3
from geographiclib.geodesic import Geodesic
import serial
running = True
global lon1,lat1,lonErr,latErr,lon2,lat2,lonErr2,latErr2

latTarg=21.75564 #target lat loc
longTarg=39.14764 #target long loc
#--------
lat1=21.75570317
lon1=39.14778467

lat2=21.75570317
lon2=39.14778667
#-------


# tl=("["+str(latTarg)+", "+str(longTarg)+"]")

#ttyACM1
# ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
ser.reset_input_buffer()

thisdict =	{
  "Key": 1000

}

def getEndpoint(lat,lon,bearing,d):
    R = 6371                     #Radius of the Earth
    brng = math.radians(bearing) #convert degrees to radians
    d = d/100000                  #convert cm to km
    lat = math.radians(lat)    #Current lat point converted to radians
    lon = math.radians(lon)    #Current long point converted to radians
    lat22 = math.asin( math.sin(lat)*math.cos(d/R) + math.cos(lat)*math.sin(d/R)*math.cos(brng))
    lon22 = lon + math.atan2(math.sin(brng)*math.sin(d/R)*math.cos(lat),math.cos(d/R)-math.sin(lat)*math.sin(lat))
    lat22 = math.degrees(lat22)
    lon22 = math.degrees(lon22)
    return round(lat22,7),round(lon22,7)

def search(array2,v): #searcg(array[], Str V) ex: search(array9 ,"[21.7556473, 39.1477785]") ,Str v in this format "[21.7556473, 39.1477785]"
   row=-1
   col=-1
   for i in array2:
     row=row+1
     numcols = len(array2[0])
     for j in i:
        col=col+1
        #print(j)  
        x=j
        ymov=col%numcols
        xmov=row   
        #print(row,col%numcols)
        #print("For point: "+ v)
        c="X"+str(xmov*10),"Y"+str(ymov*10) #mult by 5 since each square is 5cm apart 75cm/5cm = 15 col for x axis mov 65/5=13 rows for y-axis mov 
        thisdict[c] = math.dist(x,v)
        #return thisdict

def findRange(array):
    midpoint=array[7][7]
    latM=midpoint[0]
    lonM=midpoint[1]
    #for 50cm from mid point 
    print("Range From :" + str(round((latM - 00.0000050),7))+"," + str(round((lonM - 00.0000050),7)) +" to " + str(round((latM + 00.0000050),7))+"," +str(round((lonM + 00.0000050),7)))

def filterString(navC):
    navC=str(navC)
    navC=navC.replace("'",'')
    navC=navC.replace("[",'')
    navC=navC.replace("]",'')
    navC=navC.replace(" ",'')
    navC=navC.replace("",'')
    return navC


def sendNav2Ard(navC):
    ab=navC.encode('utf-8')
    ser.write(b" %s\n"%ab) 
    line = ser.readline().decode('utf-8').rstrip()
    print(line)
    time.sleep(1)

def readingArd():
    #ser.write(b"\n") 
    line = ser.readline().decode('utf-8').rstrip()
    print(line)
    time.sleep(1)

def readingArd2():
    #ser.write(b"\n") 
    line = ser.readline().decode('utf-8').rstrip()
    time.sleep(1)
    return line


def getPositionData():
    gps_socket = gps3.GPSDSocket()
    data_stream = gps3.DataStream()
    gps_socket.connect()
    gps_socket.watch()
    for new_data in gps_socket:
        if new_data:
            data_stream.unpack(new_data)
            print('Longitude = ', data_stream.TPV['lon'])
            print('Latitude = ', data_stream.TPV['lat'])
            print('lonErr = ', data_stream.TPV['epx'])
            print('latErr = ', data_stream.TPV['epy'])
            #global lon1,lat1,lonErr,latErr
            lon1=data_stream.TPV['lon']
            lonErr=data_stream.TPV['epx']
            lat1=data_stream.TPV['lat']
            latErr=data_stream.TPV['epy']

            
            if( (type(lonErr) is float) & (type(latErr) is float) ):
                #if(lonErr<0.05 & latErr <0.05): #if err is lesss than 5cm
                if((lonErr<9) & (latErr <11)):
                    break
        
def getPositionData2():
    gps_socket = gps3.GPSDSocket()
    data_stream = gps3.DataStream()
    gps_socket.connect()
    gps_socket.watch()
    for new_data in gps_socket:
        if new_data:
            data_stream.unpack(new_data)
            print('Longitude Point2 = ', data_stream.TPV['lon'])
            print('Latitude Point2 = ', data_stream.TPV['lat'])
            print('lonErr Point2 = ', data_stream.TPV['epx'])
            print('latErr Point2 = ', data_stream.TPV['epy'])
            #global lon2,lat2,lonErr2,latErr2
            lon2=data_stream.TPV['lon']
            lonErr2=data_stream.TPV['epx']
            lat2=data_stream.TPV['lat']
            latErr2=data_stream.TPV['epy']

            
            if( (type(lonErr2) is float) & (type(latErr2) is float) ):
                #if(lonErr<0.05 & latErr <0.05): #if err is lesss than 5cm
                if((lonErr2<9) & (latErr2 <11)):
                    break

def getOrientation(lat1,lon1,lat2,lon2):
    global bearing # breaing from point 1 to 2 and Obearing is the below points 
    bearing= Geodesic.WGS84.Inverse(lat1,lon1,lat2,lon2)['azi1']
    if(bearing<0):
        bearing=bearing+360
    if( (bearing+90.0) >=360.0 ): 
        Obear=(bearing+90.0)%360.0 #%360 to ensure that even if you rotate the grid it will give the right orientation
    else:
        Obear=bearing+90.0 # if point 1 to point 2 is left to right add 90 else sub 90 
    print("bearing in degrees =" + str(round(bearing,1)))
    return Obear

def setBear(b):
    if(b>=360.0):
        b=b%360.0
    else:
        b=b
    return b 
    
def checkSig():
    while(1):
        singal=readingArd2()
        time.sleep(1)
        if(singal=='D'):
            #getPositionData2()
            print ("Second Point: lat = " + str(lat2) + ", long = " + str(lon2))
            break


print ("Application started!")
while running:
    #getPositionData()

    print ("First Point: lat = " + str(lat1) + ", long = " + str(lon1))
    #--Send G to arduino to go to next point------
    time.sleep(1)
    sendNav2Ard("G")
    time.sleep(1)
    # while(1):
    #     readingArd()
    #     time.sleep(1)
    #--check if Arduino reached the destiantion point and sent a signal "D"
    checkSig()
    #----Find Orientation using the two points ---
    Obear=getOrientation(lat1,lon1,lat2,lon2)
    #-------------Generating Array----------------
    
    #in this case we're doing 15 rows by 13 col
    #first 15 loc (aka "first row") , the reason it starts from loc2 is becuase first loc1 is our (refrence point coming from the rtk aka "home")

    f=0 #first or intial number
    i=5 #increment
    Right=90 # "90 bearing" moving "East" if we're going from "left" to "right" since it is a row , so its (starting from down right corener) of the "rectangle" aka "working space" 
    Left=270 # "270 bearing" moving "West" if we're going from "right" to "left" since it is a row , so its (starting from down left corener) of the "rectangle" aka "working space" 
    b=bearing
    #b=setBear(b)
    f=f+i
    loc2=getEndpoint(lat1,lon1,b,f) 
    f=f+i

    loc3=getEndpoint(lat1,lon1,b,f) 
    f=f+i

    loc4=getEndpoint(lat1,lon1,b,f)
    f=f+i

    loc5=getEndpoint(lat1,lon1,b,f)
    f=f+i

    loc6=getEndpoint(lat1,lon1,b,f)
    f=f+i

    loc7=getEndpoint(lat1,lon1,b,f)
    f=f+i

    loc8=getEndpoint(lat1,lon1,b,f)
    f=f+i

    loc9=getEndpoint(lat1,lon1,b,f)
    f=f+i

    loc10=getEndpoint(lat1,lon1,b,f)
    f=f+i

    loc11=getEndpoint(lat1,lon1,b,f)
    f=f+i

    loc12=getEndpoint(lat1,lon1,b,f)
    f=f+i

    loc13=getEndpoint(lat1,lon1,b,f)
    f=f+i

    loc14=getEndpoint(lat1,lon1,b,f)
    f=f+i

    loc15=getEndpoint(lat1,lon1,b,f)
    # first col , 9 loc "refrenc point is loc1 which is lat1 lon1"
    f=0 # to set f var back to 0 so that it starts from 5cm
    up=0 # if u want to move up brng=0 aka moving "North"
    down=180 # move down brng=180 aka moving "south"
    bb=Obear # bearing from inital point of the first row
    #bb=setBear(bb)
    #13 rows only ; so 13 elemnts for each col , in another way u can say 15  elemnts for each row
    f=f+i

    loc1_2=getEndpoint(lat1,lon1,bb,f)
    f=f+i

    loc1_3=getEndpoint(lat1,lon1,bb,f)
    f=f+i

    loc1_4=getEndpoint(lat1,lon1,bb,f)
    f=f+i

    loc1_5=getEndpoint(lat1,lon1,bb,f)
    f=f+i

    loc1_6=getEndpoint(lat1,lon1,bb,f)
    f=f+i

    loc1_7=getEndpoint(lat1,lon1,bb,f)
    f=f+i

    loc1_8=getEndpoint(lat1,lon1,bb,f)
    f=f+i

    loc1_9=getEndpoint(lat1,lon1,bb,f)
    f=f+i

    loc1_10=getEndpoint(lat1,lon1,bb,f)
    f=f+i

    loc1_11=getEndpoint(lat1,lon1,bb,f)
    f=f+i

    loc1_12=getEndpoint(lat1,lon1,bb,f)
    f=f+i

    loc1_13=getEndpoint(lat1,lon1,bb,f)


    #Second col except first elemnt one form the col bc it done before ^(in the 9 loc or first row) "so loc#col_#row"
    f=0
    f=f+i
    loc2_2=getEndpoint(loc2[0],loc2[1],bb,f)
    f=f+i

    loc2_3=getEndpoint(loc2[0],loc2[1],bb,f)
    f=f+i

    loc2_4=getEndpoint(loc2[0],loc2[1],bb,f)
    f=f+i

    loc2_5=getEndpoint(loc2[0],loc2[1],bb,f)
    f=f+i

    loc2_6=getEndpoint(loc2[0],loc2[1],bb,f)
    f=f+i

    loc2_7=getEndpoint(loc2[0],loc2[1],bb,f)
    f=f+i

    loc2_8=getEndpoint(loc2[0],loc2[1],bb,f)
    f=f+i

    loc2_9=getEndpoint(loc2[0],loc2[1],bb,f)
    f=f+i

    loc2_10=getEndpoint(loc2[0],loc2[1],bb,f)
    f=f+i

    loc2_11=getEndpoint(loc2[0],loc2[1],bb,f)
    f=f+i

    loc2_12=getEndpoint(loc2[0],loc2[1],bb,f)
    f=f+i

    loc2_13=getEndpoint(loc2[0],loc2[1],bb,f)
    f=f+i


    #third col
    f=0
    f=f+i

    loc3_2=getEndpoint(loc3[0],loc3[1],bb,f)
    f=f+i

    loc3_3=getEndpoint(loc3[0],loc3[1],bb,f)
    f=f+i

    loc3_4=getEndpoint(loc3[0],loc3[1],bb,f)
    f=f+i

    loc3_5=getEndpoint(loc3[0],loc3[1],bb,f)
    f=f+i

    loc3_6=getEndpoint(loc3[0],loc3[1],bb,f)
    f=f+i

    loc3_7=getEndpoint(loc3[0],loc3[1],bb,f)
    f=f+i

    loc3_8=getEndpoint(loc3[0],loc3[1],bb,f)
    f=f+i

    loc3_9=getEndpoint(loc3[0],loc3[1],bb,f)
    f=f+i

    loc3_10=getEndpoint(loc3[0],loc3[1],bb,f)
    f=f+i

    loc3_11=getEndpoint(loc3[0],loc3[1],bb,f)
    f=f+i

    loc3_12=getEndpoint(loc3[0],loc3[1],bb,f)
    f=f+i

    loc3_13=getEndpoint(loc3[0],loc3[1],bb,f)


    #4th col
    f=0
    f=f+i
    loc4_2=getEndpoint(loc4[0],loc4[1],bb,f)
    f=f+i

    loc4_3=getEndpoint(loc4[0],loc4[1],bb,f)
    f=f+i

    loc4_4=getEndpoint(loc4[0],loc4[1],bb,f)
    f=f+i

    loc4_5=getEndpoint(loc4[0],loc4[1],bb,f)
    f=f+i

    loc4_6=getEndpoint(loc4[0],loc4[1],bb,f)
    f=f+i

    loc4_7=getEndpoint(loc4[0],loc4[1],bb,f)
    f=f+i

    loc4_8=getEndpoint(loc4[0],loc4[1],bb,f)
    f=f+i

    loc4_9=getEndpoint(loc4[0],loc4[1],bb,f)
    f=f+i

    loc4_10=getEndpoint(loc4[0],loc4[1],bb,f)
    f=f+i

    loc4_11=getEndpoint(loc4[0],loc4[1],bb,f)
    f=f+i

    loc4_12=getEndpoint(loc4[0],loc4[1],bb,f)
    f=f+i

    loc4_13=getEndpoint(loc4[0],loc4[1],bb,f)

    #5th col
    f=0
    f=f+i

    loc5_2=getEndpoint(loc5[0],loc5[1],bb,f)
    f=f+i

    loc5_3=getEndpoint(loc5[0],loc5[1],bb,f)
    f=f+i

    loc5_4=getEndpoint(loc5[0],loc5[1],bb,f)
    f=f+i

    loc5_5=getEndpoint(loc5[0],loc5[1],bb,f)
    f=f+i

    loc5_6=getEndpoint(loc5[0],loc5[1],bb,f)
    f=f+i

    loc5_7=getEndpoint(loc5[0],loc5[1],bb,f)
    f=f+i

    loc5_8=getEndpoint(loc5[0],loc5[1],bb,f)
    f=f+i

    loc5_9=getEndpoint(loc5[0],loc5[1],bb,f)
    f=f+i

    loc5_10=getEndpoint(loc5[0],loc5[1],bb,f)
    f=f+i

    loc5_11=getEndpoint(loc5[0],loc5[1],bb,f)
    f=f+i

    loc5_12=getEndpoint(loc5[0],loc5[1],bb,f)
    f=f+i

    loc5_13=getEndpoint(loc5[0],loc5[1],bb,f)
    #6th col
    f=0
    loc6_2=getEndpoint(loc6[0],loc6[1],bb,f)
    f=f+i

    loc6_3=getEndpoint(loc6[0],loc6[1],bb,f)
    f=f+i

    loc6_4=getEndpoint(loc6[0],loc6[1],bb,f)
    f=f+i
    loc6_5=getEndpoint(loc6[0],loc6[1],bb,f)
    f=f+i

    loc6_6=getEndpoint(loc6[0],loc6[1],bb,f)
    f=f+i

    loc6_7=getEndpoint(loc6[0],loc6[1],bb,f)
    f=f+i

    loc6_8=getEndpoint(loc6[0],loc6[1],bb,f)
    f=f+i

    loc6_9=getEndpoint(loc6[0],loc6[1],bb,f)
    f=f+i

    loc6_10=getEndpoint(loc6[0],loc6[1],bb,f)
    f=f+i

    loc6_11=getEndpoint(loc6[0],loc6[1],bb,f)
    f=f+i

    loc6_12=getEndpoint(loc6[0],loc6[1],bb,f)
    f=f+i

    loc6_13=getEndpoint(loc6[0],loc6[1],bb,f)

    #7th col
    f=0
    f=f+i

    loc7_2=getEndpoint(loc7[0],loc7[1],bb,f)
    f=f+i

    loc7_3=getEndpoint(loc7[0],loc7[1],bb,f)
    f=f+i

    loc7_4=getEndpoint(loc7[0],loc7[1],bb,f)
    f=f+i

    loc7_5=getEndpoint(loc7[0],loc7[1],bb,f)
    f=f+i

    loc7_6=getEndpoint(loc7[0],loc7[1],bb,f)
    f=f+i

    loc7_7=getEndpoint(loc7[0],loc7[1],bb,f)
    f=f+i

    loc7_8=getEndpoint(loc7[0],loc7[1],bb,f)
    f=f+i

    loc7_9=getEndpoint(loc7[0],loc7[1],bb,f)
    f=f+i

    loc7_10=getEndpoint(loc7[0],loc7[1],bb,f)
    f=f+i

    loc7_11=getEndpoint(loc7[0],loc7[1],bb,f)
    f=f+i

    loc7_12=getEndpoint(loc7[0],loc7[1],bb,f)
    f=f+i

    loc7_13=getEndpoint(loc7[0],loc7[1],bb,f)

    #8th col
    f=0
    f=f+i
    loc8_2=getEndpoint(loc8[0],loc8[1],bb,f)
    f=f+i

    loc8_3=getEndpoint(loc8[0],loc8[1],bb,f)
    f=f+i

    loc8_4=getEndpoint(loc8[0],loc8[1],bb,f)
    f=f+i

    loc8_5=getEndpoint(loc8[0],loc8[1],bb,f)
    f=f+i

    loc8_6=getEndpoint(loc8[0],loc8[1],bb,f)
    f=f+i

    loc8_7=getEndpoint(loc8[0],loc8[1],bb,f)
    f=f+i

    loc8_8=getEndpoint(loc8[0],loc8[1],bb,f)
    f=f+i

    loc8_9=getEndpoint(loc8[0],loc8[1],bb,f)
    f=f+i

    loc8_10=getEndpoint(loc8[0],loc8[1],bb,f)
    f=f+i

    loc8_11=getEndpoint(loc8[0],loc8[1],bb,f)
    f=f+i

    loc8_12=getEndpoint(loc8[0],loc8[1],bb,f)
    f=f+i

    loc8_13=getEndpoint(loc8[0],loc8[1],bb,f)

    #9th col
    f=0
    f=f+i

    loc9_2=getEndpoint(loc9[0],loc9[1],bb,f)
    f=f+i

    loc9_3=getEndpoint(loc9[0],loc9[1],bb,f)
    f=f+i

    loc9_4=getEndpoint(loc9[0],loc9[1],bb,f)
    f=f+i

    loc9_5=getEndpoint(loc9[0],loc9[1],bb,f)
    f=f+i

    loc9_6=getEndpoint(loc9[0],loc9[1],bb,f)
    f=f+i

    loc9_7=getEndpoint(loc9[0],loc9[1],bb,f)
    f=f+i

    loc9_8=getEndpoint(loc9[0],loc9[1],bb,f)
    f=f+i

    loc9_9=getEndpoint(loc9[0],loc9[1],bb,f)
    f=f+i

    loc9_10=getEndpoint(loc9[0],loc9[1],bb,f)
    f=f+i

    loc9_11=getEndpoint(loc9[0],loc9[1],bb,f)
    f=f+i

    loc9_12=getEndpoint(loc9[0],loc9[1],bb,f)
    f=f+i

    loc9_13=getEndpoint(loc9[0],loc9[1],bb,f)

    #10th col
    f=0
    f=f+i
    loc10_2=getEndpoint(loc10[0],loc10[1],bb,f)
    f=f+i

    loc10_3=getEndpoint(loc10[0],loc10[1],bb,f)
    f=f+i

    loc10_4=getEndpoint(loc10[0],loc10[1],bb,f)
    f=f+i

    loc10_5=getEndpoint(loc10[0],loc10[1],bb,f)
    f=f+i

    loc10_6=getEndpoint(loc10[0],loc10[1],bb,f)
    f=f+i

    loc10_7=getEndpoint(loc10[0],loc10[1],bb,f)
    f=f+i

    loc10_8=getEndpoint(loc10[0],loc10[1],bb,f)
    f=f+i

    loc10_9=getEndpoint(loc10[0],loc10[1],bb,f)
    f=f+i

    loc10_10=getEndpoint(loc10[0],loc10[1],bb,f)
    f=f+i

    loc10_11=getEndpoint(loc10[0],loc10[1],bb,f)
    f=f+i

    loc10_12=getEndpoint(loc10[0],loc10[1],bb,f)
    f=f+i

    loc10_13=getEndpoint(loc10[0],loc10[1],bb,f)

    #11th col
    f=0
    f=f+i

    loc11_2=getEndpoint(loc11[0],loc11[1],bb,f)
    f=f+i

    loc11_3=getEndpoint(loc11[0],loc11[1],bb,f)
    f=f+i

    loc11_4=getEndpoint(loc11[0],loc11[1],bb,f)
    f=f+i

    loc11_5=getEndpoint(loc11[0],loc11[1],bb,f)
    f=f+i

    loc11_6=getEndpoint(loc11[0],loc11[1],bb,f)
    f=f+i

    loc11_7=getEndpoint(loc11[0],loc11[1],bb,f)
    f=f+i

    loc11_8=getEndpoint(loc11[0],loc11[1],bb,f)
    f=f+i

    loc11_9=getEndpoint(loc11[0],loc11[1],bb,f)
    f=f+i

    loc11_10=getEndpoint(loc11[0],loc11[1],bb,f)
    f=f+i

    loc11_11=getEndpoint(loc11[0],loc11[1],bb,f)
    f=f+i

    loc11_12=getEndpoint(loc11[0],loc11[1],bb,f)
    f=f+i

    loc11_13=getEndpoint(loc11[0],loc11[1],bb,f)


    #12th col
    f=0
    loc12_2=getEndpoint(loc12[0],loc12[1],bb,f)
    f=f+i

    loc12_3=getEndpoint(loc12[0],loc12[1],bb,f)
    f=f+i

    loc12_4=getEndpoint(loc12[0],loc12[1],bb,f)
    f=f+i

    loc12_5=getEndpoint(loc12[0],loc12[1],bb,f)
    f=f+i

    loc12_6=getEndpoint(loc12[0],loc12[1],bb,f)
    f=f+i

    loc12_7=getEndpoint(loc12[0],loc12[1],bb,f)
    f=f+i

    loc12_8=getEndpoint(loc12[0],loc12[1],bb,f)
    f=f+i

    loc12_9=getEndpoint(loc12[0],loc12[1],bb,f)
    f=f+i

    loc12_10=getEndpoint(loc12[0],loc12[1],bb,f)
    f=f+i

    loc12_11=getEndpoint(loc12[0],loc12[1],bb,f)
    f=f+i

    loc12_12=getEndpoint(loc12[0],loc12[1],bb,f)
    f=f+i

    loc12_13=getEndpoint(loc12[0],loc12[1],bb,f)

    #13th col
    f=0
    loc13_2=getEndpoint(loc13[0],loc13[1],bb,f)
    f=f+i

    loc13_3=getEndpoint(loc13[0],loc13[1],bb,f)
    f=f+i

    loc13_4=getEndpoint(loc13[0],loc13[1],bb,f)
    f=f+i

    loc13_5=getEndpoint(loc13[0],loc13[1],bb,f)
    f=f+i

    loc13_6=getEndpoint(loc13[0],loc13[1],bb,f)
    f=f+i

    loc13_7=getEndpoint(loc13[0],loc13[1],bb,f)
    f=f+i

    loc13_8=getEndpoint(loc13[0],loc13[1],bb,f)
    f=f+i

    loc13_9=getEndpoint(loc13[0],loc13[1],bb,f)
    f=f+i

    loc13_10=getEndpoint(loc13[0],loc13[1],bb,f)
    f=f+i

    loc13_11=getEndpoint(loc13[0],loc13[1],bb,f)
    f=f+i

    loc13_12=getEndpoint(loc13[0],loc13[1],bb,f)
    f=f+i

    loc13_13=getEndpoint(loc13[0],loc13[1],bb,f)

    #14th col
    f=0
    loc14_2=getEndpoint(loc14[0],loc14[1],bb,f)
    f=f+i

    loc14_3=getEndpoint(loc14[0],loc14[1],bb,f)
    f=f+i

    loc14_4=getEndpoint(loc14[0],loc14[1],bb,f)
    f=f+i

    loc14_5=getEndpoint(loc14[0],loc14[1],bb,f)
    f=f+i

    loc14_6=getEndpoint(loc14[0],loc14[1],bb,f)
    f=f+i

    loc14_7=getEndpoint(loc14[0],loc14[1],bb,f)
    f=f+i

    loc14_8=getEndpoint(loc14[0],loc14[1],bb,f)
    f=f+i

    loc14_9=getEndpoint(loc14[0],loc14[1],bb,f)
    f=f+i

    loc14_10=getEndpoint(loc14[0],loc14[1],bb,f)
    f=f+i

    loc14_11=getEndpoint(loc14[0],loc14[1],bb,f)
    f=f+i

    loc14_12=getEndpoint(loc14[0],loc14[1],bb,f)
    f=f+i

    loc14_13=getEndpoint(loc14[0],loc14[1],bb,f)

    #15th col
    f=0
    loc15_2=getEndpoint(loc15[0],loc15[1],bb,f)
    f=f+i

    loc15_3=getEndpoint(loc15[0],loc15[1],bb,f)
    f=f+i

    loc15_4=getEndpoint(loc15[0],loc15[1],bb,f)
    f=f+i

    loc15_5=getEndpoint(loc15[0],loc15[1],bb,f)
    f=f+i

    loc15_6=getEndpoint(loc15[0],loc15[1],bb,f)
    f=f+i

    loc15_7=getEndpoint(loc15[0],loc15[1],bb,f)
    f=f+i

    loc15_8=getEndpoint(loc15[0],loc15[1],bb,f)
    f=f+i

    loc15_9=getEndpoint(loc15[0],loc15[1],bb,f)
    f=f+i

    loc15_10=getEndpoint(loc15[0],loc15[1],bb,f)
    f=f+i

    loc15_11=getEndpoint(loc15[0],loc15[1],bb,f)
    f=f+i

    loc15_12=getEndpoint(loc15[0],loc15[1],bb,f)
    f=f+i

    loc15_13=getEndpoint(loc15[0],loc15[1],bb,f)
    #----------------------------




    #21.7556509,39.14777467 inder lat1 lon1

    array9=[           [ [lat1,lon1],          [loc2[0],loc2[1]],    [loc3[0],loc3[1]],    [loc4[0],loc4[1]],     [loc5[0],loc5[1]],    [loc6[0],loc6[1]],    [loc7[0],loc7[1]],    [loc8[0],loc8[1]],    [loc9[0],loc9[1]],                        [loc10[0],loc10[1]],     [loc11[0],loc11[1]],   [loc12[0],loc12[1]],    [loc13[0],loc13[1]],    [loc14[0],loc14[1]],     [loc15[0],loc15[1]] ],
                    [ [loc1_2[0],loc1_2[1]],[loc2_2[0],loc2_2[1]],[loc3_2[0],loc3_2[1]],[loc4_2[0],loc4_2[1]], [loc5_2[0],loc5_2[1]],[loc6_2[0],loc6_2[1]],[loc7_2[0],loc7_2[1]],[loc8_2[0],loc8_2[1]],[loc9_2[0],loc9_2[1]],                    [loc10_2[0],loc10_2[1]],[loc11_2[0],loc11_2[1]],[loc12_2[0],loc12_2[1]],[loc13_2[0],loc13_2[1]],[loc14_2[0],loc14_2[1]],[loc15_2[0],loc15_2[1]] ],
                    [ [loc1_3[0],loc1_3[1]],[loc2_3[0],loc2_3[1]],[loc3_3[0],loc3_3[1]],[loc4_3[0],loc4_3[1]], [loc5_3[0],loc5_3[1]],[loc6_3[0],loc6_3[1]],[loc7_3[0],loc7_3[1]],[loc8_3[0],loc8_3[1]],[loc9_3[0],loc9_3[1]],                    [loc10_3[0],loc10_3[1]],[loc11_3[0],loc11_3[1]],[loc12_3[0],loc12_3[1]],[loc13_3[0],loc13_3[1]],[loc14_3[0],loc14_3[1]],[loc15_3[0],loc15_3[1]] ],
                    [ [loc1_4[0],loc1_4[1]],[loc2_4[0],loc2_4[1]],[loc3_4[0],loc3_4[1]],[loc4_4[0],loc4_4[1]], [loc5_4[0],loc5_4[1]],[loc6_4[0],loc6_4[1]],[loc7_4[0],loc7_4[1]],[loc8_4[0],loc8_4[1]],[loc9_4[0],loc9_4[1]],                    [loc10_4[0],loc10_4[1]],[loc11_4[0],loc11_4[1]],[loc12_4[0],loc12_4[1]],[loc13_4[0],loc13_4[1]],[loc14_4[0],loc14_4[1]],[loc15_4[0],loc15_4[1]] ],
                    [ [loc1_5[0],loc1_5[1]],[loc2_5[0],loc2_5[1]],[loc3_5[0],loc3_5[1]],[loc4_5[0],loc4_5[1]], [loc5_5[0],loc5_5[1]],[loc6_5[0],loc6_5[1]],[loc7_5[0],loc7_5[1]],[loc8_5[0],loc8_5[1]],[loc9_5[0],loc9_5[1]],                    [loc10_5[0],loc10_5[1]],[loc11_5[0],loc11_5[1]],[loc12_5[0],loc12_5[1]],[loc13_5[0],loc13_5[1]],[loc14_5[0],loc14_5[1]],[loc15_5[0],loc15_5[1]] ],
                    [ [loc1_6[0],loc1_6[1]],[loc2_6[0],loc2_6[1]],[loc3_6[0],loc3_6[1]],[loc4_6[0],loc4_6[1]], [loc5_6[0],loc5_6[1]],[loc6_6[0],loc6_6[1]],[loc7_6[0],loc7_6[1]],[loc8_6[0],loc8_6[1]],[loc9_6[0],loc9_6[1]],                    [loc10_6[0],loc10_6[1]],[loc11_6[0],loc11_6[1]],[loc12_6[0],loc12_6[1]],[loc13_6[0],loc13_6[1]],[loc14_6[0],loc14_6[1]],[loc15_6[0],loc15_6[1]] ],
                    [ [loc1_7[0],loc1_7[1]],[loc2_7[0],loc2_7[1]],[loc3_7[0],loc3_7[1]],[loc4_7[0],loc4_7[1]], [loc5_7[0],loc5_7[1]],[loc6_7[0],loc6_7[1]],[loc7_7[0],loc7_7[1]],[loc8_7[0],loc8_7[1]],[loc9_7[0],loc9_7[1]],                    [loc10_7[0],loc10_7[1]],[loc11_7[0],loc11_7[1]],[loc12_7[0],loc12_7[1]],[loc13_7[0],loc13_7[1]],[loc14_7[0],loc14_7[1]],[loc15_7[0],loc15_7[1]] ],
                    [ [loc1_8[0],loc1_8[1]],[loc2_8[0],loc2_8[1]],[loc3_8[0],loc3_8[1]],[loc4_8[0],loc4_8[1]], [loc5_8[0],loc5_8[1]],[loc6_8[0],loc6_8[1]],[loc7_8[0],loc7_8[1]],[loc8_8[0],loc8_8[1]],[loc9_8[0],loc9_8[1]],                    [loc10_8[0],loc10_8[1]],[loc11_8[0],loc11_8[1]],[loc12_8[0],loc12_8[1]],[loc13_8[0],loc13_8[1]],[loc14_8[0],loc14_8[1]],[loc15_8[0],loc15_8[1]] ],
                    [ [loc1_9[0],loc1_9[1]],[loc2_9[0],loc2_9[1]],[loc3_9[0],loc3_9[1]],[loc4_9[0],loc4_9[1]], [loc5_9[0],loc5_9[1]],[loc6_9[0],loc6_9[1]],[loc7_9[0],loc7_9[1]],[loc8_9[0],loc8_9[1]],[loc9_9[0],loc9_9[1]],                    [loc10_9[0],loc10_9[1]],[loc11_9[0],loc11_9[1]],[loc12_9[0],loc12_9[1]],[loc13_9[0],loc13_9[1]],[loc14_9[0],loc14_9[1]],[loc15_9[0],loc15_9[1]] ],
                    [ [loc1_10[0],loc1_10[1]],[loc2_10[0],loc2_10[1]],[loc3_10[0],loc3_10[1]],[loc4_10[0],loc4_10[1]],[loc5_10[0],loc5_10[1]],[loc6_10[0],loc6_10[1]],[loc7_10[0],loc7_10[1]],[loc8_10[0],loc8_10[1]],[loc9_10[0],loc9_10[1]], [loc10_10[0],loc10_10[1]],[loc11_10[0],loc11_10[1]],[loc12_10[0],loc12_10[1]],[loc13_10[0],loc13_10[1]],[loc14_10[0],loc14_10[1]],[loc15_10[0],loc15_10[1]]  ],
                    [ [loc1_11[0],loc1_11[1]],[loc2_11[0],loc2_11[1]],[loc3_11[0],loc3_11[1]],[loc4_11[0],loc4_11[1]],[loc5_11[0],loc5_11[1]],[loc6_11[0],loc6_11[1]],[loc7_11[0],loc7_11[1]],[loc8_11[0],loc8_11[1]],[loc9_11[0],loc9_11[1]], [loc10_11[0],loc10_11[1]],[loc11_11[0],loc11_11[1]],[loc12_11[0],loc12_11[1]],[loc13_11[0],loc13_11[1]],[loc14_11[0],loc14_11[1]],[loc15_11[0],loc15_11[1]] ],
                    [ [loc1_12[0],loc1_12[1]],[loc2_12[0],loc2_12[1]],[loc3_12[0],loc3_12[1]],[loc4_12[0],loc4_12[1]],[loc5_12[0],loc5_12[1]],[loc6_12[0],loc6_12[1]],[loc7_12[0],loc7_12[1]],[loc8_12[0],loc8_12[1]],[loc9_12[0],loc9_12[1]], [loc10_12[0],loc10_12[1]],[loc11_12[0],loc11_12[1]],[loc12_12[0],loc12_12[1]],[loc13_12[0],loc13_12[1]],[loc14_12[0],loc14_12[1]],[loc15_12[0],loc15_12[1]] ],
                    [ [loc1_13[0],loc1_13[1]],[loc2_13[0],loc2_13[1]],[loc3_13[0],loc3_13[1]],[loc4_13[0],loc4_13[1]],[loc5_13[0],loc5_13[1]],[loc6_13[0],loc6_13[1]],[loc7_13[0],loc7_13[1]],[loc8_13[0],loc8_13[1]],[loc9_13[0],loc9_13[1]], [loc10_13[0],loc10_13[1]],[loc11_13[0],loc11_13[1]],[loc12_13[0],loc12_13[1]],[loc13_13[0],loc13_13[1]],[loc14_13[0],loc14_13[1]],[loc15_13[0],loc15_13[1]] ],

                                                ]

        #--------------Done generating--------------
    #-------Take Inputs from user-----
    print("*********************")
    print("Warning coordinates must be within the >>")
    findRange(array9)
    print("example, in form of: "+ str(array9[10][8]))
    print("example, in form of: "+ str(array9[4][1]))
    print("________________________")
    InLat1 = input("Enter Lat1 of First coordinate:")
    InLon1 = input("Enter Lon1 First coordinate:")
    InLat2 = input("Enter Lat2 of Second coordinate:")
    InLon2 = input("Enter Lon2 Second coordinate:")
    #----Filteration----
    InLat1=filterString(InLat1)
    InLon1=filterString(InLon1)
    InLat2=filterString(InLat2)
    InLon2=filterString(InLon2)
    #---------
    tstloc2=[ [float(InLat1) ,float(InLon1)],  [float(InLat2),float(InLon2)] ,  array9[0][0]]
    #tstloc= [array9[10][8],array9[4][4],array9[0][0]] # or take input from user
    a_navC=[] #array of nav cmds
    #-------Search for the Taget Points--------
    for i in tstloc2:

        search(array9,i)
        NavC1=min(thisdict, key=thisdict.get)
        a_navC.append(str(NavC1))


    # print("--------------------")
    # a_navC=filterString(a_navC)
    # print(a_navC)
    # print("--------------------")
    
    #----Send Navigation To arduino -----
    a_navC=filterString(a_navC)
    time.sleep(1)
    time.sleep(1)
    sendNav2Ard(a_navC)
    time.sleep(1)
    time.sleep(1)   


    break

try:
    while(running):
        time.sleep(1)
        time.sleep(1)
        readingArd()
except (KeyboardInterrupt):
    running = False    
    print ("Applications closed!")
    



