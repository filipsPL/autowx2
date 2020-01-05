#!/bin/bash

# Need an input parameter, which should come in the form of a shell
input=""

# Infinite loop. Keep checking input until told otherwise.
while [ true ]
do
    read input

    # If the input is the command to break out of the loop, exit
    # the loop.
    if [ "$input" = "--exit" ];
    then
        break
    fi

    # We are going to assume it is a command.
    eval $input

    # Use a random string to notify when the command has finished
    # running
    echo "SQsw48V8JZLwGOscVeuO"

    # End of loop
done

echo "End of shell scripts."

return 0
