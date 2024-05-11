#!/usr/bin/env python3
"""Preliminary exercises for Part IIA Project GF2."""
import sys
from mynames import MyNames


def open_file(path):
    """Open and return the file specified by path."""
    try:
        file = open(path, 'r')
    except Exception:
        print(f"{path} is an Invalid File Path")
        sys.exit()
    return file


def get_next_character(input_file):
    """Read and return the next character in input_file."""
    try:
        next_char = input_file.read(1)
        return next_char
    except Exception:
        return ""


def get_next_non_whitespace_character(input_file):
    """Seek and return the next non-whitespace character in input_file."""

    next_nws_char = input_file.read(1)

    if next_nws_char.isspace():
        pass
    elif next_nws_char == '\n':
        pass
    else:
        return next_nws_char


def get_next_number(input_file):
    """Seek the next number in input_file.
    Return the number (or None) and the next non-numeric character.
    """
    list_arr = []
    num_chars = ''
    next_char = input_file.read(1)

    # Get to the next encounter of digit
    while not next_char.isdigit():
        pointer = input_file.tell()
        next_char = input_file.read(1)
        if input_file.tell() == pointer:
            return None
    
    # If the next_char is a digit (we haven't got to the end of the file)
    if next_char.isdigit():
        while next_char.isdigit():
            num_chars += next_char
            next_char = input_file.read(1)

    # End of last while loop, it will break once the next char is not a num
    non_dig_char = next_char
    list_arr.append(int(num_chars))
    list_arr.append(non_dig_char)

    return list_arr


def get_next_name(input_file):
    """Seek the next name string in input_file.
    Return the name string (or None) and the next non-alphanumeric character.
    """
    name_chars = ''
    next_char = input_file.read(1)

    while not next_char.isalpha():
        pointer = input_file.tell() 
        next_char = input_file.read(1)
        if input_file.tell() == pointer:
            return None

    if next_char.isalpha():
        while next_char.isalnum():
            name_chars += next_char
            next_char = input_file.read(1)
        
    return name_chars


def main():
    """Preliminary exercises for Part IIA Project GF2."""

    # Check command line arguments
    arguments = sys.argv[1:]

    if len(arguments) != 1:
        print("Error! One command line argument is required.")
        sys.exit()

    else:
        filename = arguments[0]
        print("\nNow opening file...")
        
        file = open_file(filename)        
        char_count = len(file.read())
        print("\nNow reading file...")
                
        for i in range(char_count):
            print(get_next_character(file), end='')

        file.seek(0)
        
        print("\nNow skipping spaces...")

        for i in range(char_count):
            nws_char = get_next_non_whitespace_character(file) 
            if nws_char is not None: 
                print(nws_char)
            else: pass

        print("\nNow reading numbers...")
        # Print out all the numbers in the file
        file.seek(0)

        for i in range(char_count):
            num = get_next_number(file)

            if num is not None: 
                num = num[0]
                print(num)
            else: 
                break

        print("\nNow reading names...")
        # Print out all the names in the file

        file.seek(0)

        for i in range(char_count):  
            name = get_next_name(file)
            if name is not None: 
                print(name)
            else: 
                pass
            
        file.seek(0)

        print("\nNow censoring bad names...")
        # Print out only the good names in the file
        name = MyNames()
        bad_name_ids = [name.lookup("Terrible"), name.lookup("Horrid"),
                         name.lookup("Ghastly"), name.lookup("Awful")]

        for i in range(char_count):

            curr_name = get_next_name(file)
            if curr_name is not None:
                if name.lookup(curr_name) not in bad_name_ids:                     
                    print(curr_name)
            else: 
                pass


if __name__ == "__main__":
    main()
