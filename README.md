# riaps-tests
Repository for code used to test the riaps-platform

Tests in master branch are ready to be automated, tests being written are in their own branches.

## Running tests
1. Install necessary python modules
```
pip install pytest pyaml paramiko
```
2. Edit `riaps_testing_config.yml` to match your BBB hosts and testing configuration.
3. Call pytest from inside the repository
```
git clone https://github.com/RIAPS/riaps-tests.git
cd riaps-tests
pytest
```
Optional: Tell pytest to generate a junit xml file. This can easily be passed to Jenkins to generate a nice test report.
```
pytest --junitxml=results.xml
```

## Test format
Pytest will automatically search in any subdirectories below the intial directory for python modules prefixed with `test_`. In any matching modules, it will search for any methods prefixed with `test_` or suffixed with `_test`. Each matching method becomes it's own test. Pytest will call these methods one after another, recording the results. A test is considered failed if it throws any exceptions. Assert statements should be frequently used to verify the test progress.
Tests can import the `riaps_testing` module, which contains the `runTest(...)` method. This method can be passed .riaps and .depl files to automatically run RIAPS applications across BBB hosts. Tests can additionally implement any other helper methods to simplify the testing process, as long as the method name doesn't match the test format.
### riaps and depl file formats
`runTest(...)` will automatically substitute any keywords found in riaps and depl files to help automate testing. These keywords are optional, but provide greater reusability across configurations.
```
Keywords
NAME: The name of the running application. This allows files to be reused across multiple tests.
HOST: A hostname on which to run an application actor. Each instance of the keyword will be replaced with a unique host.
```
