import redis
import time
host = "192.168.10.106"
port = "6379"
r = redis.StrictRedis(host,port, db=0) # Connect

print(r)

key = "/NAME/p2pMsg/pub"
does_exist = r.exists(key)
print(does_exist)


clientsKey = key + "_clients"
clientsToNotify = r.smembers(clientsKey)
print(clientsToNotify)

value = "192.168.10.111:44249"
r.sadd(key,value)
