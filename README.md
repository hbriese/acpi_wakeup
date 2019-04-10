
# DisableACPIWakeupDevices
> Disable all but a set of ACPI wakeup devices on boot.

#### Install
```bash
$ DisableACPIWakeupDevices/installer install
```


#### Uninstall
```bash
$ DisableACPIWakeupDevices/installer uninstall
```


## Usage
#### List ACPI wakeup devies
```bash
$ disable-wakeup-devices -l
```


#### Keep enabled specified wakeup devices (persistent)
Device names (or sysfs nodes) that you want ACPI wakeups enabled for. Supports regular expressions.

Create a text file at /etc/wakeup-devices.conf with each device on a new line.

_e.g. Keep awake PBTN (power button), LID devices (e.g. LID...), and a particular PCI devices._
```text
> /etc/wakeup-devices.conf
PBTN
LID[\d]*
pci:0000:00:14.0
```

> _Default devices enabled:  PBTN LID[\d]*_

**It is recommended to specify devices by their sysfs node (e.g. pci:...) if the device name is not unique.**

##### Disable ALL devices
Create an empty text file at /etc/wakeup-devices.conf
```bash
$ sudo sh -c "echo '' > /etc/wakeup-devices.conf"
```

##### Restore defaults
```bash
$ sudo rm /etc/wakeup-devices.conf
```


#### Service Status
```bash
$ sudo systemctl status disable-wakeup-devices.service
```


#### Keep enabled specified wakeup devices (non-persistent)
_Overrides devices in /etc/wakeup-devices.conf_
```bash
$ disable-wakeup-devices -s -d DEVICE DEVICE ...
```

_e.g._
```bash
$ disable-wakeup-devices -s -d PBTN LID[\d]* pci:0000:00:14.0
```


##### Disable ALL devices
Use --devices (-d) without any options to disable all wakeup devices.
```bash
$ disable-wakeup-devices -s -d
```


#### Enable/disable wakeup devices
Automatically executed on start by systemd.

Use with other options for them to have an affect.

```bash
$ disable-wakeup-devices -s
```
