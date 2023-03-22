// Copies a BMP file

#include <stdio.h>
#include <stdlib.h>

#include "bmp.h"

int main(int argc, char *argv[])
{
    // ensure proper usage
    if (argc != 4)
    {
        fprintf(stderr, "Usage: copy infile outfile\n");
        return 1;
    }

    // remember integer input
    int factor = atoi(argv[1]);

    // remember filenames
    char *infile = argv[2];
    char *outfile = argv[3];



    // open input file
    FILE *inptr = fopen(infile, "r");
    if (inptr == NULL)
    {
        fprintf(stderr, "Could not open %s.\n", infile);
        return 2;
    }

    // open output file
    FILE *outptr = fopen(outfile, "w");
    if (outptr == NULL)
    {
        fclose(inptr);
        fprintf(stderr, "Could not create %s.\n", outfile);
        return 3;
    }

    // read infile's BITMAPFILEHEADER
    BITMAPFILEHEADER bf;
    fread(&bf, sizeof(BITMAPFILEHEADER), 1, inptr);

    // read infile's BITMAPINFOHEADER
    BITMAPINFOHEADER bi;
    fread(&bi, sizeof(BITMAPINFOHEADER), 1, inptr);

    // ensure infile is (likely) a 24-bit uncompressed BMP 4.0
    if (bf.bfType != 0x4d42 || bf.bfOffBits != 54 || bi.biSize != 40 ||
        bi.biBitCount != 24 || bi.biCompression != 0)
    {
        fclose(outptr);
        fclose(inptr);
        fprintf(stderr, "Unsupported file format.\n");
        return 4;
    }

    //scale the outfile's width and height
    BITMAPFILEHEADER bfnew = bf;
    BITMAPINFOHEADER binew = bi;
    binew.biWidth = factor * binew.biWidth;
    binew.biHeight = factor * binew.biHeight;

    // determine padding for scanlines
    int padding = (4 - (bi.biWidth * sizeof(RGBTRIPLE)) % 4) % 4;
    int paddingnew = (4 - (binew.biWidth * sizeof(RGBTRIPLE)) % 4) % 4;
    printf("bi.biwidth = %i\n", bi.biWidth);
    printf("Padding = %i\n", padding);
    printf("binew.biwidth = %i\n", binew.biWidth);
    printf("Padding new = %i\n", paddingnew);


    //update the new image size
    binew.biSizeImage = ((sizeof(RGBTRIPLE) * binew.biWidth) + paddingnew) * abs(binew.biHeight);

    //update the new file size
    bfnew.bfSize = binew.biSizeImage + sizeof(BITMAPFILEHEADER) + sizeof(BITMAPINFOHEADER);

    // write outfile's BITMAPFILEHEADER
    fwrite(&bfnew, sizeof(BITMAPFILEHEADER), 1, outptr);

    // write outfile's BITMAPINFOHEADER
    fwrite(&binew, sizeof(BITMAPINFOHEADER), 1, outptr);

    // iterate over infile's scanlines
    for (int i = 0, biHeight = abs(bi.biHeight); i < biHeight; i++)
    {
        for (int m =0; m < factor; m++)
        {
            // iterate over pixels in scanline
            for (int j = 0; j < bi.biWidth; j++)
            {
                // temporary storage
                RGBTRIPLE triple;
                // read RGB triple from infile
                fread(&triple, sizeof(RGBTRIPLE), 1, inptr);

                // write RGB triple to outfile
                for (int k = 0; k < factor; k++)
                {
                    fwrite(&triple, sizeof(RGBTRIPLE), 1, outptr);
                }

            }

            for (int k = 0; k < paddingnew; k++)
            {
                fputc(0x00, outptr);
            }
            //skip padding on old file
            fseek(inptr, padding, SEEK_CUR);
            //move cursor back to previous line on original file
            fseek(inptr, -bi.biWidth * sizeof(RGBTRIPLE) - padding, SEEK_CUR);
        }

        fseek(inptr, bi.biWidth * sizeof(RGBTRIPLE) + padding, SEEK_CUR);
    }

    // close infile
    fclose(inptr);

    // close outfile
    fclose(outptr);

    // success
    return 0;
}
