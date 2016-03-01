### Superclass for various course types.
class Course(object):

    ### Empty constructor
    def __init__(self):
        pass

    ### (Stub) Read obstacles in from a csv file.
    ### returns => a list of obstacles.
    def readCsv(self):
        obs = []
        with open('assault.csv', 'r') as f:
            for line in f:
                tokens = line.split(',')
                if 'pole' in tokens[0]:
                    obs.append(Pole(eval(tokens[1])/10,eval(tokens[2])/10))
                elif 'wall' in tokens[0]:
                    print(tokens)
                    new = Wall(eval(tokens[1])/10,eval(tokens[2])/10,\
                                eval(tokens[3])/10,eval(tokens[4])/10)
                    self.walls.append(new)
                    print(new.x, new.y)
        return obs

### Superclass for all obstacles.
### x -> the x axis position of the obstacle in mm.
### y -> the y axis position of the obstacle in mm.
class Obstacle(object):
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 0
        self.height = 0
        self.passable = False

### A pole of diameter 50mm.
class Pole(Obstacle):
    def __init__(self,x,y):
        super(Pole, self).__init__(x, y)
        self.width = 5
        self.height = 5

### An impassible wall.
### x -> x position of one end in mm
### y -> y position in one end mm
### x1 -> x position of the other end in mm
### y1 -> y position of the other end in mm
class Wall(Obstacle):
    def __init__(self,x,y,x1,y1):
        super(Wall, self).__init__(x,y)
        self.x1 = x1
        self.y1 = y1

### A ramp of size 50x150mm
### x -> the x axis position in mm.
### y -> the y axis position in mm.
class Ramp(Obstacle):
    def __init__(self,x,y):
        super(Ramp, self).__init__(x,y)
        self.width = 50
        self.length = 150
        self.passable = True

### A barrel
### x -> the x axis position in mm.
### y -> the y axis position in mm.
class Barrel(Obstacle):
    
    def __init__(self,x,y):
        super(Barrel,self).__init__(x,y)
        self.passable = True

### A ball.
### x -> the x axis position in mm.
### y -> the y axis position in mm.
class Ball(Obstacle):
    
    def __init__(self,x,y):
        super(Ball,self).__init__(x,y)
        self.passable = True

### A net.
### x -> the x axis position in mm.
### y -> the y axis position in mm.
class Net(Obstacle):
    
    def __init__(self,x,y):
        super(Net, self).__init__(x,y)
        self.passable = True

### A door
### x -> the x axis position in mm.
### y -> the y axis position in mm.
class Door(Obstacle):
    
    def __init__(self,x,y):
        super(Door, self).__init__(x,y)
        
        
