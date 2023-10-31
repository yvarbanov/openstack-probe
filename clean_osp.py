#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
name:             :clean_osp.py
description       :cleans iteps created by probe_osp.py
author            :jappleii@redhat.com
release           :23/10
version           :0.1
"""
import argparse
import openstack
import os
import yaml

# cleanup_files = [
#    "users.osprobe.cleanup",
#    "fips.osprobe.cleanup",
#    "networks.osprobe.cleanup",
#    "ports.osprobe.cleanup",
#    "routers.osprobe.cleanup",
#    "subnets.osprobe.cleanup",
#    "stacks.osprobe.cleanup",
#    "trunks.osprobe.cleanup",
#    "vms.osprobe.cleanup",
#    "security_groups.osprobe.cleanup"]


parser = argparse.ArgumentParser(description='Clean up OSP data')
parser.add_argument('-c', '--clean-directory', help='Directory containing the probe_osp.py cleanup data', required=True, type=str, dest='directory')
parser.add_argument('-d', '--debug', help='Print debug information instead of being silent', action="store_true", dest='debug')
args = parser.parse_args()

clean_directory = args.directory

if args.directory:
     clean_directory = args.directory
else:
    print('Please specify the directory containing the osprobe cleanup data')
    exit(1)
# clean_directory = "/tmp"
def _connect(cloud):
    if os.getenv('OS_CLIENT_CONFIG_FILE'):
        return openstack.connection.Connection(cloud=cloud)
    else:
        server = os.getenv('OS_AUTH_URL')
        project = os.getenv('OS_PROJECT_NAME')
        username = os.getenv('OS_USERNAME')
        password = os.getenv('OS_PASSWORD')
        return openstack.connection.Connection(
            auth=dict(
                auth_url=server,
                project_name=project,
                username=username,
                password=password,
                project_domain_name="Default",
                user_domain_name="Default"),
            identity_api_version=3,
            region_name="regionOne",
        )

def delete_users(directory, cloud_connection):
    """This function takes a directory path and an existing Openstack connection and deletes the user ID from directory/users.osprobe.cleanup"""
    if os.path.exists(os.path.join(directory, 'users.osprobe.cleanup')):
        with open(os.path.join(directory, 'users.osprobe.cleanup'), 'r') as f:
            lines = f.readlines()
            for line in lines:
                clean_line=line.replace('\n', '')
                try:
                    if args.debug:
                        print(f"searching for user {clean_line}\n") if args.debug else 0
                    userid = cloud_connection.identity.find_user(clean_line).id
                    try:
                        if args.debug:
                            print(f"deleting user {clean_line}\n")
                        cloud_connection.identity.delete_user(userid)
                    except Exception as e:
                        if args.debug:
                            print(f"user unable to delete: {e}\n")
                except Exception as e:
                    if args.debug:
                        print(f"user {clean_line} not found: {e}\n")
    else:
        if args.debug:
            print("No user deletion file found, skipping\n")

def delete_vms(directory, cloud_connection):
    """This function takes a directory path and an existing Openstack connection and deletes the vm ID from directory/vms.osprobe.cleanup"""
    if os.path.exists(os.path.join(directory, 'vms.osprobe.cleanup')):
        with open(os.path.join(directory, 'vms.osprobe.cleanup'), 'r') as f:
            lines = f.readlines()
            for line in lines:
                clean_line=line.replace('\n', '')
                try:
                    if args.debug:
                        print(f"deleting vm {clean_line}\n")
                    cloud_connection.compute.delete_server(clean_line)
                except Exception as e:
                    if args.debug:
                        print(f"vm {clean_line} unable to delete: {e}\n") 
    else:
        if args.debug:
            print("No vm deletion file found, skipping\n")
        
def delete_fips(directory, cloud_connection):
    """This function takes a directory path and an existing Openstack connection and deletes the floating ip ID from directory/fips.osprobe.cleanup"""
    if os.path.exists(os.path.join(directory, 'fips.osprobe.cleanup')):
        with open(os.path.join(directory, 'fips.osprobe.cleanup'), 'r') as f:
            lines = f.readlines()
            for line in lines:
                clean_line=line.replace('\n', '')
                try:
                    if args.debug:
                        print(f"deleting floating ip {clean_line}\n")
                    cloud_connection.network.delete_ip(clean_line)
                except Exception as e:
                    if args.debug:
                        print(f"floating ip {clean_line} unable to delete: {e}\n") 
    else:
        if args.debug:
            print("No fip deletion file found, skipping\n")


def delete_trunks(directory, cloud_connection):
    """This function takes a directory path and an existing Openstack connection and deletes the trunk ID from directory/trunks.osprobe.cleanup"""
    if os.path.exists(os.path.join(directory, 'trunks.osprobe.cleanup')):
        with open(os.path.join(directory, 'trunks.osprobe.cleanup'), 'r') as f:
            lines = f.readlines()
            for line in lines:
                clean_line=line.replace('\n', '')
                try:
                    my_trunk_id = cloud_connection.network.get_port(clean_line).trunk_details["trunk_id"]
                    if args.debug:
                        print(f"deleting trunk {clean_line}\n")
                        if my_trunk_id:
                            print(f"Trunk ID for port {clean_line} is {my_trunk_id}\n")
                        else:
                            print(f"No Trunk ID for port {clean_line}\n")
                    if my_trunk_id:
                        cloud_connection.network.delete_trunk(my_trunk_id)
                        cloud_connection.network.delete_port(clean_line)
                except Exception as e:
                    if args.debug:
                        print(f"trunk {clean_line} unable to delete: {e}\n") 
    else:
        if args.debug:
            print("No trunk deletion file found, skipping\n")

    
def delete_ports(directory, cloud_connection):
    """This function takes a directory path and an existing Openstack connection and deletes the port ID from directory/ports.osprobe.cleanup"""
    if os.path.exists(os.path.join(directory, 'ports.osprobe.cleanup')):
        with open(os.path.join(directory, 'ports.osprobe.cleanup'), 'r') as f:
            lines = f.readlines()
            for line in lines:
                clean_line=line.replace('\n', '')
                try:
                    if args.debug:
                        print(f"deleting port {clean_line}\n")
                    cloud_connection.network.delete_port(clean_line)
                except Exception as e:
                    if args.debug:
                        print(f"port {clean_line} unable to delete: {e}\n") 
    else:
        if args.debug:
            print("No port deletion file found, skipping\n")


def delete_networks(directory, cloud_connection):
    """This function takes a directory path and an existing Openstack connection and deletes the network ID from directory/networks.osprobe.cleanup"""
    if os.path.exists(os.path.join(directory, 'networks.osprobe.cleanup')):
        with open(os.path.join(directory, 'networks.osprobe.cleanup'), 'r') as f:
            lines = f.readlines()
            for line in lines:
                clean_line=line.replace('\n', '')
                try:
                    if args.debug:
                        print(f"deleting network {clean_line}\n")
                    cloud_connection.network.delete_network(clean_line)
                except Exception as e:
                    if args.debug:
                        print(f"network {clean_line} unable to delete: {e}\n") 
    else:
        if args.debug:
            print("No network deletion file found, skipping\n")


def delete_subnets(directory, cloud_connection):    
    """This function takes a directory path and an existing Openstack connection and deletes the subnet ID from directory/subnets.osprobe.cleanup"""
    if os.path.exists(os.path.join(directory, 'subnets.osprobe.cleanup')):
        with open(os.path.join(directory, 'subnets.osprobe.cleanup'), 'r') as f:
            lines = f.readlines()
            for line in lines:
                clean_line=line.replace('\n', '')
                try:
                    if args.debug:
                        print(f"deleting subnet {clean_line}\n")
                    cloud_connection.network.delete_subnet(clean_line)
                except Exception as e:
                    if args.debug:
                        print(f"subnet {clean_line} unable to delete: {e}\n") 
    else:
        if args.debug:
            print("No subnet deletion file found, skipping\n")
        
        
def delete_routers(directory, cloud_connection):
    """This function takes a directory path and an existing Openstack connection and attempts to delete the router ID from directory/routers.osprobe.cleanup"""
    if os.path.exists(os.path.join(directory, 'routers.osprobe.cleanup')):
        with open(os.path.join(directory, 'routers.osprobe.cleanup'), 'r') as f:
            lines = f.readlines()
            for line in lines:
                clean_line=line.replace('\n', '')
                try:
                    router = cloud_connection.network.get_router(clean_line)
                    if router:
                        router_id = router.id
                        if args.debug:
                            print(f"Beginning deleting surrounding router information for router: {clean_line}\n")
                        if router.external_gateway_info:
                            if args.debug:
                                print(f"Removing Router external_gateway\n")
                            cloud_connection.network.remove_gateway_from_router(clean_line)
                        # Now we have to cycle through the interfaces just like the openstack cli does
                        if args.debug:
                            print(f"Removing Router subnet attachments\n")
                        filters = {}
                        filters['device_id'] = router_id                       
                        for port in list(cloud_connection.network.ports(**filters)):
                            if port.device_owner != "network:router_gateway":
                                my_portid = port.id
                                if args.debug:
                                    print(f"Found attachment outside of gatewayport: port {my_portid}\n")
                                for ip_spec in port.fixed_ips:
                                    my_subnetid = ip_spec.get('subnet_id')
                                    if args.debug:
                                        print(f"Removing Router subnet attachment: port {my_portid} subnet {my_subnetid}\n")
                                    cloud_connection.network.remove_interface_from_router(router_id, my_subnetid, my_portid)
                    if args.debug:
                        print(f"Directly remove the router {router_id}\n")
                    cloud_connection.network.delete_router(router)
                except Exception as e:
                    if args.debug:
                        print(f"router {clean_line} unable to delete: {e}\n") 
    else:
        if args.debug:
            print("No router deletion file found, skipping\n")
    
def delete_stacks(directory, cloud_connection):
    """This function takes a directory path and an existing Openstack connection and deletes the stack ID from directory/stacks.osprobe.cleanup"""
    if os.path.exists(os.path.join(directory, 'stacks.osprobe.cleanup')):
        with open(os.path.join(directory, 'stacks.osprobe.cleanup'), 'r') as f:
            lines = f.readlines()
            for line in lines:
                clean_line=line.replace('\n', '')
                try:
                    if args.debug:
                        print(f"deleting stack {clean_line}\n")
                    cloud_connection.orchestration.delete_stack(clean_line)
                except Exception as e:
                    if args.debug:
                        print(f"stack {clean_line} unable to delete: {e}\n")     
    else:
        if args.debug:
            print("No stack deletion file found, skipping\n")    
   
   
    
def delete_security_groups(directory, cloud_connection):
    """This function takes a directory path and an existing Openstack connection and deletes the security group ID from directory/security_groups.osprobe.cleanup"""
    if os.path.exists(os.path.join(directory, 'security_groups.osprobe.cleanup')):
        with open(os.path.join(directory, 'security_groups.osprobe.cleanup'), 'r') as f:
            lines = f.readlines()
            for line in lines:
                clean_line=line.replace('\n', '')
                try:
                    if args.debug:
                        print(f"deleting security_group {clean_line}\n")
                    cloud_connection.network.delete_security_group(clean_line)
                except Exception as e:
                    if args.debug:
                        print(f"security_group {clean_line} unable to delete: {e}\n")     
    else:
        if args.debug:
            print("No security_group deletion file found, skipping\n")        
    


def runner(cloud):
    if cloud:
        if args.debug:
            print('Probing cloud: {}'.format(cloud))
    connection = _connect(cloud)
    delete_users(clean_directory, connection)
    delete_vms(clean_directory, connection)
    delete_fips(clean_directory, connection)
    delete_trunks(clean_directory, connection)
    delete_ports(clean_directory, connection)
    delete_routers(clean_directory, connection)
    delete_subnets(clean_directory, connection)
    delete_networks(clean_directory, connection)
    delete_security_groups(clean_directory, connection)
    delete_stacks(clean_directory, connection)
    
    

def main():
    import os
    import yaml
    if os.getenv('OS_CLIENT_CONFIG_FILE'):
        with open(os.getenv('OS_CLIENT_CONFIG_FILE')) as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
        clouds = [*data['clouds'].keys()]
        for cloud in clouds:
            runner(cloud)
    else:
        runner(None)


if __name__ == "__main__":
    main()
