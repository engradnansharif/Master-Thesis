# Master-Thesis
Intelligent Door Lock System with AI Face Recognition

---------------INSTALLATION GUIDELINE------------------
Checking memory:
df -h
Note: (/dev/root Should be 29G)
If you're not using most of it, run
 sudo raspi-config
 advanced -- expand filesystem
 reboot your pi
 
sudo apt-get update && sudo apt-get upgrade

Check your python version (Should be 3.9):

python3 -V

sudo apt-get install python3-pip python3-virtualenv

cd door_system/

python3 -m pip install virtualenv
python3 -m virtualenv env
source env/bin/activate

Installation of system packages:

sudo apt install -y build-essential cmake pkg-config libjpeg-dev libtiff5-dev libpng-dev libavcodec-dev libavformat-dev libswscale-dev libv4l-dev libxvidcore-dev libx264-dev libfontconfig1-dev libcairo2-dev libgdk-pixbuf2.0-dev libpango1.0-dev libgtk2.0-dev libgtk-3-dev libatlas-base-dev gfortran libhdf5-dev libhdf5-serial-dev libhdf5-103 libqt5gui5 libqt5webkit5 libqt5test5 python3-pyqt5 python3-dev
sudo apt-get install libopenblas-base
pip install "picamera[array]"

Opencv Installation:

pip install opencv-contrib-python
pip install opencv-python

Note: It will take a long time.

Check Numpy Version:

python3 -c "import numpy; print(numpy.__version__)"

The numpy version was used here 1.24.3, If not change using following:

pip install numpy==1.24.3

Intalling other necessary packages:

pip3 install adafruit-circuitpython-fingerprint

pip install pyserial

pip install face-recognition

pip install RPi.GPIO


Enable the camera and UART:

 sudo raspi-config
 Go to Inferface Options
 Legacy Camera Support -- Enable 
 Serial Port -- Enable
 Serial Console --Disable

Then reboot... Done!
