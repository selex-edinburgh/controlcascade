import Obstacle

class Wall(Obstacle.Obstacle):
    def __init__(self,x1,y1,x2,y2):
        self.x1, self.y1 = [x1,y1]
        self.x2, self.y2 = [x2,y2]
        self.width = 2
