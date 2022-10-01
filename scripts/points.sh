#!/bin/bash

# WARNING: all functions act locally, i.e. the working directory and its child .git repository will be edited!

# Returns all folder names where there some assignments were handed in with the given number.
# -> ARGS: $1 = assignment number in the format XX
function submissions() {
    num=$(echo "$1" | sed -r 's/(0*)([^0]+.*)/\2/g')
    find . -mindepth 2 -name "*$num*" -not -empty |
        grep -vE '(git)|(feedback)' |
        cut -d/ -f2 |
        sort -u
}

# Retrieves all point headers per assignment OR total points of students in /feedback/*.
# -> ARGS: $1 = either assignment number in format XX or with keyword "total"
function points() {
    if [ "$1" = "total" ]; then
        for name in $(find . -maxdepth 1 -type d -not -path '.'); do
            points=$(cat $name/feedback/* |
                sed -r 's/\[(.{1,3})\/.+\]/\1/' |
                grep -E '^[0-9.]{1,3}' |
                awk '{total = total + $1}END{print total}')
            echo "$(echo $name | cut -d/ -f2): $points"
        done
    elif [[ "$1" =~ ^[0-9]{2}$ ]]; then
        find . -wholename "*/feedback" -type d -exec bash -c "
            sed -r 's:^[^/]*/([^/]+)/.*:\1\: :' <<< '{}' |
            tr -d '\n' && (head -n2 '{}/assignment$1.txt' |
            tail -n1)" \; |
            sort
    fi
}
