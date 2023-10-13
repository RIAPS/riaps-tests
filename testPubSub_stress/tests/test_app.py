import pathlib
import pytest
import time

import riaps.test_suite.test_api as test_api


# --------------- #
# -- Config -- #
# --------------- #
vanderbilt_config = {"VM_IP": "172.21.20.70",
                     "app_folder_path": pathlib.Path(__file__).parents[1],
                     "app_file_name": "stress.riaps",
                     "depl_file_name": "stress_vu.depl"}

ncsu_config = {"VM_IP": "192.168.10.106",
               "app_folder_path": pathlib.Path(__file__).parents[1],
               "app_file_name": "stress.riaps",
               "depl_file_name": "stress_ncsu.depl"}

configs = {"vu": vanderbilt_config,
           "ncsu": ncsu_config}

test_cfg = configs["ncsu"]

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
    print(f"client list: {client_list}")

    controller, app_name = test_api.launch_riaps_app(
        app_folder_path=app_folder_path,
        app_file_name=app_file_name,
        depl_file_name=depl_file_name,
        database_type="dht",
        required_clients=client_list
    )

    input("Press a key to terminate the app\n")
    test_api.terminate_riaps_app(controller, app_name)
    print(f"Test complete at {time.time()}")