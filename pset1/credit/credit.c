#include <stdio.h>
#include <cs50.h>
#include <math.h>
int main(void)
{
    //double power;
    int i, checksum = 0, j, digit, first_digit, second_digit;
    long long n, digit_check, power;

    //accepts credit card input for positive numbers 13, 15, or 16 digits long
    do
    {
        n = get_long_long("Enter credit card number: ");
        digit_check = n;
        i = 0;

        //checks the length of the credit card number input, stores length in variable "i". Also stores the firt two digits.
        do
        {
            digit_check = digit_check / 10;
            i++;
            if (digit_check < 100 && digit_check > 9)
            {
                second_digit = digit_check % 10;
                first_digit = (digit_check - second_digit) / 10;
            }
        }

        while (digit_check >= 1);
    }
    while (n < 0);


    //builds the checksum value based on the supplied formula
    for (j = 0; j < i; j++)
    {
        power = pow(10, j);
        digit = ((n % (power * 10)) - (n % power)) / power;
        if (j % 2 == 0)
        {
            checksum = checksum + digit;
        }
        else
        {
            if ((digit * 2) < 10)
            {
                checksum = checksum + (2 * digit);
            }
            else
            {
                checksum = checksum + ((digit * 2) % 10) + (((digit * 2) - ((digit * 2) % 10)) / 10);
            }
        }
    }

    //this secion determind what type of card, if any, the credit card belongs to.
    if (checksum % 10 == 0)
    {
        if (i == 15 && first_digit == 3 && (second_digit == 4 || second_digit == 7))
        {
            printf("AMEX\n");
        }
        else
        {
            if (i == 16 && first_digit == 5 && second_digit > 0 && second_digit < 6)
            {
                printf("MASTERCARD\n");
            }
            else
            {
                if (first_digit == 4 && (i == 13 || i == 16))
                {
                    printf("VISA\n");
                }
                else
                {
                    printf("INVALID\n");
                }
            }
        }
    }
    else
    {
        printf("INVALID\n");
    }
}