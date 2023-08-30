#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
name:             :probe_osp.py
description       :checks openstack resources for valid(existing) project id.
author            :yvarbev@redhat.com
release           :22/07
version           :0.1
"""
import argparse

cleanup_files = [
    "users.osprobe.cleanup",
    "fips.osprobe.cleanup",
    "networks.osprobe.cleanup",
    "ports.osprobe.cleanup",
    "routers.osprobe.cleanup",
    "subnets.osprobe.cleanup",
    "stacks.osprobe.cleanup",
    "trunks.osprobe.cleanup",
    "vms.osprobe.cleanup",
    "security_groups.osprobe.cleanup"]

parser = argparse.ArgumentParser(description='Options for probe_osp.py')
parser.add_argument('-c', '--cleanup', help='creates individual resource files in the target directory', required=False, type=str, dest='directory')
args = parser.parse_args()

if args.directory:
    cleanup_bool = True
    print(f"Cleanup files: {cleanup_bool}")
    import os
    for file in cleanup_files:
        filename = f"{args.directory}/{file}"
        if os.path.exists(filename):
            print(f"removing stale file {filename}")
            os.remove(filename)
else:
    cleanup_bool = False


def _connect(cloud):
    import openstack
    import os
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


def _projects(cloud):
    return [project.id for project in _connect(cloud).identity.projects()]


def probe_users(cloud):
    projects = _projects(cloud)
    users = _connect(cloud).list_users()
    xU = []
    sU = []
    for user in users:
        if user.default_project_id not in projects:
            if user.email is None:
                xU.append(user.name)
            else:
                sU.append(user.name)
    print('Users:')
    print(len(xU), 'users with no valid project id or email')
    if cleanup_bool and len(xU) > 0:
        filename = f"{args.directory}/users.osprobe.cleanup"
        f = open(filename, 'w')
        for item in xU:
            f.write(item + "\n")
        f.close
    print(*xU)
    print(len(sU), 'users with no valid project id but have email (service users?)')
    print(*sU)
    print('~ End ~\n')


def probe_stacks(cloud):
    stacks = _connect(cloud).list_stacks()
    failed_stacks = []
    for stack in stacks:
        if 'FAILED' in stack.status:
            failed_stacks.append(stack.id)
            print('Stacks:')
            print('{}, {}, {}'.format(stack.status, stack.name, stack.status_reason))
            print('~ End ~\n')
    if cleanup_bool:
        if len(failed_stacks) > 0:
            filename = f"{args.directory}/stacks.osprobe.cleanup"
            f = open(filename, 'w')
            for item in failed_stacks:
                f.write(item + "\n")
            f.close


def probe_network(cloud):
    projects = _projects(cloud)
    networks = _connect(cloud).list_networks()
    subnets = _connect(cloud).list_subnets()
    fips = _connect(cloud).list_floating_ips()
    routers = _connect(cloud).list_routers()
    ports = _connect(cloud).list_ports()
    resources = {'networks': networks, 'subnets': subnets, 'fips': fips, 'routers': routers, 'ports': ports}
    N = {'networks': [], 'subnets': [], 'fips': [], 'routers': [], 'ports': [], 'trunks': []}
    for rtype in resources:
        for resource in resources[rtype]:
            if resource.project_id not in projects:
                if 'trunk_details' in resource and resource['trunk_details']:
                    N['trunks'].append(resource)
                else:
                    N[rtype].append(resource)
    if any(N.values()):
        print('Network:')
        for rtype in N:
            if len(N[rtype]) > 0:
                if cleanup_bool:
                    filename = f"{args.directory}/{rtype}.osprobe.cleanup"
                    f = open(filename, 'w')
                    for item in N[rtype]:
                        f.write(item.id + "\n")
                    f.close
                print('{} {} with no valid project id'.format(len(N[rtype]), rtype))
                print(rtype)
                print(*[n.id for n in N[rtype]])
                print('~ End ~\n')


def probe_compute(cloud):
    projects = _projects(cloud)
    vms = _connect(cloud).list_servers(all_projects=True)
    sgs = _connect(cloud).list_security_groups()
    xVM = []
    xSG = []
    for vm in vms:
        if vm.project_id not in projects:
            xVM.append(vm)
    for sg in sgs:
        if sg.project_id not in projects:
            xSG.append(sg)
    if cleanup_bool:
        if len(xVM) > 0:
            filename = f"{args.directory}/vm.osprobe.cleanup"
            f = open(filename, 'w')
            for item in xVM:
                f.write(item.id + "\n")
            f.close
        if len(xSG) > 0:
            filename = f"{args.directory}/security_groups.osprobe.cleanup"
            f = open(filename, 'w')
            for item in xSG:
                f.write(item.id + "\n")
            f.close
    print('Compute:')
    print(len(xVM), 'vms with no valid project id')
    print(*[x.id for x in xVM])
    print(len(xSG), 'security groups with no valid project id')
    print(*[x.id for x in xSG])
    print('~ End ~\n')


def runner(cloud):
    if cloud:
        print('Probing cloud: {}'.format(cloud))
    probe_users(cloud)
    probe_stacks(cloud)
    probe_network(cloud)
    probe_compute(cloud)


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
