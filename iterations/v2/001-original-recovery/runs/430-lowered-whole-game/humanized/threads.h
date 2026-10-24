/* Thread record of the game's thread layer: 28 bytes, one per thread it creates. */
#ifndef HUMANIZED_THREADS_H
#define HUMANIZED_THREADS_H

struct ThreadRecord {
    void *handle;                  /* Win32 thread handle */
    unsigned long stack;
    unsigned long priority;
    unsigned long flags;
    unsigned long id;              /* Win32 thread id */
    unsigned long serial;
    unsigned long slot;
};

#endif
