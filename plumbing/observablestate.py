import readersWriterLock


class ObservableState(readersWriterLock.RWLock):

    def __init__(self):
        super(ObservableState,self).__init__()
        # who should be notified
        self.__dict__['_observers'] = []
        self.__dict__['_changed'] = False
        
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

    
    
