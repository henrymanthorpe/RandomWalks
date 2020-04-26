# RandomWalks

This is the simulation package for my MPhys Project on Bacterial and Archaeal motility.\n

Prototype2.0 is the final version at the time of submission of the final report.\n
The master branch may contain further changes as and when I get around to them.\n

Python library requirements are listed in REQUIREMENTS.txt\n
The implementation can be buggy at points, mostly in the file IO routines.\n

To run a simulation:\n
First, download the package and unzip to any directory/folder you wish.\n
Then, run "python Build.py -d" to create the default configuration file in the current working directory.\n
This file can be edited in all good text-editors.\n
Then a new directory for the simulation output to be saved in should be created - for the sake of this it will be called "Batch" \n
(Somewhere with plenty of freespace is preferable, depending on your simulation variables, the trajectory files can get pretty big) \n
In this folder, create a subfolder called "configs", and in this place any and all configuration files you want to run.\n
(One is recommended for the first run)\n
Finally, return to the script folder, and run "python Build.py -o PATH/TO/Batch\n
This can either be the absolute path, or the relative path from the CWD.\n

That covers the basic operation of the simulation code.\n
Running "python Build.py -h" will show the complete set of options.\n

For any further help, requests or maintenance needs, contact Henry Manthorpe,\n
either by email: henrymanthorpe@gmail.com\n
or through the Github Issues page.\n


