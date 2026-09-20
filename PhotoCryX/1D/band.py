import tkinter as tk
from tkinter import ttk

def run_code():
    N1 = entry1.get()
    da_n1 = entry2.get()
    db_n1 = entry3.get()
    na1 = entry4.get()
    nb1 = entry5.get()
    Resolution1 = entry6.get()
    interpolation1 = entry7.get()
    
    
    import numpy as np
    import matplotlib.pyplot as plt
    import math
    import meep as mp
    from meep import mpb
    num_bands = int(N1)
    interpolation = int(interpolation1)
    
    k_points = [mp.Vector3(-0.5),          # Gamma
                mp.Vector3(),       # X
                mp.Vector3(0.5)]          # Gamma
    k_points = mp.interpolate(interpolation, k_points)

    k_plot_points = np.linspace(-0.5, 0.5, 43) # np.linspace(-0.5, 0.5, #N) #N = 2*no:of kpoints + 3
    da = int(da_n1)/1000 # in um
    db = int(db_n1)/1000 # in um
    P = da + db # Period
    na = float(na1) # Refractive index of layer A
    nb = float(nb1) # Refractive index of layer B
    epsa = na**2 # Dielectric constant of layer A
    epsb = nb**2 # Dielectric constant of layer B
    c_a1 = -P/2 + da/4
    c_a2 = P/2 - da/4

    ht = 0.1

    geometry = [
        mp.Block(mp.Vector3(da/2, ht, 0),center=mp.Vector3(c_a1, 0, 0),material=mp.Medium(epsilon=epsa),),
        mp.Block(mp.Vector3(db, ht, 0),center=mp.Vector3(0, 0, 0),material=mp.Medium(epsilon=epsb),),
       mp.Block(mp.Vector3(da/2, ht, 0),center=mp.Vector3(c_a2, 0, 0),material=mp.Medium(epsilon=epsa),),
   ]

    geometry_lattice = mp.Lattice(size=mp.Vector3(P, ht))

    resolution = int(Resolution1)
    ms = mpb.ModeSolver(num_bands=num_bands,
                        k_points=k_points,
                        geometry=geometry,
                        geometry_lattice=geometry_lattice,
                        resolution=resolution)


    ms.run_tm()
    ms.run_tm(mpb.output_efield_z)


    tm_freqs = ms.all_freqs
    tm_gaps = ms.gap_list
#ms.run_te()
    ms.run_te()
    ms.run_te(mpb.output_at_kpoint(mp.Vector3(0.5), mpb.output_hfield_z, mpb.output_dpwr))
    ms.output_epsilon()
    te_freqs = ms.all_freqs
    te_gaps = ms.gap_list

#plot epsilon function
    md = mpb.MPBData(rectify=True, periods=1, resolution=512)
    eps = ms.get_epsilon()
    converted_eps = md.convert(eps)
    plt.imshow(converted_eps.T, interpolation='spline36', cmap='binary')
    plt.axis('off')
    plt.savefig('epsilon.jpg')
    plt.close()


# ============================================================
#                 Band Structure Plots
# ============================================================
#              1. scatter plot normalized
# ============================================================

    fig, ax = plt.subplots()
    #fig, ax = plt.subplots(figsize=(7.5, 10))
    x = range(len(tm_freqs*P))
#    for xz, tmz, tez in zip(x, tm_freqs, te_freqs):
#        ax.scatter([xz]*len(tmz), tmz, color='blue')
#        ax.scatter([xz]*len(tez), tez, color='red', facecolors='none')
    ax.plot(tm_freqs*P, color='blue')
#    ax.plot(te_freqs, color='red')
    ax.set_xlim([x[0], x[-1]])
    for gap in tm_gaps:
        if gap[0] > 1:
            ax.fill_between(x, gap[1]*P, gap[2]*P, color='blue', alpha=0.2)

#    for gap in te_gaps:
#        if gap[0] > 1:
#            ax.fill_between(x, gap[1], gap[2], color='red', alpha=0.2)
#    ax.text(12, 0.04, 'TM', color='blue', size=15)
#    ax.text(13.05, 0.235, 'TE', color='red', size=15)

    points_in_between = (len(tm_freqs) - 3) / 2
    tick_locs = [i*points_in_between+i for i in range(3)]
    tick_labs = ['-X','Γ', 'X']
    ax.set_xticks(tick_locs)
    ax.set_xticklabels(tick_labs, size=16)
    ax.set_ylabel('Frequency (c/a)', size=16)
    ax.set_ylim([0, np.max(tm_freqs*P)])
    #ax.grid(True)
    plt.savefig('band_structure.jpg')
    plt.close()


  
    
# ============================================================
#              5. Band
# ============================================================

    fig, ax = plt.subplots()
    #fig, ax = plt.subplots(figsize=(7.5, 10))
    x = range(len(tm_freqs * 300))
    ax.plot(tm_freqs * 300, color='blue')
    ax.set_xlim([x[0], x[-1]])
    for gap in tm_gaps:
        if gap[0] > 1:
            ax.fill_between(x, gap[1] * 300, gap[2] * 300, color='blue', alpha=0.2)

#    ax.text(12, 0.04, 'TM', color='blue', size=15)
    points_in_between = (len(tm_freqs) - 3) / 2
    tick_locs = [i*points_in_between+i for i in range(3)]
    tick_labs = ['-X','Γ', 'X']
    ax.set_xticks(tick_locs)
    ax.set_xticklabels(tick_labs, size=16)
    ax.set_ylabel('Frequency (THz)', size=16)
    ax.set_ylim([0, np.max(tm_freqs * 300)])
    #ax.grid(True)
    plt.savefig('band_structure_non.jpg')
    plt.close()    
    
    N = num_bands     # total number of field plots
    num_plot = math.ceil(math.sqrt(N)) 
    eps_conv = md.convert(ms.get_epsilon())

            
# ============================================================
#                 FIELDS
# ============================================================

    efields = []
    def get_efields(ms, band):
        efields.append(ms.get_efield(band, bloch_phase=False))
    ms.run_tm(mpb.output_at_kpoint(mp.Vector3(), mpb.fix_efield_phase, get_efields))
#    ms.run_tm(mpb.output_at_kpoint(mp.Vector3(), get_efields))
    conv_e = [md.convert(f[..., 0, 2]) for f in efields[:num_bands]]
    for i, f in enumerate(conv_e):
        plt.subplot(num_plot, num_plot, i+1)
        plt.contour(eps_conv.T, cmap='binary')
        plt.imshow(np.real(f).T, cmap='jet', alpha=0.9)
        plt.axis('off')
    plt.savefig("fields.jpg", dpi=300, bbox_inches='tight')
    plt.close()


# ============================================================
#                 FIELDS NORM
# ============================================================
 
    for i, f in enumerate(conv_e):
        plt.subplot(num_plot, num_plot, i+1)
        plt.contour(eps_conv.T, cmap='binary')
        plt.imshow(np.abs(f.T), cmap='jet', alpha=0.9)
        plt.axis('off')
    plt.savefig("fields_NORM.jpg", dpi=300, bbox_inches='tight')
    plt.close()
    exit()


#
root = tk.Tk()
root.geometry('425x425')
#custom_font = font.Font(family="Helvetica", size=12, weight="bold")
#root.configure(bg='black')  # Set background color to black
root.title("Band Structure of 1D Photonic Crystal using MPB GUI")


label1 = ttk.Label(root, text="  Number of bands to compute\n \tflux:(default 8)", font=("bitstream charter", 11))
label1.grid(row=0, column=0, padx=10, pady=5)
#values = ['2','4','6','8','10','12','14','16','18','20']
#dropdown = ttk.Combobox(root, values=values)
#dropdown.grid(row=0, column=1)
#label1.pack()
entry1 = ttk.Entry(root)
entry1.grid(row=0, column=1, padx=10, pady=5)
#entry1.pack()

label2 = ttk.Label(root, text="Width of layer 'A' in nm:", font=("bitstream charter", 11))
label2.grid(row=1, column=0, padx=10, pady=5)
#label2.pack()
entry2 = ttk.Entry(root)
entry2.grid(row=1, column=1, padx=10, pady=5)
#entry2.pack()

label3 = ttk.Label(root, text="Width of layer 'B' in nm:", font=("bitstream charter", 11))
label3.grid(row=2, column=0, padx=10, pady=5)
#label3.pack()
entry3 = ttk.Entry(root)
entry3.grid(row=2, column=1, padx=10, pady=5)
#entry3.pack()

label4 = ttk.Label(root, text="Refractive index of layer A:", font=("bitstream charter", 11))
label4.grid(row=3, column=0, padx=10, pady=5)
#label4.pack()
entry4 = ttk.Entry(root)
entry4.grid(row=3, column=1, padx=10, pady=5)
#entry4.pack()

label5 = ttk.Label(root, text="Refractive index of layer B:", font=("bitstream charter", 11))
label5.grid(row=4, column=0, padx=10, pady=5)
#label5.pack()
entry5 = ttk.Entry(root)
entry5.grid(row=4, column=1, padx=10, pady=5)
#entry5.pack()

label6 = ttk.Label(root, text="  Resolution: \n (default 128)", font=("bitstream charter", 11))
label6.grid(row=5, column=0, padx=10, pady=5)
#label6.pack()
entry6 = ttk.Entry(root)
entry6.grid(row=5, column=1, padx=10, pady=5)
#entry6.pack()


label7 = ttk.Label(root, text="  Number of Interpolation points: \n (default 20)", font=("bitstream charter", 11))
label7.grid(row=6, column=0, padx=10, pady=5)
#label6.pack()
entry7 = ttk.Entry(root)
entry7.grid(row=6, column=1, padx=10, pady=5)

button = ttk.Button(root, text="Run", command=run_code)
button.grid(row=9, column=1, padx=10, pady=5)
#run_button.pack()

root.mainloop()
