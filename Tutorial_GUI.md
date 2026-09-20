## PhotoCryX tutorial using GUI
#### The initial interface of PhotoCryX is;

<p align="center">
  <img src="images/GUI.png" width="600">
</p>

## One-dimensional Photonic Crystal (1DPC)
#### The 1D interface has just the "Run Simulation" button as shown below

<p align="center">
  <img src="images/1D.png" width="600">
</p>

#### This will open a folder-creation pop-up as shown below. If we do not create a folder, the run happens in the parent directory or the source directory
#### So it is better to create a folder, and the source directory remains untouched

<p align="center">
  <img src="images/folder_creation.png" width="600">
</p>

#### Then the parameter pop-up opens up as shown below; either default values can be used or any arbitrary values. It may be noted that currently 'nm' structures are only optimized

<p align="center">
  <img src="images/1D_parameters.png" width="600">
</p>

#### The computed epsilon and band structure are displayed as shown; it also computes the field, which can be opened directly by clicking the "Open Image" tab

<p align="center">
  <img src="images/1D_computed.png" width="600">
</p>

## Two-dimensional Photonic Crystal (2DPC) - Honeycomb lattice

<p align="center">
  <img src="images/2D.png" width="600">
</p>

<p align="center">
  <img src="images/folder_creation.png" width="600">
</p>


<p align="center">
  <img src="images/honeycomb_parameters.png" width="600">
</p>

<p align="center">
  <img src="images/honeycomb_computed.png" width="600">
</p>

## Three-dimensional Photonic Crystal (3DPC) - FCC lattice

<p align="center">
  <img src="images/3D.png" width="600">
</p>

<p align="center">
  <img src="images/folder_creation.png" width="600">
</p>

<p align="center">
  <img src="images/FCC_parameters.png" width="600">
</p>

<p align="center">
  <img src="images/FCC_computed.png" width="600">
</p>

#### The epsilon is just a 2D surface plot, to visualize in 3D we need additional packages like Mayavi or Vis5D, the installation is discussed [here](https://github.com/donmathew008/PhotoCryX/blob/main/Installation.md)
#### All 3D folders are occupied with "plot3d.py" which uses Mayavi, The detailed 3D visualization is given [here](https://github.com/donmathew008/PhotoCryX/blob/main/3D_Visualization.md)

## Executable mode (EXEC) with GDSII file and "mpb.in" in the destination folder

<p align="center">
  <img src="images/EXEC.png" width="600">
</p>

#### The control file or the main input file is "mpb.in", here, a sample is given
<p align="center">
  <img src="images/control_file.png" width="600">
</p>






	





	


			





		

