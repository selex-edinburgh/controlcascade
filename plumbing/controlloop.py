import Queue
import threading
import time

class ControlLoop(threading.Thread):
    """ 
        A thread class that 
    """
    
    def __init__ (self, stateData, loopFunction, minPeriod, maxPeriod, name="Unnamed Loop"):
        super(ControlLoop,self).__init__()
        self.daemon = True
        self.queue = Queue.Queue()
        self._minperiod = minPeriod
        self._maxperiod = maxPeriod
        self._loopFunction = loopFunction
        self.stateData = stateData
        threading.Thread.__init__ (self)
        self.name = name

    
    def run(self):
        self._lastrun = time.clock()
        while True:
            batchdata = []
            haveData = False
            haveDataDeadline = self._lastrun + self._minperiod
            haveNoDataDeadline = self._lastrun + self._maxperiod
            while True:
                #keep gathering data until minPeriod has passed
                #or if nothing appears, continue waiting until maxPeriod before giving up
                timeout = (haveDataDeadline if haveData else haveNoDataDeadline)\
                           - time.clock()
                try:
                    batchdata.append(self.queue.get(True,max(timeout,0)))
                    haveData = True
                except Queue.Empty:
                    pass
                except Exception as err:
                    print err
                t = time.clock()
                if (t >= haveDataDeadline and haveData) or  ( t >= haveNoDataDeadline ):
                    break
            self._lastrun = time.clock()
            self.stateData.writer_acquire()
            self._loopFunction(self.stateData, batchdata)
            self.stateData.writer_release()
            self.stateData.notify()


class ControlObserverTranslator:
    def __init__(self, destinationLoop, translateFunction):
        self._destLoop = destinationLoop
        self._destStateData = destinationLoop.stateData
        self._destQueue = destinationLoop.queue
        self._transFunction = translateFunction
    def update(self,updatedState):
        self._destStateData.reader_acquire()
        updatedState.reader_acquire()
        try:
            self._transFunction(updatedState, self._destStateData, self._destQueue)
        except Exception as err:
            print err
        finally:
            self._destStateData.reader_release()
            updatedState.reader_release()
