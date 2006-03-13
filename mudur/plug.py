#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2006, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version. Please read the COPYING file.
#

import sys
import os
import string
import subprocess
import gettext
import time

def loadFile(path):
    """Read contents of a file"""
    f = file(path)
    data = f.read()
    f.close()
    return data

#

def sysValue(path, value):
    return loadFile("%s/%s" % (path, value)).rstrip("\n")

def sysHexValue(path, value):
    tmp = loadFile("%s/%s" % (path, value)).rstrip("\n")
    if tmp.startswith("0x"):
        tmp = tmp[2:]
    return tmp

#

def pciDevice(path):
    return (
            sysHexValue(path, "vendor"),
            sysHexValue(path, "device"),
            sysHexValue(path, "subsystem_vendor"),
            sysHexValue(path, "subsystem_device"),
            sysValue(path, "class")
    )

def pciColdDevices():
    devices = []
    for dev in os.listdir("/sys/bus/pci/devices"):
        devices.append(pciDevice("/sys/bus/pci/devices/%s" % dev))
    return devices

def pciModules(devices):
    PCI_ANY = '0xffffffff'
    
    modules = set()
    for mod in file("/lib/modules/%s/modules.pcimap" % os.uname()[2]):
        if mod != '' and not mod.startswith('#'):
            mod = mod.split()
            for dev in devices:
                t = filter(lambda x: mod[x+1] == PCI_ANY or mod[x+1].endswith(dev[x]), range(4))
                if len(t) != 4:
                    continue
                if int(dev[4], 16) & int(mod[6], 16) != int(mod[5], 16):
                    continue
                modules.add(mod[0])
    return modules

#

def usbDevice(path):
    dev = [
        "0x%s" % sysValue(path, "../idVendor"),
        "0x%s" % sysValue(path, "../idProduct"),
        "0x%s" % sysValue(path, "../bcdDevice"),
    ]
    
    if os.path.exists(path + "/bDeviceClass"):
        dev.extend((
            "0x%s" % sysValue(path, "bDeviceClass"),
            "0x%s" % sysValue(path, "bDeviceSubClass"),
            "0x%s" % sysValue(path, "bDeviceProtocol"),
        ))
    else:
        # out-of-range values
        dev.extend(('0x1000', '0x1000', '0x1000'))
    
    if os.path.exists(path + "/bInterfaceClass"):
        dev.extend((
            "0x%s" % sysValue(path, "bInterfaceClass"),
            "0x%s" % sysValue(path, "bInterfaceSubClass"),
            "0x%s" % sysValue(path, "bInterfaceProtocol"),
        ))
    else:
        # out-of-range values
        dev.extend(('0x1000', '0x1000', '0x1000'))
    
    return dev

def usbColdDevices():
    devices = []
    for dev in os.listdir("/sys/bus/usb/devices"):
        if dev[0] in string.digits:
            path = os.path.realpath("/sys/bus/usb/devices/" + dev)
            if os.path.exists(os.path.join(path, "../idVendor")):
                devices.append(usbDevice(path))
    return devices

def usbModules(devices):
    mVendor = 0x0001
    mProduct = 0x0002
    mDevLo = 0x0004
    mDevHi = 0x0008
    mDevClass = 0x0010
    mDevSubClass = 0x0020
    mDevProto = 0x0040
    mIntClass = 0x0080
    mIntSubClass = 0x0100
    mIntProto = 0x0200
    
    modules = set()
    for line in file("/lib/modules/%s/modules.usbmap" % os.uname()[2]):
        if line == '' or line.startswith('#'):
            continue
        
        mod, flags, values = line.split(None, 2)
        flags = int(flags, 16)
        values = values.split()
        for dev in devices:
            if flags & mVendor and dev[0] != values[0]:
                continue
            if flags & mProduct and dev[1] != values[1]:
                continue
            if flags & mDevLo and int(dev[2], 16) < int(values[2], 16):
                continue
            if flags & mDevHi and int(dev[2], 16) < int(values[3], 16):
                continue
            if flags & mDevClass and dev[3] != values[4]:
                continue
            if flags & mDevSubClass and dev[4] != values[5]:
                continue
            if flags & mDevProto and dev[5] != values[6]:
                continue
            if flags & mIntClass and dev[6] != values[7]:
                continue
            if flags & mIntSubClass and dev[7] != values[8]:
                continue
            if flags & mIntProto and dev[8] != values[9]:
                continue
            modules.add(mod)
    return modules

#

devs = pciColdDevices()
print pciModules(devs)

devs = usbColdDevices()
print usbModules(devs)
