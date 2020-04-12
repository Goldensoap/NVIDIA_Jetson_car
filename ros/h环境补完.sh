#!/bin/bash

set -e

# pip安装包补完

pip install catkin_pkg rospkg rosinstall osrf-pycommon
# catkin tools 安装
cd ~
git clone https://github.com/catkin/catkin_tools.git

cd catkin_tools

python setup.py install

#cv_bridge编译(可选)
sudo apt install ros-melodic-cv-bridge

cd ~

mkdir -p catkin_workspace/src

cd catkin_workspace

catkin init

catkin config -DPYTHON_EXECUTABLE=/home/jetbot/.pyenv/shims/python3 -DPYTHON_INCLUDE_DIR=/home/jetbot/.pyenv/versions/3.7.6/include/python3.7m -DPYTHON_LIBRARY=/home/jetbot/.pyenv/versions/3.7.6/lib/libpython3.7m.so -DSETUPTOOLS_DEB_LAYOUT=OFF

catkin config --install

git clone https://github.com/ros-perception/vision_opencv.git src/vision_opencv

# apt-cache show ros-melodic-cv-bridge | grep Version

# cd src/vision_opencv/

# git checkout 1.13.0

# cd ../../

# catkin build cv_bridge

# source devel/setup.bash

cd src

catkin create pkg catch_mouse --catkin-deps rospy roscpp sensor_msgs std_msgs cv_bridge