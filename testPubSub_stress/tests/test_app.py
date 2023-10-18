import datetime
import json
import pathlib
import pytest
import queue
import time

import riaps.test_suite.test_api as test_api

# --------------- #
# -- Config -- #
# --------------- #
vanderbilt_scott_config = {"VM_IP": "172.21.20.70",
                           "app_folder_path": pathlib.Path(__file__).parents[1],
                           "app_file_name": "stress.riaps",
                           "depl_file_name": "stress_vu_scott.depl"}

ncsu_config = {"VM_IP": "192.168.10.106",
               "app_folder_path": pathlib.Path(__file__).parents[1],
               "app_file_name": "stress.riaps",
               "depl_file_name": "stress_ncsu.depl"}

configs = {"vu_se": vanderbilt_scott_config,
           "ncsu": ncsu_config}

test_cfg = configs["vu_se"]


# -------------------------- #
# -- GUI DRIVEN APP TESTS -- #
# -------------------------- #
@pytest.mark.parametrize('platform_log_server', [{'server_ip': test_cfg["VM_IP"]}], indirect=True)
@pytest.mark.parametrize('log_server', indirect=True,
                         argvalues=[{'server_ip': test_cfg["VM_IP"],
                                     'log_config_path': f"{test_cfg['app_folder_path']}/riaps-log.conf"}])
def test_app(platform_log_server, log_server):
    app_folder_path = test_cfg["app_folder_path"]
    app_file_name = test_cfg["app_file_name"]
    depl_file_name = test_cfg["depl_file_name"]

    client_list = test_api.get_client_list(file_path=f"{app_folder_path}/{depl_file_name}")
    write_test_log(f"client list: {client_list}")

    event_q = queue.Queue()
    log_file_path = str(pathlib.Path(__file__).parents[1]) + "/server_logs"
    log_file_observer_thread = test_api.FileObserverThread(event_q, folder_to_monitor=log_file_path)
    log_file_observer_thread.start()

    controller, app_name = test_api.launch_riaps_app(
        app_folder_path=app_folder_path,
        app_file_name=app_file_name,
        depl_file_name=depl_file_name,
        database_type="dht",
        required_clients=client_list
    )

    stress_handler(event_q)

    input("Press a key to terminate the app\n")
    test_api.terminate_riaps_app(controller, app_name)
    print(f"Test complete at {time.time()}")


def write_test_log(msg):
    log_dir_path = pathlib.Path(__file__).parents[1] / 'tests' / 'test_logs'
    log_dir_path.mkdir(parents=True, exist_ok=True)
    with open(f"{log_dir_path}/test_log.txt", "a") as log_file:
        log_file.write(f"{datetime.datetime.utcnow()} | {msg}\n")


def stress_handler(event_q):
    try:
        files = {}
        total_connections = 0
        while True:
            try:
                event_source = event_q.get(10)  #
            except queue.Empty:
                write_test_log(f"File event queue is empty")
                continue

            if ".log" not in event_source:  # required to filter out the directory events
                continue

            file_name = pathlib.Path(event_source).name
            file_data = files.get(file_name, None)
            if file_data is None:
                file_handle = open(event_source, "r")
                files[file_name] = {"fh": file_handle, "offset": 0}
            else:
                file_handle = file_data["fh"]

            for line in file_handle:
                files[file_name]["offset"] += len(line)

                if "connections" in line:
                    msg = json.loads(line.split("::")[4])
                    connections = msg["connections"]
                    node = msg["id"]

                    if str(node) not in file_name:
                        continue

                    if files[file_name].get("connections", None) != connections:
                        files[file_name]["connections"] = connections
                        total_connections = sum([files[file].get("connections", 0) for file in files])
                        write_test_log(f"file: {file_name} node: {node}"
                                       f" connections: {connections} type: {msg['topic']} "
                                       f"total: {total_connections}")

    except KeyboardInterrupt:
        write_test_log(f"Keyboard interrupt received")
