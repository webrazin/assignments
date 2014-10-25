import diff_drive
import ach
import sys
import time
from ctypes import *
import socket
import cv2.cv as cv
import cv2
import numpy as np

dd = diff_drive
ref = dd.H_REF()
tim = dd.H_TIME()

ROBOT_DIFF_DRIVE_CHAN   = 'robot-diff-drive'
ROBOT_CHAN_VIEW   = 'robot-vid-chan'
ROBOT_TIME_CHAN  = 'robot-time'
# CV setup 
cv.NamedWindow("wctrl", cv.CV_WINDOW_AUTOSIZE)
#capture = cv.CaptureFromCAM(0)
#capture = cv2.VideoCapture(0)

# added
##sock.connect((MCAST_GRP, MCAST_PORT))
newx = 320
newy = 240

nx = 640
ny = 480

r = ach.Channel(ROBOT_DIFF_DRIVE_CHAN)
r.flush()
v = ach.Channel(ROBOT_CHAN_VIEW)
v.flush()
t = ach.Channel(ROBOT_TIME_CHAN)
t.flush()

i=0
move_x=0;

while True:
    # Get Frame
    img = np.zeros((newx,newy,3), np.uint8)
    c_image = img.copy()
    vid = cv2.resize(c_image,(newx,newy))
    [status, framesize] = v.get(vid, wait=False, last=True)
    if status == ach.ACH_OK or status == ach.ACH_MISSED_FRAME or status == ach.ACH_STALE_FRAMES:
        vid2 = cv2.resize(vid,(nx,ny))
        img = cv2.cvtColor(vid2,cv2.COLOR_BGR2RGB)
        cv2.imshow("wctrl", img)
        cv2.waitKey(10)
    else:
        raise ach.AchException( v.result_string(status) )


    [status, framesize] = t.get(tim, wait=False, last=True)
    if status == ach.ACH_OK or status == ach.ACH_MISSED_FRAME or status == ach.ACH_STALE_FRAMES:
        pass
        #print 'Sim Time = ', tim.sim[0]
    else:
        raise ach.AchException( v.result_string(status) )
        
    sim_time=tim.sim[0];
    new_sim_time=0; 
    
    blur = cv2.GaussianBlur(img,(5,5),0)

    
    blue,green,red = cv2.split(blur);
    ret,threshold = cv2.threshold(red,1,1,cv2.THRESH_BINARY_INV)
     
    M = cv2.moments(threshold)
    if M["m00"] != 0:
    	centroid_x = int(M['m10']/M['m00'])
    	centroid_y = int(M['m01']/M['m00'])
    	red_values= (0,0,200)
    	cv2.circle(img, (int(centroid_x),int(centroid_y)), 10, red_values,-1,8,0) 
    	# can put the text from blue track
    	error=320-centroid_x
    	
    	print centroid_x
    	print 'Difference = ',move_x-centroid_x
    	print error
    	 
    	if error<0: #robot moving right, clockwise to track the object 
            ref.ref[0] = -.1*(abs(error)/10)
            ref.ref[1] = .1*(abs(error)/10)
        elif error>0: # robot moving left, counterclockwise, to
            ref.ref[0] = .1* (abs(error)/10)
            ref.ref[1] = -.1*(abs(error)/10)
        else: 
            ref.ref[0] = 0            
            ref.ref[1] = 0
    	
    	cv2.imshow("tracking object", img)
        r.put(ref);
        #cv2.imshow("wctrl", img)
        r.put(ref);
        
        move_x=centroid_x; 
        
    while new_sim_time<0.06:
	[status, framesize] = t.get(tim, wait=False, last=True)
        new_sim_time=tim.sim[0]-sim_time 	
    	


