### This file is only needed for 3D lattices to visualize epsilon in 3D

[Reference](https://mpb.readthedocs.io/en/latest/Data_Analysis_Tutorial/)
### This can only be used if and only if all the steps in the "Installation.md" are followed as such, and all packages are installed without errors

### After computation of band structure of the 3D lattice, say the file is at
```
~/Desktop/FCC
```
                          
### We have "band-epsilon.h5" in "Desktop/FCC"; it also has "band-dpwr.k*.b*.h5", say "band-dpwr.k06.b*.h5"
### Refer to mpb-docs for more details on the commands

### Now open a terminal at the location and run (change the numbers "06")
```
cd ~/Desktop/FCC
```
```
mpb-data -m 2 -r -n 32 band-epsilon.h5 band-dpwr.k06.b*.h5
```
```                                                                                   
h5tov5d -o fcc.v5d -d data-new band-epsilon.h5 band-dpwr.k06.b*.h5
```
	
### Sometimes the HDF5 library is not found; then export the lib location (Replace "HDF5_PATH" with the HDF5 directory)

```
export LD_LIBRARY_PATH=HDF5_PATH/lib/:$LD_LIBRARY_PATH
``` 
	
### If an HDF5 error pops up, export the following and run the above 

```
export HDF5_USE_FILE_LOCKING=FALSE
```
### This command may be used constantly in dealing with HDF5 files

### To view using vis5d (Recommended)
                                                                                   
```
vis5d fcc.v5d &
```
	
### To view in Mayavi, execute 

```
python plot3d.py
```
	

