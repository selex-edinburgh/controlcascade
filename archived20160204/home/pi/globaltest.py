x=10
print "x=", x

def funct():
    global x
    x= x+1
    print "x=", x

funct()
print "x=", x
