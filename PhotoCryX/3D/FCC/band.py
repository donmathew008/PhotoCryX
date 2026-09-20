import tkinter as tk
from tkinter import ttk  

def run_code():
    N1 = entry1.get()
    m1 = entry2.get()
    Resolution1 = entry3.get() 
    epsilon1 = entry4.get()
    r1 = entry5.get()
    interpolation1 = entry6.get()
     
    
    import math
    import h5py
    import numpy as np
    import matplotlib.pyplot as plt
    import meep as mp
    from meep import mpb
    
    num_bands = int(N1)
    mesh_size = int(m1)
    resolution = int(Resolution1)
    interpolation = int(interpolation1)
    r =float(r1)
    eps = float(epsilon1)
    geometry_lattice = mp.Lattice(
        basis1=mp.Vector3(0.5, 0, 0.5),
        basis2=mp.Vector3(0.5, 0.5, 0),
        basis3=mp.Vector3(0, 0.5, 0.5)
    )



    vlist = [
        mp.Vector3(0, 0.5, 0.5),        # X
        mp.Vector3(0.25, 0.625, 0.625),    # U
        mp.Vector3(0.5, 0.5, 0.5),          # L
        mp.Vector3(0, 0, 0),            # Gamma
        mp.Vector3(0, 0.5, 0.5),        # X
        mp.Vector3(0.25, 0.75, 0.5),    # W
        mp.Vector3(0.375, 0.75, 0.375)  # K
    ]
    k_points = mp.interpolate(interpolation, vlist) # 4


    diel = mp.Medium(epsilon=eps)

    geometry = [mp.Sphere(r, center=mp.Vector3(0, 0, 0), material=diel)]


    ms = mpb.ModeSolver(
        geometry_lattice=geometry_lattice,
        k_points=k_points,
        geometry=geometry,
        resolution=resolution,
        num_bands=num_bands,
        mesh_size=mesh_size
    )


# run calculation, outputting electric_field energy density at the U point:
    ms.run(mpb.output_at_kpoint(mp.Vector3(0, 0, 0), mpb.output_dpwr))
    ms.output_epsilon()
    td_freqs = ms.all_freqs
    td_gaps = ms.gap_list
    
#plot epsilon function
    md = mpb.MPBData(lattice=ms.get_lattice(), rectify=True, periods=3, resolution=512)
    eps1 = ms.get_lattice()
    converted_eps = md.convert(eps1)
    plt.imshow(converted_eps.T, interpolation='spline36', cmap='binary')
    plt.axis('off')
    plt.savefig('epsilon.jpg')
    plt.savefig('epsilon_2D.eps', format='eps')
    plt.close()
#plt.show()
    with h5py.File('epsilon.h5', 'w') as f:
        f.create_dataset('data-new', data=converted_eps)

    fig, ax = plt.subplots()
    x = range(len(td_freqs))
# Plot bands
# Scatter plot for multiple y values, see https://stackoverflow.com/a/34280815/2261298
#    for xz, tmz in zip(x, td_freqs):
#        ax.scatter([xz]*len(tmz), tmz, color='black')
    #ax.scatter([xz]*len(tez), tez, color='red', facecolors='none')
    ax.plot(td_freqs, color='blue')
#ax.plot(te_freqs, color='red')
    ax.set_ylim([0, 0.6])
    ax.set_xlim([x[0], x[-1]])

# Plot gaps
    for gap in td_gaps:
        if gap[0] > 1:
            ax.fill_between(x, gap[1], gap[2], color='blue', alpha=0.2)
    points_in_between = (len(td_freqs) - 7) / 6
    tick_locs = [i*points_in_between+i for i in range(7)]
    tick_labs = ['X', 'U', 'L', 'Γ', 'X', 'W', 'K']
    ax.set_xticks(tick_locs)
    ax.set_xticklabels(tick_labs, size=16)
    ax.set_ylabel('Frequency (c/a)', size=16)
    ax.set_ylim([0, np.max(td_freqs)])
    ax.grid(True)
    plt.savefig('band_structure.jpg')
    plt.close()


# ============================================================
#              non Norm
# ============================================================

    fig, ax = plt.subplots()
    x = range(len(td_freqs * 300))
    ax.plot(td_freqs * 300, color='red')
    ax.set_xlim([x[0], x[-1]])
    for gap in td_gaps:
        if gap[0] > 1:
            ax.fill_between(x, gap[1] * 300, gap[2] * 300, color='red', alpha=0.5)
    #ax.text(13.05, 0.235, 'TE', color='red', size=15)

    points_in_between = (len(td_freqs) - 7) / 6
    tick_locs = [i*points_in_between+i for i in range(7)]
    tick_labs = ['X', 'U', 'L', 'Γ', 'X', 'W', 'K']
    ax.set_xticks(tick_locs)
    ax.set_xticklabels(tick_labs, size=16)
    ax.set_ylabel('Frequency (THz)', size=16)
    ax.set_ylim([0, np.max(td_freqs * 300)])
    ax.grid(True)
    plt.savefig('band_structure_non.jpg')
    plt.close()    
    
    
    N = num_bands     # total number of field plots
    num_plot = math.ceil(math.sqrt(N)) 
#    eps_conv = md.convert(ms.get_epsilon())

            
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
#        plt.contour(eps_conv.T, cmap='binary')
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
#        plt.contour(eps_conv.T, cmap='binary')
        plt.imshow(np.real(f).T, cmap='jet', alpha=0.9)
        plt.axis('off')
    plt.savefig("TE_fields.jpg", dpi=300, bbox_inches='tight')
    plt.close()

# ============================================================
#                 TM FIELDS NORM
# ============================================================
 
    for i, f in enumerate(conv_e):
        plt.subplot(num_plot, num_plot, i+1)
#        plt.contour(eps_conv.T, cmap='binary')
        plt.imshow(np.abs(f.T), cmap='jet', alpha=0.9)
        plt.axis('off')
    plt.savefig("TM_fields_NORM.jpg", dpi=300, bbox_inches='tight')
    plt.close()


# ============================================================
#                 TE FIELDS NORM
# ============================================================

    for i, f in enumerate(conv_h):
        plt.subplot(num_plot, num_plot, i+1)
#        plt.contour(eps_conv.T, cmap='binary')
        plt.imshow(np.abs(f.T), cmap='jet', alpha=0.9)
        plt.axis('off')
    plt.savefig("TE_fields_NORM.jpg", dpi=300, bbox_inches='tight')
    plt.close()
    exit()


root = tk.Tk()
root.geometry('450x425')
#custom_font = font.Font(family="Helvetica", size=12, weight="bold")
#root.configure(bg='black')  # Set background color to black
root.title("Band Structure of 3D FCC Photonic Crystal using MPB")


label1 = ttk.Label(root, text="Number of bands to compute\n \tflux:(default 5)", font=("bitstream charter", 11))
label1.grid(row=0, column=0, padx=10, pady=5)
entry1 = ttk.Entry(root)
entry1.grid(row=0, column=1, padx=10, pady=5)
#entry1.pack()

label2 = ttk.Label(root, text="Mesh Size: \n (default 5)", font=("bitstream charter", 11))
label2.grid(row=1, column=0, padx=10, pady=5)
entry2 = ttk.Entry(root)
entry2.grid(row=1, column=1, padx=10, pady=5)
#entry2.pack()

label3 = ttk.Label(root, text="  Resolution: \n (default 16)", font=("bitstream charter", 11))
label3.grid(row=2, column=0, padx=10, pady=5)
entry3 = ttk.Entry(root)
entry3.grid(row=2, column=1, padx=10, pady=5)
#entry3.pack()

label4 = ttk.Label(root, text="Dielectric constant of dielectric sphere \n (default 13)", font=("bitstream charter", 11))
label4.grid(row=3, column=0, padx=10, pady=5)
entry4 = ttk.Entry(root)
entry4.grid(row=3, column=1, padx=10, pady=5)
#entry4.pack()

label5 = ttk.Label(root, text="Radius of Sphere: \n (default 0.3)", font=("bitstream charter", 11))
label5.grid(row=4, column=0, padx=10, pady=5)
entry5 = ttk.Entry(root)
entry5.grid(row=4, column=1, padx=10, pady=5)

label6 = ttk.Label(root, text="Number of Interpolation points: \n (default 4)", font=("bitstream charter", 11))
label6.grid(row=5, column=0, padx=10, pady=5)
entry6 = ttk.Entry(root)
entry6.grid(row=5, column=1, padx=10, pady=5)
#entry6.pack()




button = ttk.Button(root, text="Run", command=run_code)
button.grid(row=9, column=1, padx=10, pady=5)
#run_button.pack()

#reset_button = tk.Button(root, text="Reset", command=reset_fields)
#reset_button.pack()

root.mainloop()
