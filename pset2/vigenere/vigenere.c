//this program accepts a command line input of a key, then prompts the user for plain text. It then encrypts the plain text using
//the key.

#include <stdio.h>
#include <cs50.h>
#include <string.h>
#include <ctype.h>
#include <math.h>
int main(int argc, string argv[])
{
    int i, key_len, txt_len, j = 0;
    string key, plain_text;

    //check that there is only ONE word entered for the key
    if (argc != 2)
    {
        printf("Enter ONLY one key (no spaces)\n");
        return (1);
    }

    key_len = strlen(argv[1]);
    key = argv[1];
    int int_val[key_len];

    //check that the key contains ONLY capital or lower letters
    for (i = 0; i < key_len; i++)
    {
        if (key[i] < 'A' || key[i] > 'z' || (key[i] > 'Z' && key[i] < 'a'))
        {
            printf("Key must contain ONLY letters\n");
            return (1);
        }
    }

    //convert the key into all capital letters, then converts the characters into useful integer values
    for (i = 0; i < key_len; i++)
    {
        key[i] = toupper(key[i]);
        int_val[i] = key[i] - 'A';
    }

    //accepts plain text input from the user and stores its length
    plain_text = get_string("plaintext: ");
    txt_len = strlen(plain_text);

    //converts the plain text into a cipher, ONLY if it is a letter
    for (i = 0; i < txt_len; i++)
    {
        if ((plain_text[i] >= 'A' && plain_text[i] <= 'Z') || (plain_text[i] >= 'a' && plain_text[i] <= 'z'))
        {
            printf("plain text character: %c key number: %i ", plain_text[i], int_val[j]);
            if (plain_text[i] <= 'Z')
            {
                plain_text[i] = (plain_text[i] - 'A' + int_val[j]) % 26 + 'A';
            }
            if (plain_text[i] >= 'a')
            {
                plain_text[i] = (plain_text[i] - 'a' + int_val[j]) % 26 + 'a';
            }
            j++;
            printf("cipher character: %c\n", plain_text[i]);
            if (j >= key_len)
            {
                j = 0;
            }
        }
    }
    printf("ciphertext: %s\n", plain_text);
    return (0);
}