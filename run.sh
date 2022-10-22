# install packages
pip install -r source/requirements.txt

# run all files in input folder, store results in output folder, show video on screen
python source/main.py

# run silently, or if you dont have video device
# python source/main.py --dont-show-video

# run specific file
# python source/main.py --path input\\level_1\\input1.txt

# run some specific levels
# python source/main.py --level 2 4

# for more information
# python source/main.py -h
