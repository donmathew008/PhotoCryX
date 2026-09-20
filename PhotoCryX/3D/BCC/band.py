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
#    from mayavi import mlab
    import numpy as np
    import matplotlib.pyplot as plt
    import meep as mp
    from meep import mpb
    
    num_bands = int(N1)
    mesh_size = int(m1)
    resolution = int(Resolution1)
    interpolation = int(interpolation1)
    r = float(r1)
    eps = float(epsilon1)

    # ============================================================
    #                 BCC LATTICE 
    # ============================================================
    geometry_lattice = mp.Lattice(
        basis1=mp.Vector3(0.5, 0.5, -0.5),
        basis2=mp.Vector3(-0.5, 0.5, 0.5),
        basis3=mp.Vector3(0.5, -0.5, 0.5)
    )

    # ============================================================
    #                 BCC K-PATH
    # ============================================================
    vlist = [
#        mp.Vector3(0, 0, 0),            # Γ
        mp.Vector3(-0.5, 0.5, 0.5),     # H
        mp.Vector3(0, 0.5, 0),          # N
        mp.Vector3(0, 0, 0),            # Γ
        mp.Vector3(0.25, 0.25, 0.25),   # P
        mp.Vector3(-0.5, 0.5, 0.5)      # H
    ]

    k_points = mp.interpolate(interpolation, vlist)

    diel = mp.Medium(epsilon=eps)

    # ============================================================
    #                 GEOMETRY (ONLY ONE SPHERE)
    # ============================================================
    geometry = [
        mp.Sphere(r, center=mp.Vector3(0, 0, 0), material=diel)
    ]

    ms = mpb.ModeSolver(
        geometry_lattice=geometry_lattice,
        k_points=k_points,
        geometry=geometry,
        resolution=resolution,
        num_bands=num_bands,
        mesh_size=mesh_size
    )

    # Run TM bands
#    ms.run_tm()
    ms.run(mpb.output_at_kpoint(mp.Vector3(0, 0, 0), mpb.output_dpwr))
    ms.output_epsilon()
    td_freqs = ms.all_freqs
    td_gaps = ms.gap_list

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
    # ============================================================
    #                 BAND STRUCTURE 
    # ============================================================
    fig, ax = plt.subplots()
    x = range(len(td_freqs))

    for i in range(min(6, num_bands)):
        ax.plot(td_freqs[:, i], color='blue')

    ax.set_xlim([x[0], x[-1]])
    ax.set_ylim([0, np.max(td_freqs)])

    # Plot gaps
    for gap in td_gaps:
        if gap[0] > 1:
            ax.fill_between(x, gap[1], gap[2], color='blue', alpha=0.2)

    # Correct tick placement
    num_k = len(vlist)
    points_in_between = (len(td_freqs) - num_k) / (num_k - 1)
    tick_locs = [i * (points_in_between + 1) for i in range(num_k)]
    tick_labs = ['H', 'N', 'Γ', 'P', 'H']

    ax.set_xticks(tick_locs)
    ax.set_xticklabels(tick_labs, size=14)

    ax.set_ylabel('Frequency (c/a)', size=14)
    ax.grid(True)

    plt.savefig('band_structure.jpg')
    plt.close()

    # ============================================================
    #                 NON-NORMALIZED (THz approx)
    # ============================================================
    fig, ax = plt.subplots()
    scale = 300

    for i in range(min(6, num_bands)):
        ax.plot(td_freqs[:, i] * scale, color='red')

    for gap in td_gaps:
        if gap[0] > 1:
            ax.fill_between(x, gap[1]*scale, gap[2]*scale, color='red', alpha=0.3)

    ax.set_xticks(tick_locs)
    ax.set_xticklabels(tick_labs, size=14)

    ax.set_ylabel('Frequency (THz)', size=14)
    ax.set_ylim([0, np.max(td_freqs * scale)])
    ax.grid(True)

    plt.savefig('band_structure_non.jpg')
    plt.close()
    exit()


# ============================================================
#                 GUI
# ============================================================

root = tk.Tk()
root.geometry('450x425')
#custom_font = font.Font(family="Helvetica", size=12, weight="bold")
#root.configure(bg='black')  # Set background color to black
root.title("Band Structure of 3D BCC Photonic Crystal using MPB")


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

label5 = ttk.Label(root, text="Radius of Sphere: \n (default 0.4)", font=("bitstream charter", 11))
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


root.mainloop()
