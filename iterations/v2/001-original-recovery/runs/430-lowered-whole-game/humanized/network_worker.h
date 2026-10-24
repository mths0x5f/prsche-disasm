/* Network worker: only the address mode at +0BCh is known here. */
#ifndef HUMANIZED_NETWORK_WORKER_H
#define HUMANIZED_NETWORK_WORKER_H

struct NetworkWorker {
    unsigned char unknown_00[0xbc];
    unsigned long address_mode;    /* 1: text addresses; above 3: a provider resolves them */
};

#endif
