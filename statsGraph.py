import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.patches as mpatches
import time

fig = plt.figure()
ax1 = fig.add_subplot(1,1,1)
ax2 = fig.add_subplot(1,1,1)
ax3 = fig.add_subplot(1,1,1)
def animate(i):
    pullData = open("loopStats.txt","r").read()
    dataArray = pullData.split('\n')
    xar = []
    yar = []
    yar2= []
    yar3 =[]
    for eachLine in dataArray:
        if len(eachLine)>1:
            x,y,a,b = eachLine.split(',')
            xar.append(float(x))
            yar.append(float(y))
            yar2.append(float(a))
            yar3.append(float(b))

    ax1.clear()
    ax1.plot(xar,yar)
    ax2.plot(xar,yar2)
    ax3.plot(xar,yar3)
    blue_patch = mpatches.Patch(color='blue', label='Average')
    green_patch = mpatches.Patch(color='green', label='Max')
    red_patch = mpatches.Patch(color ='red', label= 'Min')

    plt.legend(handles=[blue_patch, green_patch, red_patch])

ani = animation.FuncAnimation(fig, animate, interval=100)

plt.show()
