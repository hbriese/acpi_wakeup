#!/usr/bin/python3
import argparse
import os
import re

DEVICES_PATH = '/proc/acpi/wakeup'


def read_config():
    conf_path = '/etc/acpi_wakeup.conf'

    if os.path.exists(conf_path):
        devices = []
        with open(conf_path, 'r') as f:
            for dev in f:
                dev = dev.lstrip().partition('#')[0].rstrip()
                if len(dev) > 0:
                    devices.append(dev)

        return devices

    # Else return default devices
    return ['PBTN', r'LID[\d]*']


def device_in_list(enable_devs, dev, sysfs_node):
    found = any((re.match(expr, dev) for expr in enable_devs))
    if not found and sysfs_node:
        found = any((re.match(expr, sysfs_node) for expr in enable_devs))

    return found


def echo(file, s):
    os.system('echo "{}" > {}'.format(s, file))


def print_devices():
    with open(DEVICES_PATH, 'r') as f:
        print(''.join(f.readlines()))


def get_devices():
    devices = []    # Devices are tuples (Device, S-state, Status, Sysfs node)
    with open(DEVICES_PATH, 'r') as f:
        f.readline()    # Ignore first line
        for l in f:
            l = l.strip().split()
            # Add Devices & S-state if they're empty
            if len(l) > 0 and len(l[0]) > 0 and l[0][0] == '*':
                l = ['', ''] + l

            if len(l) < 4:  # Add empty Sysfs node if required
                l.append('')

            l[2] = 'enabled' in l[2]    # Convert status to bool
            devices.append(l)

    return devices


def set_device_wakeup(enable_devs, dev):
    # Device   S-state   Status   Sysfs node
    name, state, status, node = dev

    enable = device_in_list(enable_devs, name, node)
    if status ^ enable:  # (enabled and not enable_dev) or (not enabled and enable_dev):
        echo(DEVICES_PATH, name)

        if node:  # Disable devices with a provided node manually
            dev_type, name = node.split(sep=':', maxsplit=1)
            p = '/sys/bus/{}/devices/{}/power/wakeup'.format(dev_type, name)
            if os.path.exists(p):
                echo(p, 'enabled' if enable else 'disabled')
            else:
                print('WARNING: wakeup path does not exist: {}'.format(p))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--list', '-l', default=False, action='store_true', help='List ACPI wakeup devices')
    parser.add_argument('--devices', '-d', dest='devices', nargs='*',
                        help="ACPI wakeup devices to keep enabled; accepts regex. Default: -d PBTN LID\d*")
    parser.add_argument('--set', '-s', default=False, action='store_true',
                        help='Enable wakeup devices listed, disable those not.')
    args = parser.parse_args()

    # Wakeup devices order of pref: args, config, default values
    enable_devices = args.devices if args.devices else read_config()

    if args.set:
        if os.getuid() != 0:
            print('Must be run as root.')
            exit(1)

        for dev in get_devices():
            set_device_wakeup(enable_devices, dev)
    elif args.list:
        print_devices()
    else:
        parser.print_help()
