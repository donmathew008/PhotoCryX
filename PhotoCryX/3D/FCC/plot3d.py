from mayavi import mlab
from tvtk.util.ctf import ColorTransferFunction, PiecewiseFunction
import h5py
import numpy as np

with h5py.File("band-epsilon.h5", "r") as f:
    eps = f["data-new"][:]

mlab.figure(bgcolor=(1, 1, 1))
src = mlab.pipeline.scalar_field(eps)
vol = mlab.pipeline.volume(src)

vmin, vmax = eps.min(), eps.max()
vmid = 0.5 * (vmin + vmax)

# --- COLOR TRANSFER FUNCTION ---
ctf = ColorTransferFunction()
ctf.add_rgb_point(vmin, 0.0, 0.0, 0.0)
ctf.add_rgb_point(vmid, 0.0, 0.6, 1.0)
ctf.add_rgb_point(vmax, 0.0, 0.0, 0.6)



# --- OPACITY TRANSFER FUNCTION ---
otf = PiecewiseFunction()
otf.add_point(vmin, 0.0)
otf.add_point(vmax, 0.6)

vol._volume_property.set_color(ctf)
vol._volume_property.set_scalar_opacity(otf)

mlab.show()
