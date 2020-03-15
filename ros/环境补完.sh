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