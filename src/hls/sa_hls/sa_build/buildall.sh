# set pipefail to catch and exit on any errors
set -Eeuo pipefail

BASE_DIR=$(dirname $(readlink -f $0))

TARGET=hw_emu
DEVICE=/opt/xilinx/platforms/xilinx_u55c_gen3x16_xdma_3_202210_1/xilinx_u55c_gen3x16_xdma_3_202210_1.xpfm
export XCL_EMULATION_MODE=hw_emu

pushd ${BASE_DIR}/../sa_kernel
make clean DEVICE=$DEVICE
make all DEVICE=$DEVICE
popd

# xilinx binary container (xclbin)
pushd ${BASE_DIR}
make realclean DEVICE=$DEVICE
make binary-container TARGET=$TARGET DEVICE=$DEVICE
popd
