# Displaying Numbers

x = 3.7
y = 4.8
z = x + y

# integers
# output: 3 plus 4 equals 8

print"%d plus %d equals %d" % (x,y,z)

# real numbers
# output: 3.700000 plus 4.800000 equals 8.500000

print"%f plus %f equals %f" % (x,y,z)

# real numbers, two decimal places
# output: 3.70 plus 4.50 equals 8.50

print"%.2f plus %.2f equals %.2f" % (x,y,z)
