# Questions

## What's `stdint.h`?

My understanding is that this is the header file which allows us to specify the number of bits we want to group together. This lets
me build thing slike a 16 bit or a 32 bit image--the more bits I choose to use, the more color options I have available to me.

## What's the point of using `uint8_t`, `uint32_t`, `int32_t`, and `uint16_t` in a program?

My understanding is that these are generally agreed on data structures to interpret a series of bits in a meaningful way.


## How many bytes is a `BYTE`, a `DWORD`, a `LONG`, and a `WORD`, respectively?

BYTE = 1 byte
DWORD = 4 bytes
LONG = 4 bytes
WORD = 2 bytes

## What (in ASCII, decimal, or hexadecimal) must the first two bytes of any BMP file be? Leading bytes used to identify file formats (with high probability) are generally called "magic numbers."

"BM" Must be the first two bytes to identify a BMP file.

## What's the difference between `bfSize` and `biSize`?

bfsize is the size of the bmp file, it bits, of the file. biSize is the number of bits required by the structure.

## What does it mean if `biHeight` is negative?

If biHeight is negative, the bitmap is a top-down DIB and its origin is the upper-left corner.

## What field in `BITMAPINFOHEADER` specifies the BMP's color depth (i.e., bits per pixel)?

biBitcount

## Why might `fopen` return `NULL` in lines 24 and 32 of `copy.c`?

if fopen cannot find the file location that is is pointing towards, it might return a null value.

## Why is the third argument to `fread` always `1` in our code?

Because we always want the function to execute.

## What value does line 65 of `copy.c` assign to `padding` if `bi.biWidth` is `3`?

Line 63 makes certain that each line contains a multiple of 4 bytes. If bi.biWidth is 3, then we have
padding = (4 - (bi.biWidth * sizeof(RGBTRIPLE)) % 4) % 4;
padding = (4 - (3 * 3) % 4) % 4;
padding = (4 - 9 % 4) % 4;
padding = (4 - 1) % 4;
padding = 3

## What does `fseek` do?

FSeek lets me choose the location a pointer is pointign towards

## What is `SEEK_CUR`?

This is the current location of the pointer

## Whodunit?

It was Professor Plum with the candlestick in the library!
