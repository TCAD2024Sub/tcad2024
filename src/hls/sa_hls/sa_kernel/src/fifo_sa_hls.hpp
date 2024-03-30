#ifndef CPP_FIFO_SA_HLS_H
#define CPP_FIFO_SA_HLS_H

#include "types_sa_hls.hpp"

#define CAPACITY 10

class FifoSaHls
{
private:
    W m_arr[CAPACITY];
    ap_int<8> m_size;
    ap_int<8> m_front;
    ap_int<8> m_rear;

public:
    FifoSaHls();
    void enqueue(W data);
    W dequeue();
    W peek();
    bool isEmpty() const;
    bool isFull() const;
    ap_int<8> getSize() const;
};

#endif
