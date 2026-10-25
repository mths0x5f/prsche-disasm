/* 00529a20: Points a deque iterator at the start of a 512-byte node. */
struct DequeIterator {
    void *unknown_00;
    char *current;
    char *node_end;
    char **node;
    void set_node(char **new_node);
};

void DequeIterator::set_node(char **new_node)
{
    char *start;

    node = new_node;
    start = *new_node;                  /* after the store and only once, as the original: they may overlap */
    current = start;
    node_end = start + 0x200;
}
