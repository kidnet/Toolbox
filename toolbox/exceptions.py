class ToolboxEexception(Exception):
    #The base Toolbox exception from which all others should subclass.
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg

class ToolboxFileNotFound(ToolboxEexception):
    pass

class ToolboxConnectionFiled(ToolboxEexception):
    pass
