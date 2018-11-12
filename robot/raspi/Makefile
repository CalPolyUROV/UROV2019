# Makefile to raspberry pi's on robot and suraface unit
# Should work on Unix. For windows, go to the location of your python.exe 
# 	binary and rename a copy of it to python3.exe

PYTHON_CMD = python3
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
env:
	sudo apt install python3
	sudo apt install python3-pip
	$(PYTHON_CMD) -m pip install --upgrade pip
	$(PYTHON_CMD) -m pip install pyserial --user
	$(PYTHON_CMD) -m pip install pygame --user
	$(PYTHON_CMD) --version | diff $(PYTHON_VERSION) -
	