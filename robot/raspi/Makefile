
PYTHON_CMD = python3
PYTHON_FLAGS = -b -B -W ignore:Deprecation

ROBOT_SRC = main.py
SERVER_SRC = topside.py
TEST_SRC = tests.py


robot: $(ROBOT_SRC)
	$(PYTHON_CMD) $(PYTHON_FLAGS) $(ROBOT_SRC)

server: $(SERVER_SRC)
	$(PYTHON_CMD) $(PYTHON_FLAGS) $(SERVER_SRC)

test: $(TEST_SRC)
	$(PYTHON_CMD) $(PYTHON_FLAGS) $(TEST_SRC)
	