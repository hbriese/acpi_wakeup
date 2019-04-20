#!/usr/bin/python3
import argparse
import os
import re


def read_config():
    conf_path = '/etc/wakeup-devices.conf'

    if os.path.exists(conf_path):
        devices = []
        with open(conf_path, 'r') as f:
            for l in f:
                l = l.strip()
                if l:
                    devices.append(l)

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


def set_device_wakeup(wakeup_path, enable_devs, l):
    # Device   S-state   Status   Sysfs node
    dev = l[0]
    enabled = 'enabled' in l[2]
    sysfs_node = l[3] if len(l) >= 4 else None

    enable = device_in_list(enable_devs, dev, sysfs_node)
    if enabled ^ enable:  # (enabled and not enable_dev) or (not enabled and enable_dev):
        echo(wakeup_path, dev)

        if sysfs_node:  # Disable devices with a sysfs node manually
            dev_type, dev = sysfs_node.split(sep=':', maxsplit=1)
            p = '/sys/bus/{}/devices/{}/power/wakeup'.format(dev_type, dev)
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

    # Read acpi wakeup devices
    acpi_wakeup_path = '/proc/acpi/wakeup'
    with open(acpi_wakeup_path, 'r') as f:
        acpi_lines = f.readlines()

    # Wakeup devices order of pref: args, config, default values
    enable_devices = args.devices if args.devices else read_config()

    if args.set:
        # if os.getuid() != 0:
        #     print('Must be run as root.')
        #     exit(1)

        acpi_device_lines = [l.strip().split() for l in acpi_lines][1:]
        for l in acpi_device_lines:
            set_device_wakeup(acpi_wakeup_path, enable_devices, l)
    elif args.list:
        print(''.join(acpi_lines))
    else:
        parser.print_help()

