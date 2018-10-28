
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

env:
	sudo apt install python3
	sudo apt install python3-pip
	$(PYTHON_CMD) -m pip install --upgrade pip
	$(PYTHON_CMD) -m pip install pyserial
	$(PYTHON_CMD) --version | diff $(PYTHON_VERSION) -
	