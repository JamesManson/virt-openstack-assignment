import argparse

import openstack

conn = openstack.connect()

def create():
    
    IMAGE = 'ubuntu-16.04-x86_64'#identifying resources needed 
    FLAVOUR = 'c1.c1r1'
    NETWORK = 'private-net'
    KEYPAIR = 'mansjc2-key'
    
    image = conn.compute.find_image(IMAGE)
    flavor = conn.compute.find_flavor(FLAVOUR)
    network = conn.network.find_network(NETWORK)
    keypair = conn.compute.find_keypair(KEYPAIR)
    
    print("Launching Instance 1:")#creating web server
	SERVER = 'mansjc2-web'
	server = conn.compute.create_server(
		name=SERVER, image_id=image.id, flavor_id=flavour.id,
		networks=[{"uuid": network.id}], key_name=keypair.name)
        
    server = conn.compute.wait_for_server(server)
    
    print("Launching Instance 2:")#creating app server
	SERVER = 'mansjc2-app'
	server = conn.compute.create_server(
		name=SERVER, image_id=image.id, flavor_id=flavour.id,
		networks=[{"uuid": network.id}], key_name=keypair.name)
        
    server = conn.compute.wait_for_server(server)
    
    print("Launching Instance 3:")#creating db server
	SERVER = 'mansjc2-db'
	server = conn.compute.create_server(
		name=SERVER, image_id=image.id, flavor_id=flavour.id,
		networks=[{"uuid": network.id}], key_name=keypair.name)
        
    server = conn.compute.wait_for_server(server)
        
    print("Creating Network:")#creating network and passing name
	NAME = 'mansjc2-net'
	network = conn.network.create_network(
		name=NAME)
	print(network)
	
	print("Creating Subnet:")#create subnet for the network 
	NAME = 'mansjc2-subnet'
	subnet = conn.network.create_subnet(
		name=NAME,
		network_id=NETWORK,
		ip_version='4',
		cidr='192.168.50.0/24',
		gateway_ip='192.168.50.1')
	print(subnet)
	
	print("Creating Router:")#creating router and associating subnet
	NAME = 'mansjc2-rtr'
	router = conn.router.create_router(
		name=NAME, 
		router_subnet='mansjc2-subnet'
		)
	
	print("Associate Floating IP")
	public_net = conn.network.find_network('public_net')#accessing public network and retrive ip address from it
	floating_ip = conn.network.create_ip(floating_network_id=public_net.id)
	conn.compute.add_floating_ip_to_server(server, floating_ip.floating_ip_address)#associating our floating ip address to with the server
	
    
    
	
	
	
    pass



def run():

    conn.compute.start_server('mansjc2-web')#starting servers
	conn.compute.start_server('mansjc2-app')
    conn.compute.start_server('mansjc2-db')
    
    pass



def stop():

    conn.compute.stop_server('mansjc2-web')#stopping servers
    conn.compute.stop_server('mansjc2-app')
    conn.compute.stop_server('mansjc2-db')

    pass



def destroy():

    print("Delete Network:")

    network = conn.network.find_network(
        'mansjc2-net')#find network by name

    for mansjc2-subnet in network.subnet_ids:
        conn.network.delete_subnet(mansjc2-subnet, ignore_missing=False)#delete subnet for network
		conn.network.delete_network(mansjc2-net, ignore_missing=False)#delete network

    print("Delete Router:")
    
    router = conn.compute.find_router(
        'mansjc2-rtr')#find router by name
        
    for mansjc2-router in router.router_ids:
        conn.compute.delete_router(mansjc2-router, ignore_missing=False)#delete router
        
    print("Delete Server:")

    server = conn.compute.find_server(
        'mansjc2-web')#find web server
       
    for mansjc2-web in server.server_ids:
        conn.compute.delete_server(mansjc2-web, ignore_missing=False)#delete web server
     
    server = conn.compute.find_server(
        'mansjc2-app')#find app server
       
    for mansjc2-app in server.server_ids:
        conn.compute.delete_server(mansjc2-app, ignore_missing=False)#delete app server
    
    server = conn.compute.find_server(
        'mansjc2-db')#find db server
       
    for mansjc2-db in server.server_ids:
        conn.compute.delete_server(mansjc2-db, ignore_missing=False)#delete db server
        
    pass



def status():

    conn.compute.get_server_metadata('mansjc2-web')#get metadata for web server
    conn.compute.get_server_metadata('mansjc2-app')#get metadata for app server
    conn.compute.get_server_metadata('mansjc2-db')#get metadata for db server

    pass





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