# Makefile to raspberry pi's on robot and suraface unit
# Should work on Unix. For windows, go to the location of your python.exe 
# 	binary and rename a copy of it to python3.exe

PYTHON_CMD = python3
PYTHON_DBG_FLAGS = -B

MAIN_SRC = main.py
TEST_SRC = tests.py
LAUNCH_CMD = $(PYTHON_CMD) $(MAIN_SRC)
DBG_LAUNCH_CMD = $(PYTHON_CMD) $(PYTHON_DBG_FLAGS) $(MAIN_SRC)

ROBOT_IP = 10.0.10.11
USERNAME = ubuntu

# Production launchers
robot:
	$(LAUNCH_CMD) robot

topside:
	$(LAUNCH_CMD) topside

# Debug launchers
debug_topside:
	$(DBG_LAUNCH_CMD) topside -d

debug_robot:
	$(DBG_LAUNCH_CMD) robot -d

# Debug shortcuts
dt: debug_topside

dr: debug_robot


ssh:
	ssh $(USERNAME)@$(ROBOT_IP)

test: $(TEST_SRC)
	$(PYTHON_CMD) $(TEST_SRC)

# Setup environment for development and use
# Supprts only systems that use the apt package manager
# Windows and Mac not supported
py_version: 
	$(PYTHON_CMD) --version | diff python_version -
	
py_install:
	# From apt repos: (based on your distro, raspbian will be different)
	sudo apt update
	sudo apt install python3
	
py:
	$(PYTHON_CMD)

py_build:
	# According to https://gist.github.com/dschep/24aa61672a2092246eaca2824400d37f
	cd ../../..
	sudo apt update
	sudo apt upgrade
	sudo apt install build-essential tk-dev libncurses5-dev libncursesw5-dev libreadline6-dev libdb5.3-dev libgdbm-dev libsqlite3-dev libssl-dev libbz2-dev libexpat1-dev liblzma-dev zlib1g-dev
	wget https://www.python.org/ftp/python/3.6.5/Python-3.6.5.tar.xz
	tar xf Python-3.6.5.tar.xz
	cd Python-3.6.5
	./configure --enable-optimizations
	make -j 4
	sudo make altinstall

pip_install:
	sudo apt install python3-pip

pip_upgrade:
	$(PYTHON_CMD) -m pip install --upgrade pip --user

pyserial_install:
	$(PYTHON_CMD) -m pip install --upgrade pyserial

pygame_install:
	$(PYTHON_CMD) -m pip install --upgrade pygame

pygame_build:
	# https://www.raspberrypi.org/forums/viewtopic.php?f=32&t=33157
	cd ../../..
	sudo apt-get install mercurial 
	hg clone https://bitbucket.org/pygame/pygame
	cd pygame

	sudo apt-get install libsdl-dev libsdl-image1.2-dev libsdl-mixer1.2-dev libsdl-ttf2.0-dev 
	sudo apt-get install libsmpeg-dev libportmidi-dev libavformat-dev libswscale-dev
	sudo apt-get install python3-dev python3-numpy

	python3 setup.py build 
	sudo python3 setup.py install

pygame_build_mac:
	# https://brysonpayne.com/2015/01/10/setting-up-pygame-on-a-mac/
	brew install mercurial
	brew install sdl sdl_image sdl_mixer sdl_ttf portmidi
	brew install --HEAD smpeg
	sudo pip3 install hg+http://bitbucket.org/pygame/pygame

todo:
	grep --line-number --initial-tab "# TODO:" *.py | tr -s [:space:]  > todo.txt
	cat todo.txt

clean:
	find . -name '*.pyc' -delete
	find . -name '__pycache__' -delete
	# rm -rf trash

gource:
	gource -a 0.25 -s 1 --hide bloom -r 60  -1920x1080 -o - | ffmpeg -y -r 60 -f image2pipe -vcodec ppm -i - -vcodec libvpx -b20000K ../../../gource.webm
