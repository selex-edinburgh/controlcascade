import Queue
import threading
import time
import sys
import traceback

class ControlLoop(threading.Thread):
    """ 
        A thread class that 
    """
    
    def __init__ (self, stateData, loopFunction, minPeriod, maxPeriod, name="Unnamed Loop"):
        super(ControlLoop,self).__init__()

        self.queue = Queue.Queue()
        self._minperiod = minPeriod
        self._maxperiod = maxPeriod
        self._loopFunction = loopFunction
        self.stateData = stateData
        self.setDaemon(True)
        self.name = name

    
    def run(self):
        print "starting thread\n"
        self._lastrun = time.time()
        while True:
            batchdata = []
            haveData = False
            haveDataDeadline = self._lastrun + self._minperiod
            haveNoDataDeadline = self._lastrun + self._maxperiod
            while True:
                #keep gathering data until minPeriod has passed
                #or if nothing appears, continue waiting until maxPeriod before giving up
                timeout = (haveDataDeadline if haveData else haveNoDataDeadline)\
                           - time.time()
                try:
                    batchdata.append(self.queue.get(True,max(timeout,0)))
                    haveData = True
                except Queue.Empty:
                    pass
                except:
                    traceback.print_exc()
                t = time.time()
                if (t >= haveDataDeadline and haveData) or  ( t >= haveNoDataDeadline ):
                    break
            self._lastrun = time.time()
            self.stateData.writer_acquire()
            try:
                self._loopFunction(self.stateData, batchdata)
            except:
                traceback.print_exc()
            self.stateData.writer_release()
            self.stateData.notify()

    def connectTo(self,destLoop,trFn):
        obsTr = ControlObserverTranslator(destLoop, trFn)
        self.stateData.attach(obsTr)
            

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
        #except Exception as err:
           # print err
        finally:
            self._destStateData.reader_release()
            updatedState.reader_release()
