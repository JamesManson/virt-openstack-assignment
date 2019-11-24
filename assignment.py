import argparse
import time
import openstack

IMAGE = 'ubuntu-16.04-x86_64' #identifying resources needed 
FLAVOUR = 'c1.c1r1'
NETWORK = 'mansjc2-net'
KEYPAIR = 'mansjc2-key'
SUBNET = 'mansjc2-subnet'
ROUTER = 'mansjc2-router'
SECURITYGROUP = 'mansjc2-group'
SERVER1 = 'mansjc2-web'
SERVER2 = 'mansjc2-app'
SERVER3 = 'mansjc2-db'

conn = openstack.connect(cloud_name='openstack') #connect to openstack  

def create():
    
    image = conn.compute.find_image(IMAGE) 
    flavour = conn.compute.find_flavor(FLAVOUR)
    network = conn.network.find_network(NETWORK)
    keypair = conn.compute.find_keypair(KEYPAIR)
    router = conn.network.find_router(ROUTER)
    security_group = conn.network.find_security_group(SECURITYGROUP)
    server_list = [SERVER1,SERVER2,SERVER3]
    
    if not network: #if there is no network found, create one
        print("Creating network") 
        network = conn.network.create_network(name=NETWORK)
        print("Creating subnet") 
        subnet = conn.network.create_subnet(
            name=SUBNET,
            network_id=network.id,
            ip_version='4',
            cidr='192.168.50.0/24'
            gateway_ip='192.168.50.1')
        print("Network has been created")
    else:
        print("Network aleady found") 
        
        
    if not router: #if there is no router found, create one
        print("Creating router")
        attrs = {"name" : ROUTER, "external_gatewat_info" : {"network_id" : conn.network.find_network("public-net").id}}
        router = conn.network.create_router(**attrs)
        conn.network.add_interface_to_router(router, subnet_id=conn.network.find_network(NETWORK).subnet_ids[0])
        print("Router has been created")
    else:
        print("Router already found") 

    
    for name in server_list:
        server = conn.compute.find_server(name)
        if not server: #if there is no server found, create one
            print("Creating " + name + " server")
            server = conn.compute.create_server(name=name, image_id=image.id, flavor_id=flavour.id, networks=[{"uuid": network.id}],
            server = conn.compute.wait_for_server(server)
            conn.compute.add_security_group_to_server(server, security_group)
            if name is server_list[0]:
                floatingIP = conn.network.create_ip(floating_network_id=conn.network.find_network('public-net').id)
                conn.compute.add_floating_ip_to_server(server, address=floating_ip.floating_ip_address)
            print("Server " + name + " has been created")
        else:
            print("Server already found")


def run():

    for name in server_list: #start server if not already active
        server = conn.compute.find_server(name)
        if not server:
            print(name + " server was not found")
        else:
            server = conn.compute.get_server(server)
            if server.status == "SHUTOFF":
                conn.compute.start_server(server)
                print(name + " is now active")
            else: 
                print(name + " is already active")


def stop():

    for name in server_list: #stop servers if not already inactive
        server = conn.compute.find_server(name)
        if not server:
            print(name + " server was not found")
        else:
            server = conn.compute.get_server(server)
            if server.status == "ACTIVE":
                conn.compute.stop_server(server)
                print(name + " is now inactive")
            else:
                print(name + " is already inactive")


def destroy():

    router = conn.network.find_router(ROUTER) 
    network = conn.network.find_network(NETWORK)
    subnet = conn.network.find_subnet(SUBNET)

    for name in server_list: #delete servers if exists.
        server = conn.compute.find_server(name)
        if not server:
            print(name + " server was not found")
        else:
            conn.compute.delete_server(server)
            print(name + " server has been deleted")
    
    time.sleep(10) #wait for servers to be deleted"
    
    if not router: #delete router if exists
        print("Router does not exist")
    else:
        conn.network.delete_router(router)
        print("Router has been deleted")
        
    if not subnet: #delete subnet if exists
        print("Subnet does not exist")
    else:
        conn.network.delet_subnet(subnet)
        print("Subnet has been deleted")
      
    if not network: #deleted network if exists
        print("Network does not exist")
    else:
        conn.network.delet_network(network)
        print("Network has been deleted")
    

def status():
    
    for name in server_list: #get status of each server
        server = conn.compute.find_server(name)
        if not server:
            print(name + " server does not exist")
        else:
            server = conn.compute.get_server(server)
            status = server.status
            print(name + " currently " + server.status)





### You should not modify anything below this line ###

if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument('operation',

                        help='One of "create", "run", "stop", "destroy", or "status"')

    args = parser.parse_args()

    operation = args.operation



    operations = {

        'create'  : create,

        'run'     : run,

        'stop'    : stop,

        'destroy' : destroy,

        'status'  : status

        }



    action = operations.get(operation, lambda: print('{}: no such operation'.format(operation)))

    action()