# catalog
This catalog web app allows users to create, read, update and delete items. To be more specific, users can log in with their Google account, add movies in a specific category to the database, edit the information of the movies and can also delete the movie they added. Users can only modify the movies which are created by themselves.

This project makes use of the Linux-based virtual machine (VM), you'll need VirtualBox, Vagrant installed in advance.

# Start Guide:

Put all files into a folder "catalog" inside vagrant subdirectory
From your terminal, inside the vagrant subdirectory, run the command vagrant up
When vagrant up is finished running, run vagrant ssh to log in to your Linux VM
Inside the VM, change directory to \vagrant (cd \vagrant), and then cd catalog
Download and run command python catalog_init.py to populate database with movies
Run command python application.py
Open a browser and enter localhost:5000
