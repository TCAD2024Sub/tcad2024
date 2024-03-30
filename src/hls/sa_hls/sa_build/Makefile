#Makefile for xclbin creation
#

#+-------------------------------------------------------------------------------
# The following parameters are assigned with default values. These parameters can
# be overridden through the make command line
#+-------------------------------------------------------------------------------

REPORT := no
PROFILE := no
DEBUG := no

#'estimate' for estimate report generation
#'system' for system report generation
ifneq ($(REPORT), no)
CLFLAGS += --report estimate
LDCLFLAGS += --report system
endif

# generates profile summary report
ifeq ($(PROFILE), yes)
LDCLFLAGS += --profile_kernel data:all:all:all
endif

# generates debug summary report
ifeq ($(DEBUG), yes)
CLFLAGS += --dk protocol:all:all:all
endif

# configuration settings
VPP := $(XILINX_VITIS)/bin/v++

# extract platform name only from full path to xpfm
XILINX_PLATFORM=$(basename $(notdir $(DEVICE)))

# set default hardware target, allows override for hardware emulation (hw_emu)
TARGET ?= hw

ifeq ($(TARGET),hw)
PROJECT=sa_hw
else
PROJECT=sa_hw_emu
endif

SA_KERNEL_XO:=simulatedAnnealingTop.xo
SA_KERNEL_XO_FULLPATH=../sa_kernel/$(SA_KERNEL_XO)

# shell specific connectivity
ifeq ($(TARGET),$(filter $(TARGET),hw_emu))
VPPLINKFLAGS := --config sa.hw_emu.ini
else
VPPLINKFLAGS := --config sa.u55.ini
endif


XODIR = xo
ifeq ($(TARGET),$(filter $(TARGET),hw_emu))
# adds debug symbols
VPPLINKFLAGS += -g
endif

XOS = $(SA_KERNEL_XO) 
       
CLFLAGS += -t $(TARGET) --platform $(DEVICE) --save-temps --kernel_frequency 320

$(XODIR):
	mkdir $@

# gather up external kernels
xo/$(SA_KERNEL_XO): $(SA_KERNEL_XO_FULLPATH) | $(XODIR)
	cp $< $@

# emulation configuration
emconfig: $(EMCONFIG_DIR)/emconfig.json
$(EMCONFIG_DIR)/emconfig.json:
	emconfigutil --platform $(DEVICE) --od $(EMCONFIG_DIR)

BINARY_CONTAINER = $(PROJECT).xclbin
BINARY_CONTAINER_XOS = $(addprefix $(XODIR)/,$(XOS))

.PHONY: gather-xos
gather-xos: $(BINARY_CONTAINER_XOS)

.PHONY: binary-container
binary-container: $(BINARY_CONTAINER)

$(BINARY_CONTAINER): $(BINARY_CONTAINER_XOS)
	$(VPP) $(CLFLAGS) $(LDCLFLAGS) -l -o $@ $^ $(VPPLINKFLAGS)

.PHONY: clean
clean:
	-rm -f $(PROJECT).xclbin* $(PROJECT).ltx *.log
	-rm -rf .ipcache _x .Xil

realclean: clean
	-rm -rf xo/

.PHONY: help
help:
	@echo "Makefile usage:"
	@echo "  make binary-container  Generate hardware build (xclbin)"
	@echo "  make clean             Clean intermediate build folders"
	@echo "  make realclean         Clean + remove imported kernel objects (xo)"

