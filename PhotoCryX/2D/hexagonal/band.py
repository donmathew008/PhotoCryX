import tkinter as tk
from tkinter import ttk

def run_code():
    N1 = entry1.get()
    a1 = entry2.get()
    ratio1 = entry3.get()
    epsilon1 = entry4.get()
    interpolation1 = entry5.get()
    Resolution1 = entry6.get()
   
    import math
    import numpy as np
    import matplotlib.pyplot as plt
    import meep as mp
    from meep import mpb


    num_bands = int(N1)
    resolution = int(Resolution1)
    interpolation = int(interpolation1)
    a = float(a1)/1000
    r =float(ratio1)*a
    eps = float(epsilon1)

    geometry_lattice = mp.Lattice(size=mp.Vector3(a, a),
                                  basis1=mp.Vector3(0.5, math.sqrt(3)/2),
                                  basis2=mp.Vector3(1, 0))

    geometry = [mp.Cylinder(r, material=mp.Medium(epsilon=eps), center=mp.Vector3(0, 0))]

    k_points = [
        mp.Vector3(),               # Gamma
        mp.Vector3(0.5, 0.5),          # M
        mp.Vector3(1./3, 2./3),    # K
        mp.Vector3(),               # Gamma
    ]


    k_points = mp.interpolate(interpolation, k_points)

    ms = mpb.ModeSolver(
        geometry=geometry,
        geometry_lattice=geometry_lattice,
        k_points=k_points,
        resolution=resolution,
        num_bands=num_bands
    )
    ms.run_tm(mpb.output_at_kpoint(mp.Vector3(-1./3, 1./3), mpb.fix_efield_phase,
              mpb.output_efield_z))
    ms.output_epsilon()
    tm_freqs = ms.all_freqs
    tm_gaps = ms.gap_list
    ms.run_te()
    te_freqs = ms.all_freqs
    te_gaps = ms.gap_list


    md = mpb.MPBData(rectify=True, periods=3, resolution=512)
    eps = ms.get_epsilon()
    converted_eps = md.convert(eps)
    plt.imshow(converted_eps.T, interpolation='spline36', cmap='binary')
    plt.axis('off')
    plt.savefig('epsilon.jpg')
    plt.close()
    
# ============================================================
#                 Band Structure Plots
# ============================================================
#              1. TE and TM with scatter plot normalized
# ============================================================

    fig, ax = plt.subplots()
    x = range(len(tm_freqs))
#    for xz, tmz, tez in zip(x, tm_freqs, te_freqs):
#        ax.scatter([xz]*len(tmz), tmz, color='blue')
#        ax.scatter([xz]*len(tez), tez, color='red', facecolors='none')
    ax.plot(tm_freqs, color='blue')
    ax.plot(te_freqs, color='red')
    ax.set_xlim([x[0], x[-1]])
    for gap in tm_gaps:
        if gap[0] > 1:
            ax.fill_between(x, gap[1], gap[2], color='blue', alpha=0.2)

    for gap in te_gaps:
        if gap[0] > 1:
            ax.fill_between(x, gap[1], gap[2], color='red', alpha=0.2)
    ax.text(11, 0.04, 'TM', color='blue', size=15)
    ax.text(11, 0.14, 'TE', color='red', size=15)

    points_in_between = (len(tm_freqs) - 4) / 3
    tick_locs = [i*points_in_between+i for i in range(4)]
    tick_labs = ['Γ', 'M', 'K', 'Γ']
    ax.set_xticks(tick_locs)
    ax.set_xticklabels(tick_labs, size=16)
    ax.set_ylabel('Frequency (c/a)', size=16)
    ax.set_ylim([0, np.max(te_freqs)])
    ax.grid(True)
    plt.savefig('band_structure.jpg')
    plt.close()


# ============================================================
#              2. TE and TM normalized
# ============================================================

    fig, ax = plt.subplots()
    x = range(len(tm_freqs))
    ax.plot(tm_freqs , color='blue')
    ax.plot(te_freqs , color='red')
    ax.set_xlim([x[0], x[-1]])
    for gap in tm_gaps:
        if gap[0] > 1:
            ax.fill_between(x, gap[1], gap[2], color='blue', alpha=0.2)

    for gap in te_gaps:
        if gap[0] > 1:
            ax.fill_between(x, gap[1], gap[2], color='red', alpha=0.2)
    ax.text(48, 0.04, 'TM', color='blue', size=15)
    ax.text(48, 0.14, 'TE', color='red', size=15)

    points_in_between = (len(tm_freqs[:, :6] ) - 4) / 3
    tick_locs = [i*points_in_between+i for i in range(4)]
    tick_labs = ['Γ', 'M', 'K', 'Γ']
    ax.set_xticks(tick_locs)
    ax.set_xticklabels(tick_labs, size=16)
    ax.set_ylabel('Frequency (c/a)', size=16)
    ax.set_ylim([0, np.max(te_freqs)])
    ax.grid(True)
    plt.savefig('band_structure_norm.jpg')
    plt.close()
## tm_freqs[:, :6]    
# ============================================================
#              3. TE and TM 
# ============================================================

    fig, ax = plt.subplots()
    x = range(len(tm_freqs * 300/a))
    ax.plot(tm_freqs * 300/a, color='blue')
    ax.plot(te_freqs * 300/a, color='red')
    ax.set_xlim([x[0], x[-1]])
    for gap in tm_gaps:
        if gap[0] > 1:
            ax.fill_between(x, gap[1] * 300/a, gap[2] * 300/a, color='blue', alpha=0.2)

    for gap in te_gaps:
        if gap[0] > 1:
            ax.fill_between(x, gap[1] * 300/a, gap[2] * 300/a, color='red', alpha=0.2)
    ax.text(11, 0.04, 'TM', color='blue', size=15)
    ax.text(11, 0.14, 'TE', color='red', size=15)

    points_in_between = (len(tm_freqs) - 4) / 3
    tick_locs = [i*points_in_between+i for i in range(4)]
    tick_labs = ['Γ', 'M', 'K', 'Γ']
    ax.set_xticks(tick_locs)
    ax.set_xticklabels(tick_labs, size=16)
    ax.set_ylabel('Frequency (THz)', size=16)
    ax.set_ylim([0, np.max(te_freqs * 300/a)])
    ax.grid(True)
    plt.savefig('band_structure_non.jpg')
    plt.close()    
    
# ============================================================
#              4. TE
# ============================================================

    fig, ax = plt.subplots()
    x = range(len(te_freqs * 300/a))
    ax.plot(te_freqs * 300/a, color='red')
    ax.set_xlim([x[0], x[-1]])
    for gap in te_gaps:
        if gap[0] > 1:
            ax.fill_between(x, gap[1] * 300/a, gap[2] * 300/a, color='red', alpha=0.2)
#    ax.text(13.05, 0.235, 'TE', color='red', size=15)

    points_in_between = (len(te_freqs) - 4) / 3
    tick_locs = [i*points_in_between+i for i in range(4)]
    tick_labs = ['Γ', 'M', 'K', 'Γ']
    ax.set_xticks(tick_locs)
    ax.set_xticklabels(tick_labs, size=16)
    ax.set_ylabel('Frequency (THz)', size=16)
    ax.set_ylim([0, np.max(te_freqs * 300/a)])
    ax.grid(True)
    plt.savefig('band_structure_non_TE.jpg')
    plt.close()    
    
# ============================================================
#              5. TM
# ============================================================

    fig, ax = plt.subplots()
    x = range(len(tm_freqs * 300/a))
    ax.plot(tm_freqs * 300/a, color='blue')
    ax.set_xlim([x[0], x[-1]])
    for gap in tm_gaps:
        if gap[0] > 1:
            ax.fill_between(x, gap[1] * 300/a, gap[2] * 300/a, color='blue', alpha=0.2)

#    ax.text(12, 0.04, 'TM', color='blue', size=15)
    points_in_between = (len(tm_freqs) - 4) / 3
    tick_locs = [i*points_in_between+i for i in range(4)]
    tick_labs = ['Γ', 'M', 'K', 'Γ']
    ax.set_xticks(tick_locs)
    ax.set_xticklabels(tick_labs, size=16)
    ax.set_ylabel('Frequency (THz)', size=16)
    ax.set_ylim([0, np.max(tm_freqs * 300/a)])
    ax.grid(True)
    plt.savefig('band_structure_non_TM.jpg')
    plt.close()    
    
    N = num_bands     # total number of field plots
    num_plot = math.ceil(math.sqrt(N)) 
    eps_conv = md.convert(ms.get_epsilon())

# ============================================================
#              6. TM normalized
# ============================================================
#tm_freqs[:, :6]
    fig, ax = plt.subplots()
    x = range(len(tm_freqs))
    ax.plot(tm_freqs, color='blue')
    ax.set_xlim([x[0], x[-1]])
    for gap in tm_gaps:
        if gap[0] > 1:
            ax.fill_between(x, gap[1], gap[2], color='blue', alpha=0.2)
    points_in_between = (len(tm_freqs) - 4) / 3
    tick_locs = [i*points_in_between+i for i in range(4)]
    tick_labs = ['Γ', 'M', 'K', 'Γ']
    ax.set_xticks(tick_locs)
    ax.set_xticklabels(tick_labs, size=16)
    ax.set_ylabel('Frequency (c/a)', size=16)
    ax.set_ylim([0, np.max(tm_freqs)])
    ax.grid(True)
    plt.savefig('band_structure_norm_TM.jpg')
    plt.close()

# ============================================================
#              7. TE normalized
# ============================================================

    fig, ax = plt.subplots()
    x = range(len(te_freqs))
    ax.plot(te_freqs, color='red')
    ax.set_xlim([x[0], x[-1]])

    for gap in te_gaps:
        if gap[0] > 1:
            ax.fill_between(x, gap[1], gap[2], color='red', alpha=0.2)

    points_in_between = (len(te_freqs) - 4) / 3
    tick_locs = [i*points_in_between+i for i in range(4)]
    tick_labs = ['Γ', 'M', 'K', 'Γ']
    ax.set_xticks(tick_locs)
    ax.set_xticklabels(tick_labs, size=16)
    ax.set_ylabel('Frequency (c/a)', size=16)
    ax.set_ylim([0, np.max(te_freqs)])
    ax.grid(True)
    plt.savefig('band_structure_norm_TE.jpg')
    plt.close()                
# ============================================================
#                 TM FIELDS
# ============================================================

    efields = []
    def get_efields(ms, band):
        efields.append(ms.get_efield(band, bloch_phase=True))
    ms.run_tm(mpb.output_at_kpoint(mp.Vector3(), mpb.fix_efield_phase, get_efields))
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

    hfields = []
    def get_hfields(ms, band):
        hfields.append(ms.get_hfield(band, bloch_phase=True))
    ms.run_te(mpb.output_at_kpoint(mp.Vector3(), mpb.output_hfield_z, get_hfields))
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

    for i, f in enumerate(conv_h):
        plt.subplot(num_plot, num_plot, i+1)
        plt.contour(eps_conv.T, cmap='binary')
        plt.imshow(np.abs(f.T), cmap='jet', alpha=0.9)
        plt.axis('off')
    plt.savefig("TE_fields_NORM.jpg", dpi=300, bbox_inches='tight')
    plt.close()
    exit()

root = tk.Tk()
root.geometry('450x425')
#custom_font = font.Font(family="Helvetica", size=12, weight="bold")
#root.configure(bg='black')  # Set background color to black
root.title("Band Structure of 2D Hexagonal Photonic Crystal using MPB")


label1 = ttk.Label(root, text="  Number of bands to compute\n \tflux:(default 8)", font=("bitstream charter", 11))
label1.grid(row=0, column=0, padx=10, pady=5)
#values = ['2','4','6','8','10','12','14','16','18','20']
#dropdown = ttk.Combobox(root, values=values)
#dropdown.grid(row=0, column=1)
#label1.pack()
entry1 = ttk.Entry(root)
entry1.grid(row=0, column=1, padx=10, pady=5)
#entry1.pack()

label2 = ttk.Label(root, text="Side length 'a' in nm: \n (default 1000)", font=("bitstream charter", 11))
label2.grid(row=1, column=0, padx=10, pady=5)
#label2.pack()
entry2 = ttk.Entry(root)
entry2.grid(row=1, column=1, padx=10, pady=5)
#entry2.pack()

label3 = ttk.Label(root, text="r/a ratio: \n (default 0.2)", font=("bitstream charter", 11))
label3.grid(row=2, column=0, padx=10, pady=5)
#label3.pack()
entry3 = ttk.Entry(root)
entry3.grid(row=2, column=1, padx=10, pady=5)
#entry3.pack()

label4 = ttk.Label(root, text="Dielectric constant of dielectric cylinder \n (default 11.7)", font=("bitstream charter", 11))
label4.grid(row=3, column=0, padx=10, pady=5)
#label4.pack()
entry4 = ttk.Entry(root)
entry4.grid(row=3, column=1, padx=10, pady=5)
#entry4.pack()

label5 = ttk.Label(root, text="  Number of Interpolation points: \n (default 4)", font=("bitstream charter", 11))
label5.grid(row=4, column=0, padx=10, pady=5)
#label6.pack()
entry5 = ttk.Entry(root)
entry5.grid(row=4, column=1, padx=10, pady=5)

label6 = ttk.Label(root, text="  Resolution: \n (default 32)", font=("bitstream charter", 11))
label6.grid(row=5, column=0, padx=10, pady=5)
#label6.pack()
entry6 = ttk.Entry(root)
entry6.grid(row=5, column=1, padx=10, pady=5)
#entry6.pack()




button = ttk.Button(root, text="Run", command=run_code)
button.grid(row=9, column=1, padx=10, pady=5)
#run_button.pack()

root.mainloop()
