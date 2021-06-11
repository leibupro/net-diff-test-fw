# ############################################################
#
#                              +
#                 ---====D                        @
#        o                    *
#                     *              o
#             |
#            -O-                         =( =         +
#       +     |                   *
#                    ____     ________
#                   /  _/__  / __/ __/    .
#                  _/ // _ \/ _/_\ \             +  .
#         *       /___/_//_/___/___/             |
#                                        -O-         @
#       +                                |
#                       *
#                    ,      .
#            .    `
#        @                +    `~---~~`           *
#
#                    *       .            o         +
#
#
#    File:         vswitch.bash
#
#
#    Purpose:      This bash script controls
#                  the set up / tear down
#                  of a virtual switch.
#                  The virtual switch gets set
#                  with n ports and n virtual
#                  ethernet devices. The
#                  virtual ethernet devices
#                  are then connected to the
#                  virtual switch.
#
#
#    Remarks:      - Run this script as sudoer.
#
#                  - Dependencies:
#                    * Bourne again shell (bash)
#                    * getopts
#                    * openvswitch package
#                      (arch linux)
#                    * openvswitch-switch package
#                      (debian)
#                    * ip command
#                    * sysctl
#
#                  - We want to avoid unfeasible
#                    protocols, therefore we proudly
#                    disable IPv6 here.
#
#                  - The link speed of virtual
#                    network interfaces can not
#                    be set or alterd.
#
#                  - The switch port interfaces have
#                    to operate in promiscuous mode.
#
#
#    Assumption:   path variable is set.
#                  -> no need to specify the full
#                     paths to the binaries ...
#
#
#    Author(s):    P. Leibundgut <leiu@zhaw.ch>
#
#
#    Date:         12/2020
#
#
# ############################################################


# in the environment file all the global constants
# are stored at a single place.
source ./vnetenv

# distribution dependent globals
vswitch_service=""


print_usage() {
  printf "usage, e.g.: sudo bash ./${0} -s\n\
             sudo bash ./${0} -t\n\
             sudo bash ./${0} -u 2\n\
             sudo bash ./${0} -d 6\n" >&2
}


init_distro_deps(){
  if [ -f /etc/debian_version ]; then
    vswitch_service="openvswitch-switch.service"
  elif [ -f /etc/arch-release ]; then
    vswitch_service="ovs-vswitchd.service"
  else
    printf "Distribution not yet considered.\n" >&2
    exit 1
  fi
}


port_no_in_range(){

  if [[ ${1} -ge ${MIN_PORTS} && \
        ${1} -le ${MAX_PORTS} ]]; then
    ret_val=1
  else
    ret_val=0
  fi
  return ${ret_val}
}


port_no_is_possible(){
  # count ports in virtual switch ...
  port_count=`ovs-vsctl list-ports ${BRIDGE_NAME} 2>&1 | \
              grep -n "${OVS_PORT_BASE_NAME}" | wc -l`

  if [[ ${1} -ge ${MIN_PORTS} && \
        ${1} -le ${port_count} ]]; then
    ret_val=1
  else
    ret_val=0
  fi
  return ${ret_val}
}


port_control(){
  port_no_is_possible ${1}
  if [ ${?} = 1 ]; then
    ip netns exec ns${1} ip link set dev ${VETH_BASE_NAME}${1} ${2}
    printf "Virtual ethernet port brought ${2}.\n" >&2
  else
    printf "Can't do anything here. Maybe wrong argument specified.\n" >&2
    exit 1
  fi
}


set_up(){
  port_no_in_range ${NO_PORTS}

  if [ ${?} = 1 ]; then
    printf "setting up virtual switch with ${NO_PORTS} ports.\n" >&2
    systemctl start ${vswitch_service}
    ovs-vsctl init
    printf "Adding bridge ...\n" >&2
    ovs-vsctl --may-exist add-br ${BRIDGE_NAME}
    for i in `seq 1 ${NO_PORTS}`;
    do
      ip netns add ns${i}
      ip link add ${VETH_BASE_NAME}${i} type veth peer name ${OVS_PORT_BASE_NAME}${i}
      ovs-vsctl add-port ${BRIDGE_NAME} ${OVS_PORT_BASE_NAME}${i}
      ip link set ${VETH_BASE_NAME}${i} netns ns${i}
      ip netns exec ns${i} ip link set dev ${VETH_BASE_NAME}${i} up
      ip link set dev ${OVS_PORT_BASE_NAME}${i} up
      ip link set ${OVS_PORT_BASE_NAME}${i} promisc on
      ip netns exec ns${i} ip addr add \
          ${IP_ADDR_BASE}${i}/${IP_NETMASK} dev ${VETH_BASE_NAME}${i}

      # disable IPv6 on both interfaces of the veth pair.
      sysctl -wq net.ipv6.conf.${OVS_PORT_BASE_NAME}${i}.disable_ipv6=1
      ip netns exec ns${i} sysctl -wq net.ipv6.conf.${VETH_BASE_NAME}${i}.disable_ipv6=1

      printf "\n\n*******************************************************************\n" >&2
      printf "Interfaces of net namespace: ns${i}:\n" >&2
      printf "*******************************************************************\n\n" >&2
      ip netns exec ns${i} ip a
    done

    printf "\n\n*******************************************************************\n" >&2
    printf "Interfaces of the host machine:\n" >&2
    printf "*******************************************************************\n\n" >&2
    sleep 1
    ip a
  else
    printf "You must be jokin\', ${NO_PORTS} ports?!?\n" >&2
    exit 1
  fi
}


tear_down(){
  # count ports in virtual switch ...
  port_count=`ovs-vsctl list-ports ${BRIDGE_NAME} 2>&1 | \
              grep -n "${OVS_PORT_BASE_NAME}" | wc -l`
  # Next two lines used during development of this script.
  # port_count=4
  # if [ 1 -eq 1 ]; then
  if [[ ${port_count} -ge ${MIN_PORTS} && \
        ${port_count} -le ${MAX_PORTS} ]]; then
    printf "virtual switch is being destroyed now.\n" >&2
    printf "Port Count: ${port_count}\n" >&2
    for i in `seq 1 ${port_count}`;
    do
      ip netns exec ns${i} ip addr del \
          ${IP_ADDR_BASE}${i}/${IP_NETMASK} dev ${VETH_BASE_NAME}${i}
      ip link set dev ${OVS_PORT_BASE_NAME}${i} down
      ip netns exec ns${i} ip link set dev ${VETH_BASE_NAME}${i} down
      ovs-vsctl del-port ${BRIDGE_NAME} ${OVS_PORT_BASE_NAME}${i}

      # this deletes the net namespace.
      # it implies the veth link down and link deletion of
      # the virtual ethernet device.
      ip netns del ns${i}
    done
    printf "Deleting bridge ...\n" >&2
    ovs-vsctl --if-exists del-br ${BRIDGE_NAME}
    systemctl stop ${vswitch_service}

    printf "\n\n*******************************************************************\n" >&2
    printf "Network interfaces after vswitch removal:\n" >&2
    printf "*******************************************************************\n\n" >&2
    sleep 1
    ip a
  else
    printf "tear down: nothing to do here.\n" >&2
    exit 1
  fi
}


enable_port(){
  port_control ${1} up
}


disable_port(){
  port_control ${1} down
}


main(){
  init_distro_deps
  while getopts ":stu:d:" opt; do
    case ${opt} in
      s)
        set_up
        exit 0
        ;;
      t)
        tear_down
        exit 0
        ;;
      u)
        enable_port ${OPTARG}
        exit 0
        ;;
      d)
        disable_port ${OPTARG}
        exit 0
        ;;
      \?)
        printf "Invalid option: -${OPTARG}\n" >&2
        exit 1
        ;;
      :)
        printf "Option -${OPTARG} requires an argument.\n" >&2
        exit 1
        ;;
    esac
  done

  print_usage
  exit 1
}


# entry point
main "${@}"

