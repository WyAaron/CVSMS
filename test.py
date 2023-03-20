import threading
import time



    
    
        


class CustomThread(threading.Thread):
    def __init__(self, storageNode,message):
        # execute the base constructor
        threading.Thread.__init__(self)
        # store the value
        self.storageNode = storageNode
        self.message = message
    # override the run function
    def run(self):
        time.sleep(2)
        print(f'storageNode: {self.storageNode}  \n Message: {self.message}')
        # block for a moment
        # display a message
 
        
        

t1 = CustomThread("storageNodes","Hello")
t1.start()
print(f'hello world')



class testRAID(threading.Thread):
    def __init__(self,obj):
        # execute the base constructor
        threading.Thread.__init__(self)
        # store the value
        self.obj = obj
    # override the run function
    def run(self):
        time.sleep(2)
        # TODO: Change to SFTP function
        #TODO: implement in upload
        self.obj.owner = "shsssss"
        # block for a moment
        # display a message