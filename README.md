# VAEsemane for Raspberry Pi

## What you need
* a Raspberry Pi 3B+ and an SD card with 16GB or more
* a Touch Screen, e.g. [OSOYOO Touchscreen LCD-Monitor HDMI Display 3,5"](https://www.amazon.de/gp/product/B01N5G02MZ/)
* lots of time to compile PyTorch, NumPy and other python libraries from source on Raspian

## How to build this
1. Install Raspian on your Raspberry Pi using [this documentation](https://www.raspberrypi.org/documentation/installation/noobs.md).
In case you don't have a keyboard and screen, make sure you enable ssh before installing Raspian by putting an empty ssh
file in the boot folder on the SD card. Also, the NOOBS download comes with different OS, you have to manually delete all 
other OS, so installation jumps straight to the installation of Raspian. 

2. Add at least to 2GB of swap to your Raspi by changing /etc/dphys-swapfile
```bash
# change swap size in dphys-swapfile so it maches your desired swap size 
# using your favorite editor, here we use vim.tiny
sudo vim.tiny /etc/dphys-swapfile

# reboot so changes take effect
sudo reboot
```

3. Install needed libraries --> **ToDo, coming soon**

