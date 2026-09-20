import os
import re
import math
import numpy as np
import matplotlib.pyplot as plt
import meep as mp
from meep import mpb

# ============================================================
#                      PARSER FOR mpb.in
# ============================================================

def read_mpb_in(filename="mpb.in"):
    params = {}
    if not os.path.exists(filename):
        print("ERROR: mpb.in not found!")
        exit()

    with open(filename, "r") as f:
        for line in f:
            line = line.strip()

            if not line or line.startswith("#"):
                continue

            if "=" not in line:
                continue

            key, val = map(str.strip, line.split("=", 1))

            if re.match(r"^\.(TRUE|FALSE)\.$", val, re.IGNORECASE):
                params[key] = val.strip(".").upper() == "TRUE"

            elif re.match(r"^[+-]?\d+$", val):
                params[key] = int(val)

            elif re.match(r"^[+-]?\d*\.\d+$", val):
                params[key] = float(val)

            else:
                params[key] = val

    return params


# Load mpb.in
P = read_mpb_in()
print("Loaded parameters:", P)

# ============================================================
#                 APPLY PARAMETERS
# ============================================================

num_bands = P.get("NUM_BANDS", 6)
resolution = P.get("RESOLUTION", 64)
interpolation_points = P.get("INTERPOLATION_POINTS", 20)
eps_periods = P.get("PERIODS", 1)
ht = 0.1

PLOT_EPSILON  = P.get("PLOT_EPSILON", True)
PLOT_BANDS    = P.get("PLOT_BANDS", True)
PLOT_BANDS_NORM = P.get("PLOT_BANDS_NORM", True)
PLOT_TM_FIELDS = P.get("PLOT_TM_FIELDS", True)
PLOT_TE_FIELDS = P.get("PLOT_TE_FIELDS", True)
PLOT_TM_FIELDS_NORM = P.get("PLOT_TM_FIELDS_NORM", True)
PLOT_TE_FIELDS_NORM = P.get("PLOT_TE_FIELDS_NORM", True)
PLOT_TM_PHASE  = P.get("PLOT_TM_PHASE", True)
PLOT_TE_PHASE  = P.get("PLOT_TE_PHASE", True)
FIELD_KPOINT = int(P.get("FIELD_KPOINT", 0))

# ============================================================
#                 INPUT PARAMETERS
# ============================================================

gdsII_file = P.get("GDS_FILE", "1d.gds")
scale_factor = 1.0

LAYER1 = 1
LAYER2 = 2

si_zmin = 0
si_zmax = 0.22
thickness = si_zmax - si_zmin

index_val1 = P.get("INDEX1", 11.7)
nslab1 = np.sqrt(index_val1)
slab1 = mp.Medium(index=nslab1)

index_val2 = P.get("INDEX2", 2.1025)
nslab2 = np.sqrt(index_val2)
slab2 = mp.Medium(index=nslab2)

# ============================================================
#                 LATTICE SETUP
# ============================================================

#a = 1
#geometry_lattice = mp.Lattice(size=mp.Vector3(a, ht))

# ============================================================
#      EXTRACT POLYGONS FOR TWO LAYERS FROM GDS
# ============================================================

poly_L1 = mp.get_GDSII_prisms(slab1, gdsII_file, LAYER1, si_zmin, si_zmax)
poly_L2 = mp.get_GDSII_prisms(slab2, gdsII_file, LAYER2, si_zmin, si_zmax)

# ============================================================
#           AUTO-DETECT PERIOD FROM GDS EXTENT (X–range)
# ============================================================

all_x = []

# collect x coordinates from layer 1
for poly in poly_L1:
    for v in poly.vertices:
        all_x.append(v.x * scale_factor/1000)

# collect x coordinates from layer 2
for poly in poly_L2:
    for v in poly.vertices:
        all_x.append(v.x * scale_factor/1000)

if len(all_x) == 0:
    print("ERROR: GDS contains no polygons. Cannot determine period.")
    exit()

xmin = min(all_x)
xmax = max(all_x)

PERIOD = xmax - xmin

print(f"Detected PERIOD from GDS: {PERIOD}")

# build lattice using true period
geometry_lattice = mp.Lattice(size=mp.Vector3(PERIOD, ht))

# ============================================================
#   CONVERT POLYGON → BLOCK WITH FORCED Y-HEIGHT = 0.1
# ============================================================

FORCED_Y_HEIGHT = 0.1  # <-- always use this Y thickness

def polygon_to_block(poly, material):
    """Convert a polygon prism into an mp.Block with fixed Y height."""
    verts = [mp.Vector3(v.x * scale_factor/1000, v.y * scale_factor, 0)
             for v in poly.vertices]

    xs = [v.x for v in verts]
    ys = [v.y for v in verts]

    xmin, xmax = min(xs), max(xs)
    ymin, ymax = min(ys), max(ys)

    cx = 0.5 * (xmin + xmax)
    cy = 0.5 * (ymin + ymax)

    sx = xmax - xmin       # keep X width from GDS
    sy = FORCED_Y_HEIGHT   # <-- force Y to 0.1 ALWAYS

    return mp.Block(
        size=mp.Vector3(sx, sy, thickness),
        center=mp.Vector3(cx, cy),
        material=material
    )

# ============================================================
#         BUILD GEOMETRY LIST FROM BOTH LAYERS
# ============================================================

geometry = []

for poly in poly_L1:
    geometry.append(polygon_to_block(poly, slab1))

for poly in poly_L2:
    geometry.append(polygon_to_block(poly, slab2))

# ============================================================
#                 K-PATH SETUP
# ============================================================

BZ_POINTS = {
    5: (mp.Vector3(-0.5, 0), "-X"),
    0: (mp.Vector3(0, 0), "Γ"),
    4: (mp.Vector3(0.5, 0), "X")
}

KPATH = P.get("KPATH", "5 0 4")
kpath_list = list(map(int, KPATH.split()))

def get_k_points(kpath, interpolation_points):
    pts = [BZ_POINTS[p][0] for p in kpath]
    return mp.interpolate(interpolation_points, pts)

k_points = get_k_points(kpath_list, interpolation_points)

k_labels = [BZ_POINTS[p][1] for p in kpath_list]

# ============================================================
#                 RUN MPB
# ============================================================

ms = mpb.ModeSolver(
    geometry=geometry,
    geometry_lattice=geometry_lattice,
    k_points=k_points,
    resolution=resolution,
    num_bands=num_bands
)

print("Running TM...")
ms.run_tm(mpb.output_at_kpoint(mp.Vector3(-1/3, 1/3),
                               mpb.fix_efield_phase,
                               mpb.output_efield_z))
ms.output_epsilon()
tm_freqs = ms.all_freqs
tm_gaps = ms.gap_list

#print("Running TE...")
#ms.run_te()
#te_freqs = ms.all_freqs
#te_gaps = ms.gap_list

# ============================================================
#                 DIELECTRIC PLOT
# ============================================================

if PLOT_EPSILON:
    eps = mpb.MPBData(rectify=True, periods=eps_periods, resolution=512).convert(ms.get_epsilon())
    plt.imshow(eps.T, interpolation='spline36', cmap='binary')
    plt.axis('off')
    plt.savefig("epsilon.jpg")
    plt.close()

# ============================================================
#                 BAND STRUCTURE
# ============================================================

def plot_bands(freqs, gaps, color, label, filename):
    fig, ax = plt.subplots()
    ax.plot(freqs * 300, color=color)
    x = range(len(freqs))
    for gap in gaps:
        if gap[0] > 1:
            ax.fill_between(x, gap[1] * 300, gap[2] * 300, color=color, alpha=0.2)
    ticks = np.linspace(0, len(freqs)-1, len(k_labels))
    ax.set_xticks(ticks)
    ax.set_xticklabels(k_labels, size=14)
    ax.set_xlim([x[0], x[-1]])
    ax.set_ylim([0, np.max(freqs * 300)])
    ax.set_ylabel("Frequency (THz)")
    plt.savefig(filename, dpi=300)
    plt.close()
    
# ============================================================
#                 BAND STRUCTURE both TE and TM
# ============================================================
def plot_both(tm_freqs, filename):
    fig, ax = plt.subplots()

    x = range(len(tm_freqs))

    ax.plot(tm_freqs * 300, color="blue")
#    ax.plot(te_freqs * 300, color="red")

    ticks = np.linspace(0, len(tm_freqs)-1, len(k_labels))
    ax.set_xticks(ticks)
    ax.set_xticklabels(k_labels, size=14)

    ax.set_xlim([x[0], x[-1]])
    ax.set_ylim([0, max(np.max(tm_freqs * 300))])

    ax.set_ylabel("Frequency (THz)")
    ax.legend()

    plt.savefig(filename, dpi=300)
    plt.close()

if PLOT_BANDS:
    plot_bands(tm_freqs, tm_gaps, "blue", "TM", "band_structure.jpg")
#    plot_bands(te_freqs, te_gaps, "red", "TE", "band_TE.jpg")
#    plot_bands(tm_freqs, tm_gaps, "band_structure.jpg")



# ============================================================
#                 NORMALISED BAND STRUCTURE
# ============================================================

def plot_bands_norm(freqs, gaps, color, label, filename):
    fig, ax = plt.subplots()
    ax.plot(freqs, color=color)
    x = range(len(freqs))
    for gap in gaps:
        if gap[0] > 1:
            ax.fill_between(x, gap[1], gap[2], color=color, alpha=0.2)
    ticks = np.linspace(0, len(freqs)-1, len(k_labels))
    ax.set_xticks(ticks)
    ax.set_xticklabels(k_labels, size=14)
    ax.set_ylabel("Frequency (c/a)")
    ax.set_xlim([x[0], x[-1]])
    ax.set_ylim([0, np.max(freqs)])
    plt.savefig(filename, dpi=300)
    plt.close()

if PLOT_BANDS_NORM:
    plot_bands_norm(tm_freqs, tm_gaps, "blue", "TM", "band_structure_norm.jpg")
#    plot_bands_norm(te_freqs, te_gaps, "red", "TE", "band_TE_norm.jpg")

# ============================================================
#                 FIELD EXTRACTION
# ============================================================

field_k = BZ_POINTS[FIELD_KPOINT][0]
efields, hfields = [], []

def get_efields(ms, band):
    efields.append(ms.get_efield(band, bloch_phase=True))

def get_hfields(ms, band):
    hfields.append(ms.get_hfield(band, bloch_phase=True))

if PLOT_TM_FIELDS or PLOT_TM_PHASE:
    ms.run_tm(mpb.output_at_kpoint(field_k, mpb.fix_efield_phase, get_efields))

if PLOT_TE_FIELDS or PLOT_TE_PHASE:
    ms.run_te(mpb.output_at_kpoint(field_k, mpb.output_hfield_z, get_hfields))

md = mpb.MPBData(rectify=True, resolution=256, periods=1)
eps_conv = md.convert(ms.get_epsilon())

N = num_bands
num_plot = math.ceil(math.sqrt(N))

# ============================================================
#                 TM FIELDS
# ============================================================

if PLOT_TM_FIELDS:
    conv_e = [md.convert(f[..., 0, 2]) for f in efields[:num_bands]]
    for i, f in enumerate(conv_e):
        plt.subplot(num_plot, num_plot, i+1)
        plt.contour(eps_conv.T, cmap='binary')
        plt.imshow(np.real(f).T, cmap='jet', alpha=0.9)
        plt.axis('off')
    plt.savefig("TM_fields.jpg", dpi=300, bbox_inches='tight')
    plt.close()

# ============================================================
#                 TE FIELDS
# ============================================================

if PLOT_TE_FIELDS:
    conv_h = [md.convert(f[..., 0, 2]) for f in hfields[:num_bands]]
    for i, f in enumerate(conv_h):
        plt.subplot(num_plot, num_plot, i+1)
        plt.contour(eps_conv.T, cmap='binary')
        plt.imshow(np.real(f).T, cmap='jet', alpha=0.9)
        plt.axis('off')
    plt.savefig("TE_fields.jpg", dpi=300, bbox_inches='tight')
    plt.close()

# ============================================================
#                 TM FIELDS NORM
# ============================================================

if PLOT_TM_FIELDS_NORM:
    conv_e = [md.convert(f[..., 0, 2]) for f in efields[:num_bands]]
    for i, f in enumerate(conv_e):
        plt.subplot(num_plot, num_plot, i+1)
        plt.contour(eps_conv.T, cmap='binary')
        plt.imshow(np.abs(f.T), cmap='jet', alpha=0.9)
        plt.axis('off')
    plt.savefig("TM_fields_NORM.jpg", dpi=300, bbox_inches='tight')
    plt.close()

# ============================================================
#                 TE FIELDS NORM
# ============================================================

if PLOT_TE_FIELDS_NORM:
    conv_h = [md.convert(f[..., 0, 2]) for f in hfields[:num_bands]]
    for i, f in enumerate(conv_h):
        plt.subplot(num_plot, num_plot, i+1)
        plt.contour(eps_conv.T, cmap='binary')
        plt.imshow(np.abs(f.T), cmap='jet', alpha=0.9)
        plt.axis('off')
    plt.savefig("TE_fields_NORM.jpg", dpi=300, bbox_inches='tight')
    plt.close()
    
# ============================================================
#                 TM PHASE
# ============================================================

if PLOT_TM_PHASE:
    conv_e = [md.convert(f[..., 0, 2]) for f in efields[:num_bands]]
    for i, f in enumerate(conv_e):
        plt.subplot(num_plot, num_plot, i+1)
        plt.contour(eps_conv.T, cmap='binary')
        plt.imshow(np.angle(f).T, cmap='jet', alpha=0.9)
        plt.axis('off')
    plt.savefig("TM_phase.jpg", dpi=300, bbox_inches='tight')
    plt.close()

# ============================================================
#                 TE PHASE
# ============================================================

if PLOT_TE_PHASE:
    conv_h = [md.convert(f[..., 0, 2]) for f in hfields[:num_bands]]
    for i, f in enumerate(conv_h):
        plt.subplot(num_plot, num_plot, i+1)
        plt.contour(eps_conv.T, cmap='binary')
        plt.imshow(np.angle(f).T, cmap='jet', alpha=0.9)
        plt.axis('off')
    plt.savefig("TE_phase.jpg", dpi=300, bbox_inches='tight')
    plt.close()

print("Completed successfully.")
exit()
