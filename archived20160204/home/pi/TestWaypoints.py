import math, time

route = 1
#Straight line
if route == 1:
    title = "Straight Line Test."
#                 X      Y      Dist  Hdg      #Hdg required at Waypoint
    Waypoints = [(0), (0),    (0),    (0),    #WP 0   Start Waypoint = origin
                (3000), (4000),    (0),    (0),     #WP 1
                (6000), (8000),    (0),    (0),     #WP 2
                (3000), (4000),    (0),    (0),     #WP 3
                (3000), (4000),    (0),    (0),     #WP 3
                    ]
EndWpNo = 1
    

#Calculate WPDist between Xn,Yn and Xn+1,Yn+1 using Pythagoras
for n in range(6, (EndWpNo+3)*4, 4):
    Xdist= Waypoints[n+2]-Waypoints[n-2]
    Ydist= Waypoints[n+3]-Waypoints[n-1]
    SumOfSquares= Xdist**2 + Ydist**2
#    hypot = int(math.sqrt(Xdist**2 + Ydist**2))
    hypot = int(math.sqrt(SumOfSquares))
    
    Waypoints[n] = hypot

for n in range(0, (EndWpNo+4)*4, 4):
        print(Waypoints[n], Waypoints[n+1], Waypoints[n+2], Waypoints[n+3])
                   
