from xmlrpc.client import Boolean
from digitaltwin import MController
from opcua import Server, ua, uamethod
from opcua.common.manage_nodes import create_method

  
server = Server()
    # opcua server setup
url = "opc.tcp://localhost:4840/"
server.set_endpoint(url)
server.set_security_IDs(["Anonymous", "Basic256Sha256", "Admin"])
server.allow_remote_admin("allow")
uri = "http://moduco.de/Basic"
namespace = server.register_namespace(uri)
objects = server.get_objects_node()
server.start()
print("Server started at {}".format(url))

    # register nodes
machine = objects.add_object("ns=1;i=1", "Machine")
machine_status = machine.add_variable("ns=1;i=2", "machine_status", False)
machine_temp = machine.add_variable("ns=1;i=3", "machine_temp", 0)

task = objects.add_object("ns=1;i=21", "task")
task_status = task.add_variable("ns=1;i=22", "task_status", False)
task_starttime = task.add_variable("ns=1;i=23", "task_starttime", False)
task_stoptime = task.add_variable("ns=1;i=24", "task_stoptime", False)

workpiece = objects.add_object("ns=2;i=1", "Workpiece")
workpiece_status = workpiece.add_variable("ns=2;i=2", "workpiece_status", "")
workpiece_weight = workpiece.add_variable("ns=2;i=3", "workpiece_weight", 0)
workpiece_height = workpiece.add_variable("ns=2;i=4", "workpiece_height", 0)
workpiece_position = workpiece.add_variable("ns=2;i=5", "workpiece_position", "")
program = objects.add_object("ns=3;i=1", "Program")
program_name = program.add_variable("ns=3;i=2", "Program", "")


    # Empfängt die Ergebnisse (Outputs) der Aufgaben und aktualisiert die Nodes im Namespace
class DataObserver():

    def update(self, args):
        for key, value in args.items():
            output = globals()[key]
            output.set_value(value)
        pass


    # controller setup
machine_controller = MController()
obs = DataObserver()
controller = machine_controller.setup(obs)

    # ua args for method "change_machine_state"
statusUA = ua.Argument()
statusUA.Name = "StatusUA"
statusUA.DataType = ua.NodeId(ua.ObjectIds.Boolean)
statusUA.ArrayDimensions = []
statusUA.Description = ua.LocalizedText("Status change")
statusoutput = ua.Argument()
statusoutput.Name = "StatusOutputUA"
statusoutput.DataType = ua.NodeId(ua.ObjectIds.Boolean)
statusoutput.ArrayDimensions = []
statusoutput.Description = ua.LocalizedText("Status change output")

taskUA = ua.Argument()
taskUA.Name = "TaskUA"
taskUA.DataType = ua.NodeId(ua.ObjectIds.String)
taskUA.ArrayDimensions = []
taskUA.Description = ua.LocalizedText("task execution")

taskUAinstruction = ua.Argument()
taskUAinstruction.Name = "TaskUAInstruction"
taskUAinstruction.DataType = ua.NodeId(ua.ObjectIds.Integer)
taskUAinstruction.ArrayDimensions = []
taskUAinstruction.Description = ua.LocalizedText("task execution")

taskoutput = ua.Argument()
taskoutput.Name = "TaskOutputUA"
taskoutput.DataType = ua.NodeId(ua.ObjectIds.String)
taskoutput.ArrayDimensions = []
taskoutput.Description = ua.LocalizedText("task execution result")

programUA = ua.Argument()
programUA.Name = "ProgramUA"
programUA.DataType = ua.NodeId(ua.ObjectIds.String)
programUA.ArrayDimensions = []
programUA.Description = ua.LocalizedText("Program")

programoutputUA = ua.Argument()
programoutputUA.Name = "ProgramUA"
programoutputUA.DataType = ua.NodeId(ua.ObjectIds.String)
programoutputUA.ArrayDimensions = []
programoutputUA.Description = ua.LocalizedText("Program")

    #Callable ua methods
@uamethod
def change_machine_status(parent, status):
    if status == True:
        controller.startmachine()
        return status
 
    elif status == False:
        controller.stopmachine()
        return status

@uamethod
def manualtask(parent, task, instruction):
    controller.instructmanualtaskexecution(task, instruction)
    

@uamethod
def startprogram(parent, name):
    program = controller.runprogram(name)
    return program

      #Register methods in namespace
machine.add_method(1, "change machine status", change_machine_status, [statusUA], [statusoutput])
machine.add_method(2, "manual task execition", manualtask, [taskUA, taskUAinstruction ], [taskoutput])
machine.add_method(3, "run program", startprogram, [programUA], [programoutputUA])


    