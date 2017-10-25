pySemcor - A library for processing Semcor with Python 
========

# Installation steps

1. Create "workspace" folder in home folder (i.e. ~/workspace or /home/{username}/workspace)
2. Clone pysemcor to this folder
3. Run `config.sh`
4. Run `./main.py fix` to fix 3rada dataset
5. Run `./main.py json` to generate JSON dataset
6. Run `./main.py ttl` to convert semcor XML to TTL (texttaglib) format

Shell command for the above tasks

```
mkdir ~/workspace
cd ~/workspace
git clone https://github.com/letuananh/pysemcor
cd pysemcor
bash config.sh
python3 main.py fix
python3 main.py json
python3 main.py ttl
```
