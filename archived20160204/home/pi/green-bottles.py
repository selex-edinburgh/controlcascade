# Example of saving data to a file

import time

# open the file for writing
# (the 'a' means append to end if file already exists)
logfile = open('/home/pi/bottles.csv', 'a')

# write the column headings
logfile.write("time, bottles remaining, bottles lost\n")

# bottlesLost will take on values from 0 to 10
for bottlesLost in range(11):

    # calculate how many bottles are left
    bottlesRemaining = 10 - bottlesLost

    # display a nice message for the user
    print "There were %d green bottles, sitting on the wall" % bottlesRemaining

    # log the results to the log file
    logfile.write(time.strftime("%H:%M:%S"))
    logfile.write(", ")
    logfile.write("%d" % bottlesRemaining)
    logfile.write(", ")
    logfile.write("%d" % bottlesLost)
    logfile.write("\n")

    # wait 1 second
    time.sleep(1)

# close the file
logfile.close()    
