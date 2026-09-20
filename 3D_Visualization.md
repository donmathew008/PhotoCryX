## This file is only needed for 3D lattices to visualize epsilon in 3D

## This can only be used if and only if all the steps in the "Installation.md" are followed as such, and all packages are installed without errors

## After computation of band structure of the 3D lattice, say the file is at
```
~/Desktop/FCC
```
                          
# We have "band-epsilon.h5" in our folder

# Now open a terminal at the location and run (change the numbers "06")

	mpb-data -m 2 -r -n 32 band-epsilon.h5 band-dpwr.k06.b*.h5
                                                                                   
	h5tov5d -o diamond.v5d -d data-new band-epsilon.h5 band-dpwr.k06.b*.h5
	
# Sometimes the library is not found then 

	export LD_LIBRARY_PATH=/usr/local/hdf5/lib/:$LD_LIBRARY_PATH  
	
# If HDF5 error pops up export the following and run the above 

	export HDF5_USE_FILE_LOCKING=FALSE	
	
# To view using vis5d (Recommended)
                                                                                   
	vis5d diamond.v5d &
	
# To view in Mayavi, execute 

	python plot3d.py
	

