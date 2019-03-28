How to install rtlsdr-wsprd

sudo apt-get update
sudo apt-get upgrade

sudo apt-get install build-essential cmake libfftw3-dev curl libcurl4-gnutls-dev ntp libusb-1.0-0-dev librtlsdr-dev git

git clone https://github.com/Guenael/rtlsdr-wsprd
cd rtlsdr-wsprd/
make

Then config /bin/wspr.sh with your data.
