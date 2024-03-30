#include "fifo_sa_sw.hpp"

FifoSaSw::FifoSaSw()
{
    capacity = CAPACITY;
    //arr = new W[capacity];
    size = 0;
    front = 0;
    rear = -1;
}

void FifoSaSw::enqueue(W data)
{
    if (isFull())
    {
        return;
    }
    rear = (rear + 1) % capacity;
    arr[rear] = data;
    size++;
}

W FifoSaSw::dequeue()
{
    if (isEmpty())
    {
        return {}; // Return default value for type T
    }
    W data = arr[front];
    front = (front + 1) % capacity;
    size--;
    return data;
}

W FifoSaSw::peek()
{
    if (isEmpty())
    {
        return {}; // Return default value for type T
    }
    return arr[front];
}

bool FifoSaSw::isEmpty() const
{
    return size == 0;
}

bool FifoSaSw::isFull() const
{
    return size == capacity;
}

int FifoSaSw::getSize() const
{
    return size;
}
