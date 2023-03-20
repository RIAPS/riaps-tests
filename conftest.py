import pytest
import time
from riaps.ctrl.ctrl import Controller
from riaps.utils.config import Config
import pathlib
import yaml
import os


stream = open('riaps_testing_config.yml', 'r')
config = yaml.load(stream, Loader=yaml.SafeLoader)
stream.close()
for key in {"hosts", "username", "password", "logPath", "logPrefix"}:
    assert key in config, "Failed to find '%s' in configuration file" % key

def parseString(str, name):
    """Replace keywords in string (commonly the contents of a file)

    This is a helper method for the runTest(...) method. It will automatically replace
    any keywords with the appropriate strings to automate testing.

    Args:
        str  (str): The string in which to replace keywords
        name (str): The name of the RIAPS application

    Returns:
        (str, int): The newly parsed string and the number of hosts required for running the test.

    """
    str = str.replace("NAME", name)

    num_hosts = 0
    while str.find("HOST") != -1:
        assert num_hosts < len(config['hosts']), "More hosts required than provided"
        # Replace the first instance of HOST with the next available host
        str = str.replace("HOST", config['hosts'][num_hosts], 1)
        num_hosts += 1

    return (str, num_hosts)

# use 'opendht' or 'redis'
disco_type = 'opendht'

def factory_is_cluster_ready(app_info):
    if "num_nodes" in app_info:
        count = app_info['num_nodes']
        def func(ctrl):
            return len(ctrl.getClients()) >= count
        return func
    elif "nodes" in app_info:
        clients = set(app_info['nodes'])
        def func(ctrl):
            return clients.issubset(set(ctrl.getClients()))
        return func
    raise
        
@pytest.fixture
def riaps_ctrl(request):
    marker = request.node.get_closest_marker("app_setup")
    if marker is None:
        raise
    app_info = marker.args[0]
    app_folder = pathlib.PosixPath(request.path).parent

    # Read the provided riaps and depl files
    file = open(os.path.join(app_folder, app_info['model']), "r")
    model = file.read()
    file.close()
    file = open(os.path.join(app_folder, app_info['deployment']), "r")
    deployment = file.read()
    file.close()

    model, num_hosts = parseString(model, app_info['name'])
    deployment, num_hosts = parseString(deployment, app_info['name'])

    # Write parsed files
    file = open(os.path.join(app_folder, "test.riaps"), "w")
    file.write(model)
    file.close()
    file = open(os.path.join(app_folder, "test.depl"), "w")
    file.write(deployment)
    file.close()

    is_cluster_ready = factory_is_cluster_ready(app_info)
    the_config = Config()
    c =  Controller(port=8888, script="-")
    c.setAppFolder(app_folder)
    app_name = c.compileApplication("test.riaps",app_folder)
    try:
        _ = c.compileDeployment("test.depl")
        c.discoType = disco_type
        if disco_type == 'opendht':
            c.startDht()
        else:
            c.startRedis()
        c.startService()

        counter = 300
        while not is_cluster_ready(c):
            known_clients = c.getClients()
            print(f"{len(known_clients)} known clients: {known_clients}")
            time.sleep(1)
            counter -= 1
            if counter <= 0:
                print("ERROR: wait for clients timed out")
                raise
        
        yield c

    finally:
        # Remove application
        print("remove app")
        c.removeAppByName(app_name)  # has no return value.
        # removeAppByName (line 914).
        print("app removed")

        # Stop controller
        print("Stop controller")
        c.stop()
        print("controller stopped")