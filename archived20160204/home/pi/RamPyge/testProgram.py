import ControlBoard
import time



cb = ControlBoard()

time.sleep(2)

cb.forward(200)

time.sleep(2)

cb.reverse(40)

time.sleep(2)

cb.stop()
