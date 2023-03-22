// Helper functions for music

#include <cs50.h>
#include <string.h>
#include "helpers.h"
#include <math.h>
#include <ctype.h>

// Converts a fraction formatted as X/Y to eighths
int duration(string fraction)
{
    int x, y;
    x = fraction[0] - '0';
    y = fraction[2] - '0';
    x = x * 8 / y;
    return (x);
}

// Calculates frequency (in Hz) of a note
int frequency(string note)
{
    int i, letter_difference, octave_difference;
    char note_letter[3];
    long hertz;
    double n;

    string note_list_sharp[12] = {"C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"};
    string note_list_flat[12] = {"C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"};

    //this section recognizes if the note supplied has a sharp or flat, and puts it into a useful format
    note_letter[0] = note[0];
    if (note[1] == '#' || note[1] == 'b')
    {
        note_letter[1] = note[1];
        note_letter[2] = '\0';
        octave_difference = note[2] - '0';
    }
    else
    {
        note_letter[1] = '\0';
        octave_difference = note[1] - '0';
    }

    //this section compares the note supplied to the list of notes and determines how many semitones it is from "A"
    for (i = 0; i < 12; i++)
    {
        if (!strcmp(note_list_sharp[i], note_letter) || !strcmp(note_list_flat[i], note_letter))
        {
            letter_difference = i - 9;
        }
    }

    //this section calculates the number of octaves that the note is away from the 4th, then converts it into semitones
    octave_difference = 12 * (octave_difference - 4);

    //this section calculates n, and then solves for the hertz usign the supplied equation

    n = octave_difference + letter_difference;
    hertz = round(pow(2.0, (n / 12)) * 440);
    return hertz;
}

// Determines whether a string represents a rest
bool is_rest(string s)
{
    if (!strcmp(s, ""))
    {
        return 1;
    }

    else
    {
        return 0;
    }
}
