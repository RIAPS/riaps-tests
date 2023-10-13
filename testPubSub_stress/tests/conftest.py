import pytest

from riaps.test_suite.fixtures.remote_connection import fabric_group
from riaps.test_suite.fixtures.remote_connection import setup_remote_tmux
from riaps.test_suite.fixtures.LogServer import log_server, platform_log_server
from riaps.test_suite.fixtures.utils import test_logger
from riaps.test_suite.fixtures.pytest_logger import testslogger