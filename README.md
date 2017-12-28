# hii

_press keys, observe glimmering bytes, repeat_

* [Overview](#overview)
* [Installing](#install)
* [Debug Notes](#debug-notes)
* [Contributing](#contribute)
* [License](#license)

## Overview

`hii` is a commandline tool to test usage of the Hydra Protocol by easily (a single keypress) generating posts/contents in an interactive loop.

Begun while trying to make a minimal python version of `hydrad`. Then used to see why chunks of byte-blobs were not being written to disk in some cases(still an issue).

Uses zproject-generated python bindings for Hydra and Czmq(for Zchunk).

Post mimetypes and contents:

| content| mimetype   |    encoding format        | hii generates | 
|--------|------------|------------------|--------|
|image   | image/jpeg |    zchunk        | image of words | 
|string  | text/plain |    string        | words  | 
|file    | text/zpl   |              | _TODO_  | 


The post subject and `text/plain` contents use words randomly picked from /usr/share/dict/words 

## Install

1. **Build Hydra** 

    Build & install libraries as listed in Hydra README.

    Currently, this may be the most recent fork of Hydra:  
    ```
    https://github.com/galencm/hydra
    ```

2. **Install python modules**

    ```
    pip3 install --user Pillow
    pip3 install --user curtsies
    pip3 install --user pytest
    ```  
    `hii` uses Pillow for generating images, curtsies for handling keyboard input and pytest for tests.  

3. **Clone repository and run**

    ```
    git clone https://github.com/galencm/hii
    cd hii/
    pytest -v
    ./hii 
    ```
    To see image generated from unicode overlay test:
    ```
    pytest -v --eye
    ```
    The default viewer used by Pillow is `display`, part of imagemagick. If test fails install imagemagick: `sudo apt-get install imagemagick` or `sudo dnf install imagemagick`

4. **(if missing) Install Unifont**

    To support as many languages as possible `hii` tries to use unifont for the text overlays on generated images. 

    If unifont is not found a fallback font is used.

    Run to see if installed:
    ```
    fc-list | grep unifont
    ```

    * debian package
        ```
        sudo apt-get install ttf-unifont
        ```

    * fedora package
        ```
        sudo dnf install unifont-fonts
        ```

    * download and install from file(s)
        ```
        wget http://unifoundry.com/pub/unifont-10.0.06/font-builds/unifont-10.0.06.ttf
        wget http://unifoundry.com/pub/unifont-10.0.06/font-builds/unifont_upper-10.0.06.ttf
        sudo mkdir /usr/share/fonts/unifont/
        sudo mv unifont-10.0.06.ttf  /usr/share/fonts/unifont/
        sudo mv unifont_upper-10.0.06.ttf  /usr/share/fonts/unifont/
        ```

5. **(if missing) Install words**
    `hii` uses /usr/share/dict/words as a source for text.

    If the file is not found, `hii` will always use the text: "words not found"

    A raspberry pi running rasbpian does not seem have a words file installed by default.

    * debian package
        ```
        sudo aptitude install wordlist
        ```
        will show a metapackage with choices of words to install

    * fedora package
        ```
        sudo dnf install unifont-fonts
        ```

    * diy
        create a text file with one word per line. The following command overwrites any existing words
        ```
        sudo mv yourwords.txt /usr/share/dict/words
        ```

## Debug notes

* Hydra Service filesystem structure

    By default Hydra stores files in a `.hydra` directory created(if not found) wherever service is running. The subdirectories will be created(if not found) as needed.

    ```
    .hydra
    .hydra/peers
    .hydra/posts
    .hydra/blobs
    ```

* Watch directories for filesystem changes using `inotifywait` 
    
    ```
    inotifywait -e modify,create,delete -r .hydra/ -m
    ```  

* Diff binaries using `vbindiff`

    ```
    vbindiff .hydra/posts/blobs/file_foo ../file_bar
    ```

## Contribute

This project uses the C4 process

https://rfc.zeromq.org/spec:42/C4/

## License

Mozilla Public License, v. 2.0

http://mozilla.org/MPL/2.0/



