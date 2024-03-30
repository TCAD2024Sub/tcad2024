#ifndef CPP_FIFO_SA_SW_H
#define CPP_FIFO_SA_SW_H

#include "types_sa_sw.hpp"

#define CAPACITY 10

class FifoSaSw
{
private:
    W arr[CAPACITY]{};
    int capacity;
    int size;
    int front;
    int rear;

public:
    FifoSaSw();
    void enqueue(W data);
    W dequeue();
    W peek();
    bool isEmpty() const;
    bool isFull() const;
    int getSize() const;
};

#endif
