## This file is for Purely EXEC mode, no GUI

#### The executables are stored at "PhotoCryX/EXEC", which are

* mpb_1d
* mpb_hx
* mpb_sq
* mpb_vy

#### The mandatory files are "mpb.in" and the GDSII file  
#### Here we discuss a honeycomb lattice with the GDSII file "dumbell.gds" in the "TEST/hex" folder
```
cd ~/Downloads/PhotoCryX/PhotoCryX/TEST/hex
```

#### Initially, we export the executables to the path
```
export PATH=~/Downloads/PhotoCryX/PhotoCryX/EXEC:$PATH
```
#### Here, as the hexagonal and honeycomb possess the same reciprocal vectors, the executable is "mpb_hx"
#### Edit the master control file "mpb.in" if needed and then execute
```
mpb_hx
```
#### This executes and plots all necessary images in the "~/Downloads/PhotoCryX/PhotoCryX/TEST/hex" directory
#### If needed, the TEST/hex folder may be copied to some other location
