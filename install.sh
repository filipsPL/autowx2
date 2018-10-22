#!/bin/bash


### created for and tested at the debian-like systems (tested on debian, ubuntu and mint)

### for installing the dongle
### for details, see: http://www.instructables.com/id/rtl-sdr-on-Ubuntu/
#sudo echo 'SUBSYSTEM=="usb", ATTRS{idVendor}=="0bda", ATTRS{idProduct}=="2838", GROUP="adm", MODE="0666", SYMLINK+="rtl_sdr"' >> /etc/udev/rules.d/20.rtlsdr.rules
#sudo echo "blacklist dvb_usb_rtl28xxu" >>  /etc/modprobe.d/rtl-sdr-blacklist.conf

MACHINE_TYPE=`uname -m`

./configure.sh


echo "basedir_conf.py:"
cat basedir_conf.py

source basedir_conf.py
echo $baseDir

echo
echo
echo "******** Installing required packages"
echo
echo
sudo apt-get update
sudo apt-get install rtl-sdr git libpulse-dev qt4-qmake fftw3 libc6 libfontconfig1 libx11-6 libxext6 libxft2 libusb-1.0-0-dev \
libavahi-client-dev libavahi-common-dev libdbus-1-dev libfftw3-long3 libfftw3-single3 libpulse-mainloop-glib0 librtlsdr0 librtlsdr-dev \
libfftw3-dev  libfftw3-double3 libfftw3-quad3 lame sox libsox-fmt-mp3 libtool automake python-pil python-imaging

echo
echo
echo "******** Installing python requirements"
echo
echo
pip install -r requirements.txt


mkdir -p $baseDir/bin/sources/

cd $baseDir/bin/sources/

echo
echo
echo "******** Installing wxtoimg"
echo
echo

if [ ${MACHINE_TYPE} == 'x86_64' ]; then
    echo "64-bit system"
    wget https://wxtoimgrestored.xyz/downloads/wxtoimg-linux64-2.10.11-1.tar.gz
    gunzip < wxtoimg-linux64-2.10.11-1.tar.gz | sudo sh -c "(cd /; tar -xvf -)"
else
    echo "32-bit system"
    wget https://wxtoimgrestored.xyz/downloads/wxtoimg_2.10.11-1_i386.deb
    sudo dpkg -i wxtoimg_2.10.11-1_i386.deb	# may generate some dependencies errors; if not, stop here
    # sudo apt-get -f install
fi

wxtoimg -h


echo
echo
echo "******** Installing multimon-ng-stqc"
echo
echo

cd $baseDir/bin/sources/

git clone https://github.com/sq5bpf/multimon-ng-stqc.git
cd multimon-ng-stqc
mkdir build
cd build
qmake ../multimon-ng.pro
make
sudo make install


multimon-ng -h



echo
echo
echo "******** Installing kalibrate"
echo
echo

cd $baseDir/bin/sources/

git clone https://github.com/viraptor/kalibrate-rtl.git
cd kalibrate-rtl
./bootstrap
./configure
make
sudo make install

kal -h


echo
echo
echo "******** Getting auxiliary programs"
echo
echo

cd $baseDir/bin/
wget https://raw.githubusercontent.com/filipsPL/heatmap/master/heatmap.py -O $baseDir/bin/heatmap.py



echo
echo
echo "******** Getting fresh keplers"
echo
echo

cd $baseDir
bin/update-keps.sh



exit 0

