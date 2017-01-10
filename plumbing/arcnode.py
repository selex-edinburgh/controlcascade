'''
Copyright (c) 2017 Leonardo MW Ltd

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software in a limited manner. Permissions to publish, distribute, sublicense or sell the Software are not granted. Permissions granted are: the rights to use, copy, modify and merge copies of the Software solely within the context of the "Rampaging Chariots" educational project, and subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
import Queue
import threading
import time
import sys
import traceback

class ArcNode(threading.Thread):

    def __init__ (self, stateData, loopFunction, minPeriod, maxPeriod, name="Unnamed Loop"):
        super(ArcNode,self).__init__()

        self.queue = Queue.Queue()
        self._minperiod = minPeriod
        self._maxperiod = maxPeriod
        self._loopFunction = loopFunction
        self.stateData = stateData
        self.setDaemon(True)
        self.name = name
        self._running = True
    
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
                pass
                timeout = (haveDataDeadline if haveData else haveNoDataDeadline)\
                           - time.time()
                try:
                    item = self.queue.get(True,max(timeout,0))
                    if item['messageType'] == 'loopControlMessage':
                        if item['quitLoops']: return
                        self._running =  not item['stopLoops']
                        
                    if self._running:
                        batchdata.append(item)
                        haveData = True
                except Queue.Empty:
                    pass
                except:
                    traceback.print_exc()
                t = time.time()
                if (t >= haveDataDeadline and haveData ) or \
                        ( t >= haveNoDataDeadline  ) : # and if flag is NOT true
                    break
            self._lastrun = time.time()
            if self._running:
                self.stateData.writer_acquire()
                try:
                    self._loopFunction(self.stateData, batchdata)
                except:
                    traceback.print_exc()
                self.stateData.writer_release()
                self.stateData.notify()
           
    def connectTo(self,destLoop,trFn):
        obsTr = ArcNodeObserverTranslator(destLoop, trFn)
        self.stateData.attach(obsTr)

class ArcNodeObserverTranslator:
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
