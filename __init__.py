import snipets.json_to_object


class Person(object):
    def __init__(self):
        pass
    
    def load(self, filename):
        o = snipets.json_to_object.Object()
        o.load_file(filename)
        print o
        


