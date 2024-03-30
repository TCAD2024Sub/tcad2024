set COMMON_DIR [pwd]/common/include
set KERNEL_DIR [pwd]

set CFLAGS "-I${COMMON_DIR} -I${KERNEL_DIR} -std=c++14"

open_project -reset prj_ob
add_files ${KERNEL_DIR}/sa.cpp -cflags ${CFLAGS}
add_files ${KERNEL_DIR}/saTop.cpp  -cflags ${CFLAGS}
set_top simulatedAnnealingTop
open_solution -reset -flow_target vitis "simulatedAnnealingTop"
set_part $::env(XPART)
create_clock -period $::env(XPERIOD) -name default
config_compile -pragma_strict_mode=true
csynth_design
export_design -rtl verilog -format xo -output simulatedAnnealingTop.xo
close_project

exit
