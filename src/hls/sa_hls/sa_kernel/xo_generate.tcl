
set KERNEL_DIR [pwd]

set CFLAGS "-I${KERNEL_DIR}/src -std=c++14"

open_project -reset prj_ob
add_files ${KERNEL_DIR}/saTop.cpp -cflags ${CFLAGS}
add_files ${KERNEL_DIR}/src/fifo_sa_hls.cpp -cflags ${CFLAGS}
add_files ${KERNEL_DIR}/src/pipeline_sa_hls.cpp -cflags ${CFLAGS}
add_files ${KERNEL_DIR}/src/stage0_sa_hls.cpp -cflags ${CFLAGS}
add_files ${KERNEL_DIR}/src/stage1_sa_hls.cpp -cflags ${CFLAGS}
add_files ${KERNEL_DIR}/src/stage2_sa_hls.cpp -cflags ${CFLAGS}
add_files ${KERNEL_DIR}/src/stage3_sa_hls.cpp -cflags ${CFLAGS}
add_files ${KERNEL_DIR}/src/stage4_sa_hls.cpp -cflags ${CFLAGS}
add_files ${KERNEL_DIR}/src/stage5_sa_hls.cpp -cflags ${CFLAGS}
add_files ${KERNEL_DIR}/src/stage6_sa_hls.cpp -cflags ${CFLAGS}
add_files ${KERNEL_DIR}/src/stage7_sa_hls.cpp -cflags ${CFLAGS}
add_files ${KERNEL_DIR}/src/stage8_sa_hls.cpp -cflags ${CFLAGS}
add_files ${KERNEL_DIR}/src/stage9_sa_hls.cpp -cflags ${CFLAGS}
add_files ${KERNEL_DIR}/src/util_sa_hls.cpp -cflags ${CFLAGS}

set_top simulatedAnnealingTop
open_solution -reset -flow_target vitis "simulatedAnnealingTop"
set_part $::env(XPART)
create_clock -period $::env(XPERIOD) -name default
config_compile -pragma_strict_mode=true
csynth_design
export_design -rtl verilog -format xo -output simulatedAnnealingTop.xo
close_project

exit
