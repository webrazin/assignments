import hubo_ach as ha
import ach
import sys
import time
import math
from ctypes import *

# Open Hubo-Ach feed-forward and feed-back (reference and state) channels

s = ach.Channel(ha.HUBO_CHAN_STATE_NAME)
r = ach.Channel(ha.HUBO_CHAN_REF_NAME)
s.flush()
r.flush()

# feed-forward will now be refered to as "state"
state = ha.HUBO_STATE()

# feed-back will now be refered to as "ref"
ref = ha.HUBO_REF()

# the idea of the calculation has been obtained from 

#http://www.3dkingdoms.com/ik.htm

# Get the current feed-forward (state) 
[statuss, framesizes] = s.get(state, wait=False, last=False)
# calculation of joint angles
x=-.25*1000;
y=-0.20*1000;
z=0.20*1000;
l1=229
l2=182
l3= math.sqrt(math.pow(x,2)+math.pow(y,2)+math.pow(z,2))

print "l3=",l3

theta2= math.acos((math.pow(l1,2)+math.pow(l2,2)-math.pow(l3,2))/(2*l1*l2))*57

print "theta2=",theta2

theta2_degree=180-theta2

print "theta2_degree=",theta2_degree

rad= theta2_degree/57

print "rad=",rad

#Set Left Elbow Bend (LEB) and Right Shoulder Pitch (RSP) to  -0.2 rad and 0.1 rad respectively
#ref.ref[ha.LEB] = -0.2
ref.ref[ha.REB] = -rad
#ref.ref[ha.RSP] = 0.1
#cref.ref[ha.RSP] = 0.1

# Print out the actual position of the LEB
print "Joint = ", state.joint[ha.REB].pos

# Print out the Left foot torque in X
print "Mx = ", state.ft[ha.HUBO_FT_L_FOOT].m_x

# Write to the feed-forward channel
r.put(ref)

# Close the connection to the channels
r.close()
s.close()


