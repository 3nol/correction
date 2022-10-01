#!/bin/bash

# WARNING: all functions act locally, i.e. the working directory and its child .git repository will be edited!

# Initializes all .git repositories from a list of names, given by an input file.
# Also creates the needed folders "concatenated" and "feedback" for correction.
# -> ARGS: $1 = path of students list file
function init-all() {
    GIT_HOST="https://blabla.com/group"

    if ! [ -z "$1" ]; then
        for name in $(cat $1); do
            git clone "$GIT_HOST/$name.git" &&
                cd $name &&
                mkdir concatenated &&
                mkdir feedback &&
                cd ..
        done
        echo "-- DONE INITIALIZING ALL GIT DIRECTORIES --"
    fi
}

# Pulls all child .git directories at once. Restartable script if host limits pull-rate.
# -> ARGS: NONE
function pull-all() {
    TMP_FILE="tmp-pulled-repos.txt"
    COMPLETED=1

    touch $TMP_FILE
    for dir in $(find . -maxdepth 1 -type d -not -path '.'); do
        if ! grep -q $dir $TMP_FILE; then
            cd $dir
            if [ -d ".git" ]; then
                echo "Pulling changes from $dir..."
                git pull
                if [ $? = 0 ]; then
                    echo $dir >>../$TMP_FILE
                else
                    COMPLETED=0
                fi
            fi
            cd ..
        fi
    done
    if [ $COMPLETED = 1 ]; then
        rm $TMP_FILE
        echo "-- DONE PULLING ALL GIT DIRECTORIES --"
    fi
}

# Adds and commits changes at a given path within the child .git directories.
# -> ARGS: $1 = folder to be added, $2 = commit message
function commit-all() {
    for dir in $(find . -maxdepth 1 -type d -not -path '.'); do
        cd $dir
        if [ -d ".git" ]; then
            git add "$1" && git commit -m "$2"
        fi
        cd ..
    done
    echo "-- DONE COMMITTING CHANGES OF '$1' IN ALL GIT DIRECTORIES --"
}

# Pushes all child .git directories at once. Restartable script if host limits push-rate.
# -> ARGS: NONE
function push-all() {
    TMP_FILE="tmp-pushed-repos.txt"
    COMPLETED=1

    touch $TMP_FILE
    for dir in $(find . -maxdepth 1 -type d -not -path '.'); do
        if ! grep -q $dir $TMP_FILE; then
            cd $dir
            if [ -d ".git" ]; then
                git push -u origin
                if [ $? = 0 ]; then
                    echo $dir >>../$TMP_FILE
                else
                    COMPLETED=0
                fi
            fi
            cd ..
        fi
    done
    if [ $COMPLETED = 1 ]; then
        rm $TMP_FILE
        echo "-- DONE PUSHING ALL GIT DIRECTORIES --"
    fi
}
