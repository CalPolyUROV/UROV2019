TARGET = pwmdemo

CC		:= gcc
LINKER		:= gcc -o
CFLAGS		:= -c -Wall -g -fPIC #-I/home/ubuntu/libraries/libuio -I/home/ubuntu/libraries/libpwm
LFLAGS		:= -shared
RM		:= rm -f

SRCDIR		= src
OBJDIR		= obj
SODIR		= so

SOURCES  	:= $(wildcard $(SRCDIR)/*.c)
INCLUDES	:= $(wildcard $(SRCDIR)/*.h)
OBJECTS  	:= $(SOURCES:$(SRCDIR)/%.c=$(OBJDIR)/%.o)
DYNOBJ		:= libpwmuio.so


# linking Objects
$(TARGET): $(OBJECTS)
	@$(LINKER) $(@) $(OBJECTS) $(LFLAGS)

# compiling command
$(OBJECTS): $(OBJDIR)/%.o : $(SRCDIR)/%.c $(INCLUDES)
	@$(CC) $(CFLAGS) -c $< -o $@
	@echo "Compiled "$<" successfully!"

so: $(DYNOBJ)
$(DYNOBJ): $(OBJECTS)
	@mkdir -p $(SODIR)
	@$(LINKER) $(SODIR)/$(@) $(LFLAGS) $(OBJECTS)
	@echo Sucessfully linked $(@) using $(OBJECTS)

all:
	$(TARGET)

clean:
	@$(RM) $(OBJECTS)
	@$(RM) $(TARGET)
	@$(RM) $(SODIR)/*.so
	@echo "$(TARGET) Clean Complete"
