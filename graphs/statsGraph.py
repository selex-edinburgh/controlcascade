'''
Copyright (c) 2017 Leonardo MW Ltd

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software in a limited manner. Permissions to publish, distribute, sublicense or sell the Software are not granted. Permissions granted are: the rights to use, copy, modify and merge copies of the Software solely within the context of the "Rampaging Chariots" educational project, and subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.patches as mpatches
import time

fig = plt.figure()
ax1 = fig.add_subplot(1,1,1)
ax2 = fig.add_subplot(1,1,1)
ax3 = fig.add_subplot(1,1,1)
def animate(i):
    try:
        pullData = open("log/loopStats.txt","r").read()
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
    except:
        pass
ani = animation.FuncAnimation(fig, animate, interval=100)

plt.show()
