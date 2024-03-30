MK_PATH := $(abspath $(lastword $(MAKEFILE_LIST)))
CUR_DIR=$(patsubst %/,%,$(dir $(MK_PATH)))

KERNEL_DIR=$(CUR_DIR)
COMMON_DIR=$(CUR_DIR)/common/include
COMMON_SRCS=""

TARGET=sa

SRCS=$(KERNEL_DIR)/sa.cpp \
        $(KERNEL_DIR)/sa.hpp \
        $(KERNEL_DIR)/saTop.hpp \
        $(KERNEL_DIR)/saTop.cpp

# use platform info utility to query correct part for board target
ifndef DEVICE
$(error DEVICE should be set to a valid Xilinx platform file (xpfm))
else
XPART=$(shell platforminfo $(DEVICE) --json="hardwarePlatform.board.part")
endif

# default build parameters
XPERIOD?=3.125

.PHONY: all
all: $(TARGET)

$(TARGET): $(SRCS) $(COMMON_SRCS)
	-rm -rf prj*
	XPART=$(XPART) XPERIOD=$(XPERIOD) vitis_hls -f xo_generate.tcl

.PHONY: clean
clean:
	-rm -rf prj*
	-rm -f *.xo
	-rm -f *.log
