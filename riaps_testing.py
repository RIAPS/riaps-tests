"""RIAPS testing helper methods
"""
import os
import sys
import yaml
import paramiko
import zmq
import time
import threading

stream = open('riaps_testing_config.yml', 'r')
config = yaml.load(stream, Loader=yaml.Loader)
stream.close()
for key in {"hosts", "username", "password", "logPath", "logPrefix"}:
    assert key in config, "Failed to find '%s' in configuration file" % key

# Configure SSH
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

#Create ZMQ context

ctx = zmq.Context()

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

def powerCycleControl(hostname, events):
    sock = ctx.socket(zmq.REQ)
    sock.connect('tcp://'+config['hosts'][hostNum]+':2234')
    msg = ('power',1) #second field is arbitrary for now, there in case one node could turn off multiple others

    for timediff in events:
        time.sleep(timediff)
        sock.send_pyobj(msg)
        assert sock.recv_pyobj() == 'Powercycle sent', "Powercycle failed for timediff: %d" % timediff

def runTest(name, folder, riaps, depl, startupTime=60, runTime=60, cleanupTime=10, powerTiming=None):
    """Run a RIAPS application on BBB hosts

    Args:
        name   (str): The name of RIAPS application
        folder (str): Path to the folder containing the riaps and depl files
        riaps  (str): Name of the riaps file containing the application model
        depl   (str): Name of the depl file containing the application deployment
        startupTime (int, optional): Time to wait for nodes to connect to riaps_ctrl. Defaults to 10 seconds.
        runTime     (int, optional): Time to let application run. Defaults to 30 seconds.
        cleanupTime (int, optional): Time to wait after halting the application. Defaults to 10 seconds.
        powerTiming (dic, optional): An (int):(list) dict of timing to cycle power on nodes.
            The key is which index in the list of configured hosts (starting from zero) is sending the power signal.
            The list is the amount of time slept (secs) between power signals being sent, starting concurrently
                with riaps_ctrl.

    Returns:
        dictionary: A dictionary where the keys are the names of the log files collected. Each element is a
            a list of strings representing the lines of the log file.

    Raises:
        AssertionError: Raised if any invalid arguments are passed or if a test fails.

    """
    # Verify that arguments point to valid files
    assert name != "" and not (' ' in name), "Invalid test name: %s" % name
    assert os.path.isdir(os.path.join(folder)), "Failed to find test folder: %s" % folder
    assert os.path.isfile(os.path.join(folder, riaps)), "Failed to find test riaps file: %s" % riaps
    assert os.path.isfile(os.path.join(folder, depl)), "Failed to find depl file: %s" % depl

    # Force folder to be an absolute path
    if not os.path.isabs(folder):
        folder = os.path.join(os.getcwd(), folder)

    # Verify that all hosts are accessible
    for host in config['hosts']:
        print("Verifying connection to %s" % host)
        try:
            client.connect(host, username=config['username'], password=config['password'])
            # Remove any existing logs in the logPath
            client.exec_command("sudo rm -rf %s" % os.path.join(config['logPath'], config['logPrefix']))
        except:
            assert False, "Failed to connect host: %s" % host
        finally:
            client.close()

    # Read the provided riaps and depl files
    file = open(os.path.join(folder, riaps), "r")
    model = file.read()
    file.close()
    file = open(os.path.join(folder, depl), "r")
    deployment = file.read()
    file.close()

    # Parse files
    model, num_hosts = parseString(model, name)
    deployment, num_hosts = parseString(deployment, name)

    # Write parsed files
    file = open(os.path.join(folder, "test.riaps"), "w")
    file.write(model)
    file.close()
    file = open(os.path.join(folder, "test.depl"), "w")
    file.write(deployment)
    file.close()

    # Create test.rc file
    file = open("test.rc", "w")
    file.write("w %d\n" % startupTime)
    file.write("f %s\n" % folder)
    file.write("m test.riaps\n")
    file.write("d test.depl\n")
    file.write("l %s\n" % name)
    file.write("w %d\n" % runTime)
    file.write("h %s\n" % name)
    file.write("w %s\n" % cleanupTime)
    file.write("r %s\n" % name)
    file.write("w %s\n" % cleanupTime)
    file.write("q\n")
    file.close()

    if powerTiming is not None:
        threadPool = []
        for key in powerTiming:
            threadPool.append(threading.Thread(target=powerCycleControl,args=(key,powerTiming[key])))
        for thread in threadPool:
            thread.start()

    # Launch riaps_ctrl
    assert os.system("riaps_ctrl test.rc") == 0, "Error while running riaps_ctrl"

    if powerTiming is not None:
        for thread in threadPool:
            thread.join(timeout=1.0)
            assert thread.is_alive() == False, "A powerCycleControl thread failed to close!"

    # Collect logs
    logs = {}
    for i in range(num_hosts):
        host = config['hosts'][i]
        print("Collecting logs from %s" % host)
        try:
            # Find all log files on the target host
            client.connect(host, username=config['username'], password=config['password'])
            stdin, stdout, stderr = client.exec_command("ls %s" % os.path.join(config['logPath'], config['logPrefix']))
            for line in stderr:
                print(line.strip('\n'))
            for logfile in stdout:
                logfile = logfile.strip('\n')
                print("Found logfile on %s named %s" % (host, logfile))
                stdin2, stdout2, stderr2 = client.exec_command("cat %s" % os.path.join(config['logPath'], logfile))
                log = []
                for line in stdout2:
                    line = line.strip('\n')
                    print(line)
                    log.append(line)
                logs["%d_%s" % (i, logfile)] = log
        except:
            assert False, "Failed to retrieve logs from host: %s" % host
        finally:
            client.close()
    return logs
