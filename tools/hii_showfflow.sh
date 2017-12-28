#!/bin/bash
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
# wrap inotifywait to show file events
# in .hydra directory

cleanflag=''
helpflag=''
verbose='false'

while getopts 'chv' flag; do
  case "${flag}" in
    c) cleanflag='true' 
        echo "cleaning posts: .hydra/posts/"
        echo "cleaning peers: .hydra/peers/"
        rm -r .hydra/posts/*
        rm -r .hydra/peers/*
    ;;
    h) helpflag='true' 
        echo "wrap inotifywait to show file events"
        echo ".hydra directory"
        echo "Usage: showfflow [ options ]"
        echo "Options:"
        echo "-h      help"
        echo "-c      clean peer and posts directories"
        exit 0;
    ;;
    v) verbose='true' 
    ;;
  esac
done

inotifywait -e create,open,modify,close,delete \
            -r .hydra \
            -m \
            --format '%e %w%f' \
| while read -r EVENT FILE;
do
    printf "%-30s\t%s\n" "$EVENT" "$(stat --printf '%s\t%n' $FILE)"
done 
