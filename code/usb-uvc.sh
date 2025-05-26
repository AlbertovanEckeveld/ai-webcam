#!/bin/bash

cd /sys/kernel/config/usb_gadget/
mkdir -p g1
cd g1

echo 0x1d6b > idVendor  # Linux Foundation
echo 0x0104 > idProduct # Multifunction Composite Gadget
echo 0x0100 > bcdDevice
echo 0x0200 > bcdUSB

mkdir -p strings/0x409
echo "1234567890" > strings/0x409/serialnumber
echo "RPi" > strings/0x409/manufacturer
echo "PiCameraGadget" > strings/0x409/product

mkdir -p configs/c.1/strings/0x409
echo "Config 1: UVC" > configs/c.1/strings/0x409/configuration
echo 120 > configs/c.1/MaxPower

# Video function (UVC)
mkdir -p functions/uvc.usb0
mkdir -p functions/uvc.usb0/control/header/h
ln -s functions/uvc.usb0/control/header/h functions/uvc.usb0/control/class/fs/h
ln -s functions/uvc.usb0/control/header/h functions/uvc.usb0/control/class/ss/h

mkdir -p functions/uvc.usb0/streaming/header/h
mkdir -p functions/uvc.usb0/streaming/uncompressed/u
echo 1 > functions/uvc.usb0/streaming/uncompressed/u/bDescriptorSubtype
echo 640 > functions/uvc.usb0/streaming/uncompressed/u/wWidth
echo 480 > functions/uvc.usb0/streaming/uncompressed/u/wHeight
echo 1843200 > functions/uvc.usb0/streaming/uncompressed/u/dwMaxVideoFrameBufferSize
echo 333333 > functions/uvc.usb0/streaming/uncompressed/u/dwDefaultFrameInterval

ln -s functions/uvc.usb0/streaming/uncompressed/u functions/uvc.usb0/streaming/header/h
ln -s functions/uvc.usb0/streaming/header/h functions/uvc.usb0/streaming/class/fs/h
ln -s functions/uvc.usb0/streaming/header/h functions/uvc.usb0/streaming/class/ss/h

ln -s functions/uvc.usb0 configs/c.1/

ls /sys/class/udc > UDC