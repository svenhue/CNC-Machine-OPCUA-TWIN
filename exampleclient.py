
import sys
import opcua
from opcua import Client, ua


class SubHandler():

    def datachange_notification(node, val, data):
        print(node, ":", val)
        pass

def main():

    url = "opc.tcp://localhost:4840/"

    client = Client(url)
    client.set_user("Admin")
    client.set_password("Basic256Sha256")
    client.connect()
    base = client.get_objects_node()

    machine_state = client.get_node("ns=1;i=2")
    machine_temp = client.get_node("ns=1;i=3")
    task = client.get_node("ns=1;i=21")
    task_status = client.get_node("ns=1;i=22")
    task_starttime = client.get_node("ns=1;i=23")
    task_stoptime = client.get_node("ns=1;i=24")
    workpiece = client.get_node("ns=2;i=1")
    workpiece_status = client.get_node("ns=2;i=2")
    workpiece_weight = client.get_node("ns=2;i=3")
    workpiece_height = client.get_node("ns=2;i=4")
    workpiece_position = client.get_node("ns=2;i=5")
    program_name = client.get_node("ns=3;i=2")

    sub = client.create_subscription(1, SubHandler)

    sub.subscribe_data_change(machine_state)
    sub.subscribe_data_change(machine_temp)
    sub.subscribe_data_change(task)
    sub.subscribe_data_change(task_status)
    sub.subscribe_data_change(task_starttime)
    sub.subscribe_data_change(task_stoptime)
    sub.subscribe_data_change(workpiece_position)
    sub.subscribe_data_change(workpiece_weight)
    sub.subscribe_data_change(workpiece_height)

    

    method_change_machinestate = client.get_node("ns=1;i=2001")
    method_manualtask = client.get_node("ns=2;i=6")
    method_program = client.get_node("ns=3;i=3")
  
    base.call_method(method_program, "simulation")
    
    pass


if __name__ == "__main__":
    main()