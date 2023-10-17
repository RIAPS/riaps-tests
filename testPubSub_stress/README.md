parse logs to see the number of connections made:
```bash
grep -r "connections\": 6" server_logs | wc -l
```

To see which connections are known to a specific node:
```bash
grep -r "connections\": 6" server_logs/<file_name>
```