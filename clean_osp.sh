#!/bin/bash -
#===============================================================================
#
#          FILE: clean_osp.sh
#
#         USAGE: ./clean_osp.sh
#
#   DESCRIPTION: This shell script takes the probe_osp.py output and attempts
#                to delete the 
#
#       OPTIONS: ---
#  REQUIREMENTS: probe_osp.py installed and functioning, and bash installed
#                probe_osp.py must have been run with the -c option and
#                must have output data files for cleaning in the targetted
#                directory
#          BUGS: Deletion hierarchy in OSP is not always straightforward
#         NOTES: ---
#        AUTHOR: John Apple II (JAII), jappleii@redhat.com
#  ORGANIZATION: GPS
#       CREATED: 28/08/23 14:25:38
#      REVISION: 001
#===============================================================================

set -o nounset                                  # Treat unset variables as an error

function usage {
  file=$(basename "$0")
  echo "$file usage: "
  echo "  [ -c directory containing the osprobe cleanup data ]"
  echo ""
  exit 1
}

while [[ $# -gt 1 ]]
do
    key="$1"
    case $key in
      -c)
      clean_data_directory="$2"
      shift
      ;;
      *)
      usage
      shift
      ;;
  esac
  shift
done


if [ ! -d "${clean_data_directory}" ] ; then
  echo "clean data directory option \"${clean_data_directory}\" is not a directory"
  usage
fi

if [ -e "${clean_data_directory}/users.osprobe.cleanup" ] ; then  
  xargs -a "${clean_data_directory}/users.osprobe.cleanup" -n 10 openstack user delete
fi

if [ -e "${clean_data_directory}/fips.osprobe.cleanup" ] ; then  
  xargs -a "${clean_data_directory}/fips.osprobe.cleanup" -n 1 openstack floating ip delete
fi

if [ -e "${clean_data_directory}/trunks.osprobe.cleanup" ] ; then
  while read -r port; do 
    mytrunk=''
    mytrunk=$(openstack port show "$port" | grep trunk_details | tr '|' ' ' | sed -e 's/trunk_details//' -e 's/^[ ]\+//' -e 's/[ ]\+$//');
    if [ "$mytrunk" == "None" ]; then     
      openstack port delete "$port";   
    else     
      mytrunkport=$(echo "$mytrunk" | sed -e "s/'/\"/g" | jq -r .trunk_id );
      openstack network trunk delete "$mytrunkport";     
      openstack port delete "$port";   
    fi
  done < <(cat "${clean_data_directory}/trunks.osprobe.cleanup")
fi
  
if [ -e "${clean_data_directory}/vms.osprobe.cleanup" ] ; then  
  xargs -a "${clean_data_directory}/vms.osprobe.cleanup" -n 2 openstack server delete
fi

if [ -e "${clean_data_directory}/security_groups.osprobe.cleanup" ] ; then  
  xargs -a "${clean_data_directory}/security_groups.osprobe.cleanup" -n 10 openstack security group delete
fi

if [ -e "${clean_data_directory}/ports.osprobe.cleanup" ] ; then  
  xargs -a "${clean_data_directory}/ports.osprobe.cleanup" -n 10 openstack port delete
fi

if [ -e "${clean_data_directory}/routers.osprobe.cleanup" ] ; then  
  while read -r r; do
    openstack router unset --external-gateway "$r"
    raw_data=$(openstack router show "$r" | grep interfaces_info | grep subnet_id | cut -f 3 -d '|')
    subnet_ids=$(echo "$raw_data" | jq -r '.[] | .subnet_id')
    while read -r d; do
      openstack router remove subnet "$r" "$d"
    done < "$subnet_ids"
  done
fi

if [ -e "${clean_data_directory}/subnets.osprobe.cleanup" ] ; then  
  xargs -a "${clean_data_directory}/subnets.osprobe.cleanup" -n 10 openstack subnet delete
fi

if [ -e "${clean_data_directory}/networks.osprobe.cleanup" ] ; then  
  xargs -a "${clean_data_directory}/networks.osprobe.cleanup" -n 10 openstack network delete
fi

if [ -e "${clean_data_directory}/stacks.osprobe.cleanup" ] ; then  
  xargs -a "${clean_data_directory}/stacks.osprobe.cleanup" -n 5 openstack stack delete -y
fi

