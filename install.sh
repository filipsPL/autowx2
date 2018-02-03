#!/bin/bash


### created for and tested at the debian-like systems (tested on debian, ubuntu and mint)

### for installing the dongle
### for details, see: http://www.instructables.com/id/rtl-sdr-on-Ubuntu/
#sudo echo 'SUBSYSTEM=="usb", ATTRS{idVendor}=="0bda", ATTRS{idProduct}=="2838", GROUP="adm", MODE="0666", SYMLINK+="rtl_sdr"' >> /etc/udev/rules.d/20.rtlsdr.rules
#sudo echo "blacklist dvb_usb_rtl28xxu" >>  /etc/modprobe.d/rtl-sdr-blacklist.conf


echo "******** Installing required packages"
sudo apt-get install rtl-sdr git libpulse-dev qt4-qmake fftw3


echo "******** Installing python requirements"
pip install -r requirements.txt


mkdir -p bin/sources/

cd bin/sources/

echo "******** Installing wxtoimg"
wget http://www.wxtoimg.com/downloads/wxtoimg_2.10.11-1_i386.deb
sudo dpkg -i wxtoimg_2.10.11-1_i386.deb	# may generate some dependencies errors; if not, stop here
# sudo apt-get update
# sudo apt-get upgrade
sudo apt-get -f install
# sudo dpkg -i wxtoimg_2.10.11-1_i386.deb	# to finish the installation
rm wxtoimg_2.10.11-1_i386.deb

wxtoimg -h


echo "******** Installing multimon-ng-stqc"
git clone https://github.com/sq5bpf/multimon-ng-stqc.git
cd multimon-ng-stqc
mkdir build
cd build
qmake ../multimon-ng.pro
make
sudo make install
cd ../../

multimon-ng -h


echo "******** Installing kalibrate"
cd bin/
git clone https://github.com/viraptor/kalibrate-rtl.git
cd kalibrate-rtl
./bootstrap
./configure
make
sudo make install
cd ../


kal -h

