/* 00580b70: The n-th element (0-based) of a singly linked list, or 0 when it is shorter. */
struct ListNode {
    ListNode *next;
};

ListNode * __cdecl network_list_at_00580b70(ListNode **list, unsigned long n)
{
    ListNode *node = *list;

    while (node) {
        if (n-- == 0)
            return node;
        node = node->next;
    }
    return 0;
}
