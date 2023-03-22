#include <stdio.h>
#include <cs50.h>

int main(void)
{

    int n, i, j;

    //obtain the number of layers in the pyramid
    do
    {
        n = get_int("Height: ");
    }
    while (n < 0 || n > 23);

    //print the pyramid to screen
    for (i = 0; i < n; i++)
    {
        for (j = 0; j < n + 3 + i; j++)
        {
            if (j < n - i - 1 || j == n || j == n + 1) //this statement judges when there should be a space present
            {
                printf(" ");
            }
            else
            {
                printf("#");
            }
        }
        printf("\n");
    }
}