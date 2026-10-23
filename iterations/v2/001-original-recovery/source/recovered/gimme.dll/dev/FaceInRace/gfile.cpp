// FaceInRace's implementation of the GIMEX application callbacks: guarded memory blocks and
// buffered files.  gimme.dll 3a43b0f6…, VA 10003170–100049b4 (built with /GZ like the rest of
// the FaceInRace project, D:\dev\FaceInRace\Debug\FaceInRace.pdb).  The source file name is
// not attested.

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>

#include "../../_sem_arquivo/gimex/gimex.h"

int gwopenbackupmode = 3;
int(__cdecl *gerror)(const char *format, ...) = printf;

// Live block count (0x10449bb0); only ever incremented and decremented.
static int gallocblocks;

static const char gmemhead[4] = { 'G', 'M', 'E', 'M' };
static const char gmemtail[4] = { 'G', 'E', 'N', 'D' };
static const char gmemfreed[4] = { 'G', 'F', 'R', 'E' };

// 10003170.  Each block is framed as 'GMEM', size, data, 'GEND'; new data is filled with 0x66.
void *GCALL galloc(int size)
{
    if (size < 1)
    {
        gerror("galloc - INVALID SIZE %ld\n", size);
        return NULL;
    }
    char *block = (char *)malloc(size + 12);
    if (block == NULL || block == (char *)-1)
    {
        gerror("galloc - FAILED. OUT OF MEMORY. SIZE REQUESTED %ld\n", size);
        return NULL;
    }
    memcpy(block, gmemhead, 4);
    *(int *)(block + 4) = size;
    memcpy(block + 8 + size, gmemtail, 4);
    memset(block + 8, 0x66, size);
    ++gallocblocks;
    return block + 8;
}

// 100032a0.  Pointers within 0x7ff of null are rejected; freed data is filled with 0x78 and the
// head is retagged 'GFRE' so a second free is reported.
int GCALL gfree(void *memory)
{
    char *data = (char *)memory;
    int ok = 0;
    if ((int)data > -0x800 && (int)data < 0x800)
    {
        gerror("gfree - ATTEMPT TO FREE NULL POINTER\n");
        return ok;
    }
    int size = *(int *)(data - 4);
    if (memcmp(data - 8, gmemhead, 4) == 0 && size > 0 && size < 0x6400000 &&
        memcmp(data + size, gmemtail, 4) == 0)
        ok = 1;
    if (!ok)
    {
        if (memcmp(data - 8, gmemfreed, 4) == 0)
            gerror("gfree - ATTEMPT TO FREE MEMORY TWICE\n");
        else
            gerror("gfree - SENTINAL CORRUPTED; PROBABLE MEMORY DATA CORRUPTION\n");
    }
    else
    {
        memcpy(data - 8, gmemfreed, 4);
        memset(data, 0x78, size);
        free(data - 8);
        --gallocblocks;
    }
    return ok;
}

// 10003440.
int ggetm(const void *source, int count)
{
    const unsigned char *byte = (const unsigned char *)source;
    int value = 0;
    while (count--)
        value = value * 256 + *byte++;
    return value;
}

// 100034c0.
int ggeti(const void *source, int count)
{
    const unsigned char *byte = (const unsigned char *)source;
    int shift = 0;
    int value = 0;
    while (count--)
    {
        value += (int)*byte++ << (shift & 31);
        shift += 8;
    }
    return value;
}

// 10003550.
void gputm(void *destination, int value, int count)
{
    unsigned char *byte = (unsigned char *)destination;
    value <<= ((4 - count) * 8) & 31;
    for (; count; --count)
    {
        *byte++ = (unsigned char)((unsigned)value >> 24);
        value <<= 8;
    }
}

// 100035e0.
void gputi(void *destination, unsigned value, int count)
{
    unsigned char *byte = (unsigned char *)destination;
    for (; count; --count)
    {
        *byte++ = (unsigned char)value;
        value >>= 8;
    }
}

static void InitStream(GSTREAM *stream, FILE *file, int length, int writable, int mode, const char *name)
{
    stream->file = file;
    stream->position = 0;
    stream->length = length;
    stream->cursor = stream->buffer;
    stream->end = stream->buffer;
    stream->writable = writable;
    stream->dirty = 0;
    stream->mode = mode;
    stream->bufferstart = 0;
    strcpy(stream->name, name);
}

// 10003650.  "con:" reads standard input.
GSTREAM *GCALL gopen(const char *name)
{
    FILE *file;
    int mode;
    int length = 0;
    if (strncmp(name, "con:", 4) == 0)
    {
        file = stdin;
        mode = 0;
    }
    else
    {
        file = fopen(name, "rb");
        mode = 1;
    }
    GSTREAM *stream = NULL;
    if (file)
    {
        if (fseek(file, 0, SEEK_END) != 0)
        {
            gerror("gopen - SEEK ON OPEN FAILED (%s)\n", name);
        }
        else
        {
            length = ftell(file);
            fseek(file, 0, SEEK_SET);
            stream = (GSTREAM *)galloc(sizeof(GSTREAM));
            if (!stream)
                gerror("gopen - UNABLE TO ALLOCATE MEMORY FOR FILE HANDLE (%s)\n", name);
            else
                InitStream(stream, file, length, 0, mode, name);
        }
    }
    return stream;
}

// 10003b10.  Copies name and replaces its extension (if the last path element has one).
static void ReplaceExtension(char *destination, const char *name, const char *extension)
{
    strcpy(destination, name);
    char *dot = destination + strlen(destination) - 1;
    while (dot > destination && *dot != '.' && *dot != ':' && *dot != '/' && *dot != '\\')
        --dot;
    if (*dot != '.')
        dot = destination + strlen(destination);
    *dot = '\0';
    strcat(destination, extension);
}

// 10003c20.
static int IsReadOnly(const char *name)
{
    struct _stat status;
    return _stat(name, &status) != -1 && (status.st_mode & _S_IREAD) && !(status.st_mode & _S_IWRITE);
}

// 10003cb0.
static int IsDirectory(const char *name)
{
    struct _stat status;
    return _stat(name, &status) != -1 && (status.st_mode & _S_IFDIR);
}

// 10003840.  In backup modes 2 and 3 the data goes to "<name>.tm1"; gclose swaps it in.
GSTREAM *GCALL gwopen(const char *name)
{
    FILE *file = NULL;
    GSTREAM *stream = NULL;
    int mode = gwopenbackupmode;
    char writename[512];
    writename[0] = '\0';
    if (strncmp(name, "con:", 4) == 0)
    {
        file = stdout;
        mode = 0;
    }
    else if (IsReadOnly(name))
    {
        gerror("gwopen - ATTEMPT TO OPEN READONLY FILE FOR WRITING (%s)\n", name);
    }
    else if (IsDirectory(name))
    {
        gerror("gwopen - ATTEMPT TO OPEN DIRECTORY FOR WRITING (%s)\n", name);
    }
    else
    {
        if (mode == 2 || mode == 3)
            ReplaceExtension(writename, name, ".tm1");
        else
            strcpy(writename, name);
        file = fopen(writename, "w+b");
        if (!file)
        {
            // The original reports the failure even when the "wb" retry succeeds.
            file = fopen(writename, "wb");
            gerror("gwopen - UNABLE TO OPEN FILE FOR WRITE (%s)\n", writename);
        }
    }
    if (file)
    {
        stream = (GSTREAM *)galloc(sizeof(GSTREAM));
        if (!stream)
        {
            gerror("gwopen - UNABLE TO ALLOCATE MEMORY FOR FILE HANDLE (%s)\n", name);
        }
        else
        {
            InitStream(stream, file, 0, 1, mode, name);
            strcpy(stream->writename, writename);
        }
    }
    return stream;
}

// 10003ef0.  Writes back a dirty buffer and empties it.
static int gwriteflush(GSTREAM *stream)
{
    int written = 0;
    if (stream->dirty && stream->writable)
    {
        fseek((FILE *)stream->file, stream->bufferstart, SEEK_SET);
        written = (int)fwrite(stream->buffer, 1, stream->end - stream->buffer, (FILE *)stream->file);
        if (written < stream->end - stream->buffer)
            gerror("gwriteflush - OUT OF DISK SPACE\n");
        stream->dirty = 0;
    }
    stream->end = stream->buffer;
    stream->cursor = stream->end;
    fflush((FILE *)stream->file);
    return written;
}

// 10003d20.  Backup mode 2 keeps the previous file as ".bak", mode 3 drops it.
int GCALL gclose(GSTREAM *stream)
{
    int ok = 1;
    if (stream)
    {
        gwriteflush(stream);
        int mode = stream->mode;
        if (mode)
        {
            ok = fclose((FILE *)stream->file) == 0;
            if (ok && (mode == 2 || mode == 3))
            {
                char previous[512];
                ReplaceExtension(previous, stream->name, ".tm2");
                remove(previous);
                rename(stream->name, previous);
                ok = rename(stream->writename, stream->name) == 0;
                if (ok)
                {
                    if (mode == 2)
                    {
                        char backup[512];
                        ReplaceExtension(backup, stream->name, ".bak");
                        remove(backup);
                        rename(previous, backup);
                    }
                    else
                    {
                        remove(previous);
                    }
                }
            }
        }
        ok &= gfree(stream);
    }
    return ok;
}

// 10004020.  Serves what is buffered, then reads whole 8 KB blocks directly and refills.
int GCALL gread(GSTREAM *stream, void *buffer, int count)
{
    unsigned char *destination = (unsigned char *)buffer;
    int buffered = 0;
    int direct = 0;
    if (!stream)
        return 0;
    if (count < 0)
        count = 0;
    int available = (int)(stream->end - stream->cursor);
    int take = count < available ? count : available;
    if (take > 0)
    {
        memcpy(destination, stream->cursor, take);
        stream->cursor += take;
        stream->position += take;
        destination += take;
        count -= take;
        buffered += take;
    }
    int remaining = stream->length - stream->position;
    count = count < remaining ? count : remaining;
    if (count < 0)
    {
        gerror("gread - ATTEMPT TO READ PAST END OF FILE\n");
    }
    else if (stream->end == stream->cursor && count != 0)
    {
        int block = (stream->position + count) / GSTREAM_BUFFER_SIZE * GSTREAM_BUFFER_SIZE;
        gwriteflush(stream);
        if (stream->position < block)
        {
            direct = (int)fread(destination, 1, block - stream->position, (FILE *)stream->file);
            destination += direct;
            count -= direct;
        }
        stream->bufferstart = block;
        int fill = stream->length - block < GSTREAM_BUFFER_SIZE + 1 ? stream->length - block : GSTREAM_BUFFER_SIZE;
        fread(stream->buffer, 1, fill, (FILE *)stream->file);
        memcpy(destination, stream->cursor, count);
        direct += count;
        stream->cursor += count;
        stream->end += fill;
        stream->position += direct;
    }
    return buffered + direct;
}

// 10004310.
int GCALL gwrite(GSTREAM *stream, const void *buffer, int count)
{
    const unsigned char *source = (const unsigned char *)buffer;
    int written = 0;
    if (!stream)
        return 0;
    if (!stream->writable)
    {
        gerror("gwrite - ATTEMPT TO WRITE TO A READ ONLY FILE\n");
        return 0;
    }
    int room = (int)(stream->buffer + GSTREAM_BUFFER_SIZE - stream->cursor);
    int take = count < room ? count : room;
    if (take > 0)
    {
        memcpy(stream->cursor, source, take);
        stream->cursor += take;
        stream->position += take;
        if (stream->end < stream->cursor)
            stream->end = stream->cursor;
        if (stream->length < stream->position)
            stream->length = stream->position;
        stream->dirty = 1;
        source += take;
        count -= take;
        written += take;
    }
    if (stream->end == stream->cursor && count != 0)
    {
        int block = (stream->position + count) / GSTREAM_BUFFER_SIZE * GSTREAM_BUFFER_SIZE;
        gwriteflush(stream);
        if (block < stream->length)
        {
            int fill = stream->length - block < GSTREAM_BUFFER_SIZE + 1 ? stream->length - block : GSTREAM_BUFFER_SIZE;
            fseek((FILE *)stream->file, block, SEEK_SET);
            fread(stream->buffer, 1, fill, (FILE *)stream->file);
            stream->end += fill;
        }
        fseek((FILE *)stream->file, stream->position, SEEK_SET);
        int direct = (int)fwrite(source, 1, block - stream->position, (FILE *)stream->file);
        if (direct < block - stream->position)
        {
            gerror("gwrite - OUT OF DISK SPACE\n");
        }
        else
        {
            stream->position += direct;
            written += count;
            count -= direct;
            memcpy(stream->buffer, source + direct, count);
            stream->position += count;
            stream->bufferstart = block;
            stream->cursor += count;
            if (stream->length < stream->position)
                stream->length = stream->position;
            if (stream->end < stream->cursor)
                stream->end = stream->cursor;
            stream->dirty = 1;
        }
    }
    return written;
}

// 100046e0.  Seeks inside the buffer when possible; otherwise reloads the 8 KB block.
int GCALL gseek(GSTREAM *stream, int position)
{
    int ok = 1;
    if (stream)
    {
        if (position < 0)
        {
            position = 0;
            ok = 0;
        }
        else if (stream->length < position && !stream->writable)
        {
            position = stream->length;
            ok = 0;
        }
        int delta = position - stream->position;
        stream->position += delta;
        if (delta < (int)(stream->buffer - stream->cursor) || (int)(stream->end - stream->cursor) < delta)
        {
            int block = stream->position / GSTREAM_BUFFER_SIZE * GSTREAM_BUFFER_SIZE;
            gwriteflush(stream);
            ok = fseek((FILE *)stream->file, block, SEEK_SET) == 0 && ok;
            stream->bufferstart = block;
            if (block < stream->length)
            {
                int fill = stream->length - block < GSTREAM_BUFFER_SIZE + 1 ? stream->length - block : GSTREAM_BUFFER_SIZE;
                fread(stream->buffer, 1, fill, (FILE *)stream->file);
                stream->end += fill;
                stream->cursor += stream->position - block;
            }
            else
            {
                int gap = stream->position - block;
                memset(stream->buffer, 0, gap);
                stream->end = stream->buffer + gap;
                stream->cursor = stream->end;
            }
        }
        else
        {
            stream->cursor += delta;
        }
    }
    return ok;
}

// 10004960.
int GCALL glen(GSTREAM *stream)
{
    return stream->length;
}

// 10004990.
int GCALL gtell(GSTREAM *stream)
{
    return stream->position;
}
