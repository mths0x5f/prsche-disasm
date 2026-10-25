/* 0055c260: The address 4 bytes before a network object (its allocation header). */
void * __cdecl network_object_header_0055c260(void *object)
{
    return (char *)object - 4;
}
