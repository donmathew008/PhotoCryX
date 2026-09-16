## Installation of PhotoCryX using Anaconda
#### Anaconda or Miniconda is to be installed on the system, as we have done everything as a conda environment
[Download_Anaconda](https://www.anaconda.com/download)
#### After installation of conda and activating it, in a terminal execute
    conda create -n mp -c conda-forge pymeep
#### This will create a new environment "mp" which installs serial MEEP. [Reference](https://meep.readthedocs.io/en/master/Installation/#conda-packages)
#### The installed conda environment can be activated by,
    conda activate mp
#### Currently, MPB works only in serial mode (in Python); we do not require a parallel MEEP installation. We need some additional packages for the GUI, which are Tkinter and KLayout, for which the installation is straightforward. Tkinter is for the GUI, and KLayout is a GDSII file viewer and editor.
#### Tkinter can be installed using conda-forge or pip
    conda install -c conda-forge tk
    pip install tkinter
#### To install KLayout, download the "klayout*.deb" file and install 
[Download_KLayout](https://www.klayout.de/build.html)
#### Or it can be built from source
#### These are the prerequisites for PhotoCryX
#### To install PhotoCryX, download the latest version anywhere on your system, unzip it, and you are ready to compute. A desktop icon can be created using the launcher script provided in PhotoCryX. After the installation of the required packages and unzipping PhotoCryX (say in the "Downloads" folder), we will change the directory as,
    cd ~/Downloads
    wget -O PhotoCryX.zip https://github.com/donmathew008/PhotoCryX/raw/main/PhotoCryX.zip
    unzip PhotoCryX.zip
    cd PhotoCryX
#### Then we will create a desktop launcher by executing the "makeLauncher_PhotoCryX.sh" after making it executable by,
    chmod +x makeLauncher_PhotoCryX.sh
    ./makeLauncher_PhotoCryX.sh
#### This will create "PhotoCryX.desktop", which can be copied to the desktop
    cp PhotoCryX.desktop ~/Desktop
#### Thus PhotoCryX can be launched directly from the desktop
#### After creating the launcher, right-click on the desktop icon and give "Allow Launching"
#### Now the installation is completed
#### For users who prefer direct execution mode via a terminal, the executables should be added to the current path. They are stored in the folder "EXEC" inside PhotoCryX, so to add to the path,
    export PATH=~/Downloads/PhotoCryX/EXEC:$PATH
#### Thus, we can directly use the executable in whichever parent folder contains the required inputs: "mpb.in" and the GDSII file.
