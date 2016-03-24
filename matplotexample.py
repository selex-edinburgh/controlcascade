import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.patches as mpatches
import time

fig = plt.figure()
ax1 = fig.add_subplot(1,1,1)
ax2 = fig.add_subplot(1,1,1)

def animate(i):
    pullData = open("motorCommands.txt","r").read()
    dataArray = pullData.split('\n')
    xar = []
    yar = []
    bar2= []
    for eachLine in dataArray:
        if len(eachLine)>1:
            x,y,b = eachLine.split(',')
            xar.append(float(x))
            yar.append(float(y))
            bar2.append(float(b))
    ax1.clear()
    ax1.plot(xar,yar)
    ax2.plot(xar,bar2)
    blue_patch = mpatches.Patch(color='blue', label='Fwd')
    green_patch = mpatches.Patch(color='green', label='Turn')
    plt.legend(handles=[blue_patch, green_patch])

ani = animation.FuncAnimation(fig, animate, interval=100)

plt.show()
