# Makefile to raspberry pi's on robot and suraface unit
# Should work on Unix. For windows, go to the location of your python.exe 
# 	binary and rename a copy of it to python3.exe

PYTHON_CMD = python3.5
PYTHON_FLAGS = -B
PYTHON_VERSION = python_version

MAIN_SRC = main.py
TEST_SRC = tests.py
LAUNCH_CMD = $(PYTHON_CMD) $(PYTHON_FLAGS) $(MAIN_SRC)

robot:
	$(LAUNCH_CMD) robot

server:
	$(LAUNCH_CMD) topside

test: $(TEST_SRC)
	$(PYTHON_CMD) $(PYTHON_FLAGS) $(TEST_SRC)

# Setup environment for development and use
# Supprts only systems that use the apt package manager and diff
# Windows and Mac not supported
env: 
	$(PYTHON_CMD) --version | diff $(PYTHON_VERSION) -

env_setup: py_modules # env_setup py_setup py_modules
	sudo apt update
	sudo apt upgrade
	
py_setup: env_setup
	# From apt repos: (based on your distro, raspbian will be different)
	sudo apt update
	sudo apt install python3.5
	sudo apt install python3.5-pip
	
# py_build:
# 	sudo apt update
# 	sudo apt upgrade
# 	sudo apt install build-essential tk-dev libncurses5-dev libncursesw5-dev libreadline6-dev libdb5.3-dev libgdbm-dev libsqlite3-dev libssl-dev libbz2-dev libexpat1-dev liblzma-dev zlib1g-dev
# 	According to https://gist.github.com/dschep/24aa61672a2092246eaca2824400d37f
# 	wget https://www.python.org/ftp/python/3.6.5/Python-3.6.5.tar.xz
# 	tar xf Python-3.6.5.tar.xz
# 	cd Python-3.6.5
# 	./configure --enable-optimizations
# 	make -j 4
# 	sudo make altinstall

todo:
	grep --line-number --initial-tab "TODO:" *.py | tr -s [:space:]  > todo.txt
	cat todo.txt

gource:
	gource -a 0.25 -s 1 --hide bloom -r 60  -1920x1080 -o - | ffmpeg -y -r 60 -f image2pipe -vcodec ppm -i - -vcodec libvpx -b20000K ../../../gource.webm
