#!/bin/bash


### created for and tested at the debian-like systems (tested on debian, ubuntu and mint)

### for installing the dongle
### for details, see: http://www.instructables.com/id/rtl-sdr-on-Ubuntu/
#sudo echo 'SUBSYSTEM=="usb", ATTRS{idVendor}=="0bda", ATTRS{idProduct}=="2838", GROUP="adm", MODE="0666", SYMLINK+="rtl_sdr"' >> /etc/udev/rules.d/20.rtlsdr.rules
#sudo echo "blacklist dvb_usb_rtl28xxu" >>  /etc/modprobe.d/rtl-sdr-blacklist.conf

echo
echo
echo "******** Installing required packages"
echo
echo

sudo apt-get install rtl-sdr git libpulse-dev qt4-qmake fftw3 libc6 libfontconfig1 libx11-6 libxext6 libxft2 libusb-1.0-0-dev \
libavahi-client-dev libavahi-common-dev libdbus-1-dev libfftw3-long3 libfftw3-single3 libpulse-mainloop-glib0 librtlsdr0 librtlsdr-dev \
libfftw3-dev  libfftw3-double3 libfftw3-quad3 lame sox

echo
echo
echo "******** Installing python requirements"
echo
echo
pip install -r requirements.txt


mkdir -p bin/sources/

cd bin/sources/

echo
echo
echo "******** Installing wxtoimg"
echo
echo
## 32 bit version
# wget http://www.wxtoimg.com/downloads/wxtoimg_2.10.11-1_i386.deb
# sudo dpkg -i wxtoimg_2.10.11-1_i386.deb	# may generate some dependencies errors; if not, stop here
# # sudo apt-get update
# # sudo apt-get upgrade
# sudo apt-get -f install
# # sudo dpkg -i wxtoimg_2.10.11-1_i386.deb	# to finish the installation
# rm wxtoimg_2.10.11-1_i386.deb

wget http://www.wxtoimg.com/downloads/wxtoimg-linux64-2.10.11-1.tar.gz
sudo gunzip < wxtoimg-linux64-2.10.11-1.tar.gz | sudo sh -c "(cd /; tar -xvf -)"
#rm wxtoimg-linux64-2.10.11-1.tar.gz

wxtoimg -h


echo
echo
echo "******** Installing multimon-ng-stqc"
echo
echo

git clone https://github.com/sq5bpf/multimon-ng-stqc.git
cd multimon-ng-stqc
mkdir build
cd build
qmake ../multimon-ng.pro
make
sudo make install
cd ../../

multimon-ng -h



echo
echo
echo "******** Installing kalibrate"
echo
echo

cd bin/
git clone https://github.com/viraptor/kalibrate-rtl.git
cd kalibrate-rtl
./bootstrap
./configure
make
sudo make install
cd ../

exit 0

