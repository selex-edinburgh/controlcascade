'''
Copyright (c) 2017 Leonardo MW Ltd

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software in a limited manner. Permissions to publish, distribute, sublicense or sell the Software are not granted. Permissions granted are: the rights to use, copy, modify and merge copies of the Software solely within the context of the "Rampaging Chariots" educational project, and subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
import readersWriterLock
import time

class ObservableState(readersWriterLock.RWLock):

    def __init__(self):
        super(ObservableState,self).__init__()
        # who should be notified
        self.__dict__['_observers'] = []
        self.__dict__['_changed'] = False
        self.__dict__['timeStampFlow'] = {}
        
    def __setattr__(self, attrname, value):
        # intecept state updates
        self.__dict__[attrname] = value
        if attrname[0] != '_':
            # attr prefixed with _ are 'private'
            self.__dict__['_changed'] = True

    def initAttr(self, attrname, value):
        self.__dict__[attrname] = value
        
    def attach(self, observer):
        if not observer in self._observers:
            self._observers.append(observer)
            
    def notify(self, force=False):
        if ( force or self._changed ):
            for observer in self._observers:
                observer.update(self)
        self.__dict__['_changed'] = False

    def timeStampNow(self, flowType):
        self.timeStampFlow[flowType] = time.time()
        self._changed = True 
    
    