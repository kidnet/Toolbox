class ToolboxEexception(Exception):
    #The base Toolbox exception from which all others should subclass.
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg

class FileNotFound(ToolboxEexception):
    pass

class ConnectionFiled(ToolboxEexception):
    pass

class CommandExecutionError(ToolboxEexception):
    pass

class CommandExectuionTimeout(ToolboxEexception):
    pass
