import os
import json

class Manager(object):
    def __init__(self, root):
        self.root = root

    def get_path(self, filename):
        return os.path.join(self.root, filename)

    def read_text(self, filename):
        path = self.get_path(filename)
        
        with open(path, 'r') as f:
            text = f.read()
        
        return text

    def write_text(self, filename, text):
        path = self.get_path(filename)

        #try:
        #os.makedirs(os.path.dirname(path))
        #except:
        #    pass
        
        #fd = os.open(path, os.O_WRONLY, 0666)
        #os.fchmod(fd,0666)
        #os.close(fd)
        
        with open(path, 'w') as f:
            f.write(text)
       
    def read_json(self, filename):
        try:
            text = self.read_text(filename)
        except:
            text = "{}"
        
        j = json.loads(text)
        
        return j

    def write_json(self, filename, j):
        text = json.dumps(j)
        
        self.write_text(filename, text)
    


