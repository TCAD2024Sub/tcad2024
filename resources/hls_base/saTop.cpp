
#include <saTop.hpp>

extern "C" void simulatedAnnealingTop(ap_uint<7> *mem1,ap_uint<7> *mem2,ap_uint<7> *mem3){
#pragma HLS INTERFACE m_axi port = mem1 offset = slave
#pragma HLS INTERFACE m_axi port = mem2 offset = slave
#pragma HLS INTERFACE m_axi port = mem3 offset = slave
#pragma HLS INTERFACE s_axilite port = return




}
