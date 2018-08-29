"""Function for reading RIAPS hosts config
"""
import yaml

if __name__ == '__main__':
    stream = open('riaps_testing_config.yml', 'r')
    config = yaml.load(stream)
    stream.close()
    hosts = config['hosts']
    num_hosts = len(hosts)
    
    output = ''
    for x in range(num_hosts):
        output += hosts[x]
        if x != (num_hosts - 1):
            output += ','
    print(output)