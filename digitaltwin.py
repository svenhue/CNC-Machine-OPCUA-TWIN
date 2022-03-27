from datetime import datetime
import random
import time
import sys
from pprint import pprint

 # Aktuatoren simulieren die Signale des Steuergeräts (MController) und führen Aktionen mit dem Werkstück aus
 # input meistens = Werkstück
class RotaryActuator:
    
    def run(self, input, instruction):
        workpiece_weight = input.weight 
        workpiece_height = input.height
        workpiece_weight = workpiece_weight - instruction * 2
        workpiece_height = workpiece_height - instruction * 1
        output = {"workpiece_height": workpiece_height, "workpiece_weight": workpiece_weight}
        
        return output

class PositioningActuator:
    
    def run(self, input, instruction):
        output = {} 
        if instruction == "clamp_workpiece":
            output["workpiece_position"] = "fixed"
            return output
        elif instruction == "release_workpiece":
            output["workpiece_position"] = "loosely"
            return output
    
    
    # Aufgaben, für die Parameter definiert werden können 
class MTask():

    tasks = {"clamp_workpiece" : {"time": 4, "requirements": {"actuator":"PositioningActuator"}}, 
             "rotate":  {"time": 4, "requirements": {"actuator":"RotaryActuator"}, "transitions": {"position":"fixed"}},
             "release_workpiece":{"time": 4, "requirements": {"actuator": "PositioningActuator"}}}
    
    def start(self):
        now = datetime.now() 
        self.starttime = now.strftime("%H:%M:%S")
        return self.starttime
        
    def stop(self):
        now = datetime.now()
        self.stoptime = now.strftime("%H:%M:%S")
        return self.stoptime

    def checktransitions(self, workpiece):
        if self.task_data.get("transitions") is not None:
            transitions = self.task_data.get("transitions")
            for key, value in transitions.items():
                subject = getattr(workpiece, key)
                if subject == value:
                    return True
                else:
                    return False
        else: 
            return True
                
    def instruct(self, taskname, instructions):
        task_data = MTask.tasks.get(taskname)
        self.task = taskname
        self.task_data = task_data
        self.instructions = instructions
        return self



class Workpiece():
 
    def __init__(self):
        self.type = "Grenztaster"
        self.weight = 400
        self.height = 20
        self.position = "loosely"
        pass

    # Sendet die durch eine Aufgabe veränderten Daten (Werkstück, Aufgabe, Maschine) an den DataObserver, der die Notes im Namespace aktualisiert
class DataPublisher():

    def __init__(self):
        self._observers = []

    def subscribe(self, observer):
        self._observers.append(observer)

    def dispatch(self, args):
        for obs in self._observers:
            obs.update(args)

    def unsubscibe(self, observer):
        self._observers.remove(observer)
    
    # Ein Programm besteht aus x beliebigen Aufgaben, welche in der angegebenen Reihenfolge ausgeführt werden. Zudem können Anweisungen mitgegeben werden
class Program():

    programs = {"simulation": 
                {"tasks": [
                    {"task": "clamp_workpiece"}, 
                    {"task": "rotate", "instruction": 23}, 
                    {"task":"rotate", "instruction": 44}, 
                    {"task": "release_workpiece"}]}}

    def set(self, name):
        program = Program.programs.get(name)
        self.name = name
        self.program = program
        return self


    # Maschine führt die Aufgaben aus und gibt das Ergebnis zurück
class Machine():

    def __init__(self):
        self.temp = 20
        pass
    
    def executetask(self, controller, task):

        #if task.checktransitions(controller.workpiece) == True:
        starttime = task.start()
        time.sleep(task.task_data.get("time"))
        output =  getattr(self, task.task)(task, controller)
        stoptime = task.stop()
        output["task_starttime"] = starttime
        output["task_stoptime"] = stoptime
        output["task"] = task.task
        return output
        #else:
        #    output = {"task_status": "requirements not met"} 
        #    return output

    def clamp_workpiece(self, task, controller):
        workpiece = self.processoutput_withactuator(task, controller.workpiece, "clamp_workpiece")
        output = {"task_status": "finished", "workpiece_status": "unprocessed", "workpiece_height": 20, "workpiece_weight": 400}
        output.update(workpiece)
        return output

    def release_workpiece(self, task, controller):
        workpiece = self.processoutput_withactuator(task, controller.workpiece, "release_workpiece")
        output = {"workpiece_status": "processed", "task_status": "finished"}
        output.update(workpiece)
        return output
        
    def rotate(self, task, controller):
        
        workpiece = self.processoutput_withactuator(task, controller.workpiece, task.instructions)

        avaible_status = ["finished", "malfunction"]
        status = random.choices(avaible_status,[0.9, 0.1])
        temps = [56,60,61,55,66,71,80,50, 67, 74]
        temp = random.choices(temps, [0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1, 0.1])
        output = {"task_status" : status[0], "machine_temp": temp}
        output.update(workpiece)
        return output

    def processoutput_withactuator(self, task, workpiece, instructions):
        
        required_actuator_name = task.task_data.get("requirements").get("actuator")
        actuator = getattr(sys.modules[__name__], required_actuator_name)
        output = actuator.run(actuator, workpiece, instructions)
        return output

    # Der Controller ist das Interface des digitalen Zwillings und stellt alle verfügbaren Methoden bereit
class MController():

    def instructmanualtaskexecution(self, taskname, instructions):

        task = MTask()
        task = task.instruct(taskname, instructions)
        output = self.machine.executetask(self, task)
        self.dispatchoutputs(output)
        
        return output

    def setup(self, obs):
        self.machine = Machine()
        self.workpiece = Workpiece()
        self.pub = DataPublisher()
        self.pub.subscribe(obs)
        return self
    
    def startmachine(self):
        self.pub.dispatch({"machine_status" : True})
        pass

    def stopmachine(self):
        self.pub.dispatch({"machine_status": False})
        pass

    def dispatchoutputs(self, output):
        self.pub.dispatch(output)
        pass
    
    def runprogram(self, programname):
        program = Program()
        program = program.set(programname)
        self.taskloop(program)
        pass

    def taskloop(self, program):

        tasklist = program.program.get("tasks")      
        for task  in tasklist:
            output = self.instructmanualtaskexecution(task.get("task"), task.get("instruction"))
            output["program_name"] = program.name
            self.dispatchoutputs(output)
            

