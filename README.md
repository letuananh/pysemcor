pysemcor
========

A library for processing Semcor with Python 

# Installation steps

1. Create "workspace" folder in home folder (i.e. /home/{username}/workspace
2. Clone pysemcor, beautifulsoup, ntlk  to this folder
3. Run config.sh
4. Run fixsemcor.py

Shell command for the above tasks

```
mkdir ~/workspace
cd ~/workspace
git clone https://github.com/letuananh/beautifulsoup
git clone https://github.com/letuananh/pysemcor
git clone https://github.com/nltk/nltk
cd pysemcor
bash config.sh
python3 fixsemcor.py all
```
