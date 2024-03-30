#ifndef SA_TOP_H
#define SA_TOP_H

#include <cstring>
#include "ap_int.h"
#include "hls_stream.h"
#include "src/pipeline_sa_hls.hpp"

extern "C" void simulatedAnnealingTop(ap_int<8> *n2c, ap_int<8> *c2n, ap_int<8> *n);

#endif
