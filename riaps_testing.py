import os
import sys
import yaml
import paramiko

stream = open('riaps_testing_config.yml', 'r')
config = yaml.load(stream)
stream.close()
for key in {"hosts", "username", "password", "logPath", "logPrefix"}:
    assert key in config, "Failed to find '%s' in configuration file" % key

# Configure SSH
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

def parseString(str, name, folder, riaps, depl):
    str = str.replace("NAME", name)
    str = str.replace("FOLDER", folder)
    str = str.replace("RIAPS", riaps)
    str = str.replace("DEPL", depl)

    host = 0
    num_hosts = len(config['hosts'])
    while str.find("HOST") != -1:
        assert host < num_hosts, "More hosts required than provided"
        str = str.replace("HOST", config['hosts'][host], 1)
        host+=1

    return (str, host)

def runTest(name, folder, riaps, depl, startupTime=10, runTime=30, cleanupTime=10):
    # Verify that arguments point to valid files
    assert name != "" and not (' ' in name), "Invalid test name: %s" % name
    if not os.path.isabs(folder):
        folder = os.path.join(os.getcwd(), folder)
    assert os.path.isdir(os.path.join(folder)), "Failed to find test folder: %s" % folder
    assert os.path.isfile(os.path.join(folder, riaps)), "Failed to find test riaps file: %s" % riaps
    assert os.path.isfile(os.path.join(folder, depl)), "Failed to find depl file: %s" % depl

    # Verify that all hosts are accessible
    for host in config['hosts']:
        print("Verifying connection to %s" % host)
        try:
            client.connect(host, username=config['username'], password=config['password'])
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
    model, num_hosts = parseString(model, name, folder, riaps, depl)
    deployment, num_hosts = parseString(deployment, name, folder, riaps, depl)

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
    file.write("r %s\n" % name)
    file.write("w %s\n" % cleanupTime)
    file.write("q\n")
    file.close()

    # Launch riaps_ctrl
    assert os.system("riaps_ctrl test.rc") == 0, "Error while running riaps_ctrl"

    # Collect logs
    logs = {}
    for i in range(num_hosts):
        host = config['hosts'][i]
        print("Collecting logs from %s" % host)
        try:
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
    print("Starting log processing!")
    return logs