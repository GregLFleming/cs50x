//Searches for and recovers deleted jpegs on a memory file.

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

int main(int argc, char *argv[])
{
    //checks that exactly one line argument was given
    if (argc != 2)
    {
        fprintf(stderr, "Exactly ONE line argument must be entered.\n");
        return 1;
    }

    //stores the name of the raw data file
    char *rawdata = argv[1];

    // open input file
    FILE *inptr = fopen(rawdata, "r");
    if (inptr == NULL)
    {
        fprintf(stderr, "Could not open %s.\n", rawdata);
        return 2;
    }

    int filecount = 0;
    uint8_t buffer[512];
    char output_file_name[8];

    //creates the very first jpeg file
    sprintf(output_file_name, "%03i.jpg", filecount);
    FILE *outptr = fopen(output_file_name, "w");
    filecount++;

    //finds the very first jpeg and writes a single block
    while(!(buffer[0] == 0xff && buffer[1] == 0xd8 && buffer[2] == 0xff))
    {
        fread(buffer, 1, 512, inptr);
        if (buffer[0] == 0xff && buffer[1] == 0xd8 && buffer[2] == 0xff)
        {
            //writes the very first block into the new jpeg
            fwrite(buffer, 1, 512, outptr);
        }
    }

    int newfilecount = 0;

    //writes blocks of data until end of file is detected. Whenever a new jpeg is detected, the old jpeg is closed and
    //a new jpeg file is created.
    int end_check = 512;
    while(end_check == 512)
    {
        end_check = fread(buffer, 1, 512, inptr);
        if (buffer[0] == 0xff && buffer[1] == 0xd8 && buffer[2] == 0xff)
        {
            //closes old jpeg and creates new jpeg
            newfilecount++;
            fclose(outptr);
            sprintf(output_file_name, "%03i.jpg", filecount);
            outptr = fopen(output_file_name, "w");
            filecount++;
        }

        //copies the jpeg block onto the new jpeg file
        if(end_check == 512)
        {
            fwrite(buffer, 1, 512, outptr);
        }
    }
    return(0);
}