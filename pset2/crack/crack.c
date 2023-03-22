#include <stdio.h>
#include <cs50.h>
#include <string.h>
#include <crypt.h>
#define _XOPEN_SOURCE
#include <unistd.h>

int main(int argc, string argv[])
{

    char salt[3], password_test[6];
    string input, hashed_test;
    int i, j;

    //check that there is only ONE line entered for the hashed password
    if (argc != 2)
    {
        printf("Enter ONLY one hashed password (no spaces)\n");
        return (1);
    }

    input = argv[1];
    input[13] = '\0';
    salt[0] = input[0];
    salt[1] = input[1];
    salt[2] = '\0';

    for (i = 0; i < 5; i++)
    {
        //reset all of the test values to "A", sets the number of digits to test
        for (j = 0; j <= i; j++)
        {
            password_test[j] = 'A';
            password_test[j + 1] = '\0';
        }

        //test every possible 5 digit combination of letters. if the hash is found, the program ends.
        for (password_test[0] = 'A'; password_test[0] <= 'z'; password_test[0]++)
        {
            hashed_test = crypt(password_test, salt);
            if (!strcmp(hashed_test, input))
            {
                printf("%s\n", password_test);
                return (0);
            }
            if (i > 0)
            {
                for (password_test[1] = 'A'; password_test[1] <= 'z'; password_test[1]++)
                {
                    hashed_test = crypt(password_test, salt);
                    if (!strcmp(hashed_test, input))
                    {
                        printf("%s\n", password_test);
                        return (0);
                    }
                    if (i > 1)
                    {
                        for (password_test[2] = 'A'; password_test[2] <= 'z'; password_test[2]++)
                        {
                            hashed_test = crypt(password_test, salt);
                            if (!strcmp(hashed_test, input))
                            {
                                printf("%s\n", password_test);
                                return (0);
                            }
                            if (i > 2)
                            {
                                for (password_test[3] = 'A'; password_test[3] <= 'z'; password_test[3]++)
                                {
                                    hashed_test = crypt(password_test, salt);
                                    if (!strcmp(hashed_test, input))
                                    {
                                        printf("%s\n", password_test);
                                        return (0);
                                    }
                                    if (i > 3)
                                    {
                                        for (password_test[4] = 'A'; password_test[4] <= 'z'; password_test[4]++)
                                        {
                                            hashed_test = crypt(password_test, salt);
                                            if (!strcmp(hashed_test, input))
                                            {
                                                printf("%s\n", password_test);
                                                return (0);
                                            }
                                        }
                                    }
                                }
                            }

                        }
                    }
                }
            }

        }
    }

    printf("Password not found.\n");
    return (1);
}