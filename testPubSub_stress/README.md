If the tests are being run with pytest then the RIAPS test suite must be installed.
https://github.com/RIAPS/test_suite
as well as (watchdog)[https://pypi.org/project/watchdog/].

parse logs to see the number of connections made:
```bash
grep -r "connections\": 6" server_logs | wc -l
```

To see which connections are known to a specific node:
```bash
grep -r "connections\": 6" server_logs/<file_name>
```

