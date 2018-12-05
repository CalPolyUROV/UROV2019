# Makefile to raspberry pi's on robot and suraface unit
# Should work on Unix. For windows, go to the location of your python.exe 
# 	binary and rename a copy of it to python3.exe

PYTHON_CMD = python3.5
PYTHON_FLAGS = -B
PYTHON_VERSION = python_version

ROBOT_SRC = main.py
SERVER_SRC = topside.py
TEST_SRC = tests.py

robot: $(ROBOT_SRC)
	$(PYTHON_CMD) $(PYTHON_FLAGS) $(ROBOT_SRC)

server: $(SERVER_SRC)
	$(PYTHON_CMD) $(PYTHON_FLAGS) $(SERVER_SRC)

test: $(TEST_SRC)
	$(PYTHON_CMD) $(PYTHON_FLAGS) $(TEST_SRC)

# Setup environment for development and use
# Supprts only systems that use the apt package manager and diff
# Windows and Mac not supported
env: py_modules # env_setup py_setup py_modules
	
	$(PYTHON_CMD) --version | diff $(PYTHON_VERSION) -

env_setup: 
	sudo apt-get update
	sudo apt-get install build-essential tk-dev libncurses5-dev libncursesw5-dev libreadline6-dev libdb5.3-dev libgdbm-dev libsqlite3-dev libssl-dev libbz2-dev libexpat1-dev liblzma-dev zlib1g-dev
	
py_setup:
	# From apt repos: (based on your distro, raspbian will be different)
	# sudo apt-get update
	# sudo apt install python3
	# sudo apt install python3-pip

#	According to https://gist.github.com/dschep/24aa61672a2092246eaca2824400d37f
# 	wget https://www.python.org/ftp/python/3.6.5/Python-3.6.5.tar.xz
# 	tar xf Python-3.6.5.tar.xz
# 	cd Python-3.6.5
# 	./configure
# 	make
# 	sudo make altinstall

py_modules:

	$(PYTHON_CMD) -m pip install --upgrade pip
	$(PYTHON_CMD) -m pip install pyserial --user
	$(PYTHON_CMD) -m pip install pygame --user
