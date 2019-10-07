#!/bin/python
import os

def main():
    net_interfaces = os.listdir('/sys/class/net/')

    print("Interfaces:")
    print("Index", "Name", sep="\t")
    for i in range(0, len(net_interfaces)):
        print(i, net_interfaces[i], sep="\t")

    internal_interface_index = input("Select index of interface for external network(0-%d): " % (len(net_interfaces) - 1))
    if not internal_interface_index.isdigit():
        print("Error: Invalid interface")

    external_interface_index = input("Select index of interface for internal network(0-%d): " % (len(net_interfaces) - 1))
    if not external_interface_index.isdigit():
        print("Error: Invalid interface")

    if internal_interface_index == external_interface_index:
        print("Error: Cannot have the same external and internal interface")

    internal_interface = net_interfaces[internal_interface_index]
    external_interface = net_interfaces[external_interface_index]

    print("The following must be entered in dotted decimal format")
    external_host = input("External IP address of this machine: ")
    external_address_space = input("External network space: ")
    internal_host = input("Internal target host: ")
    internal_address_space = input("Internal network space: ")
    external_gateway = input("External gateway: ")

    fwd_proc_filename = "/proc/sys/net/ipv4/ip_forward"
    with open(fwd_proc_filename, "w") as fwd_proc_file:
        fwd_proc_file.write("1")

    print("Wiping current IPTABLES")
    os.system("iptables -F")
    os.system("iptables -X")
    os.system("iptables -t nat -F")
    os.system("iptables -t nat -X")

    print("Settings default policy to DROP")
    os.system("iptables -P INPUT DROP")
    os.system("iptables -P OUTPUT DROP")
    os.system("iptables -P FORWARD DROP")

    print("Configuring IPTABLES for forwarding")
    os.system("iptables -t nat -A POSTROUTING -o %s -j SNAT MASQUERADE" % (internal_interface))
    os.system("iptables -t nat -A PREROUTING -d %s -j DNAT --to-destination %s" % (external_host, internal_host))

    print("Configuring routing")
    os.system("clear ip route")
    os.system("ip route add %s dev %s" % (external_address_space, external_interface))
    os.system("ip route add %s dev %s" % (internal_address_space, internal_interface))
    os.system("ip route add default via %s" % (external_gateway))


if __name__ == "__main__":
    main()
