#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 18 11:54:03 2017

@author: Maciej Sciesiek
"""
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.gridspec as gridspec
import numpy as np
from scipy import signal

ktory_folder = 'TEM_Jola'
if ktory_folder == 'Jola':
    src = '/mnt/Dane/0_Microcavities/UW0707/TEM/Jola'
    rysunki = [['0707_2_cd.jpg', 'red', 700],
               ['0707_3_cd_mg.jpg', 'blue', 200],
               ['0707_1_mg.jpg', 'green', 100],
               ['0707_2_mg.jpg', 'green', 200],
               ['0707_3_mg.jpg', 'green', 100],
               ['0707_3_mn.jpg', 'blue', 100],
               ['0707_6_cd_mg.jpg', 'blue', 40],
               ['0707_6_mg.jpg', 'blue', 40]]
elif ktory_folder == 'TEM_Jola':
    src = '/mnt/Dane/0_Microcavities/UW0707/TEM/TEM_Jola'
    rysunki = [['0707_1_cd.jpg', 'red', 3000],
               ['0707_1_mg.jpg', 'blue', 3000],
               ['0707_2_mg.jpg', 'blue', 700],
               ['0707_3_mg.jpg', 'blue', 200],
               ['0707_4_mg.jpg', 'blue', 90]]
else:
    print('nie ma takiego folderu')
    raise ValueError

ktory = 0
rys = rysunki[ktory][0]
ktory_rysowac = rysunki[ktory][1]  # r, b, g, colokwiek
skala = rysunki[ktory][2]  # dlugosc paska w nm
# %% -----------------------------------------------------------------
# wczytanie danych
obrazek = mpimg.imread(src + '/' + rys)
r_whole = obrazek[:, :, 0]
g_whole = obrazek[:, :, 1]
b_whole = obrazek[:, :, 2]

r = np.sum(r_whole, axis=1)
g = np.sum(g_whole, axis=1)
b = np.sum(b_whole, axis=1)

# dlugosc podzialki
pasek = 0
for i in range(round(len(r)*9/10), round(len(r) * 98/100)):
    p_r = r_whole[i, :]
    p_g = g_whole[i, :]
    p_b = b_whole[i, :]
    pasek_i = np.sum((p_r > 253) & (p_g > 253) & (p_b > 253))
    if pasek_i > pasek:
        pasek = pasek_i
print('Dlugosc paska na obrazku to ' + str(pasek) + ' pix')

# pozycje w połowie wysokości:
if ktory_rysowac == 'red':
    tot = r
elif ktory_rysowac == 'green':
    tot = g
elif ktory_rysowac == 'blue':
    tot = b
else:
    tot = r+g+b

total = np.around(signal.savgol_filter(tot, 11, 3)).astype(int)
half = (total.max() - total.min())/2 + total.min()
in_half = total - half

# znalezienie zgrubne
points = []
for i in range(len(in_half)-1):
    if ((in_half[i] > 0) and (in_half[i+1] < 0)) or \
       ((in_half[i] < 0) and (in_half[i+1] > 0)):
            points.append(i + (abs(in_half[i]) /
                          (abs(in_half[i]) + abs(in_half[i+1]))))
# znalezienie dokladne
point_prec = []
half_prec = []
for i in range(len(points)):
    if i == 0:
        ind_lo = 0
        ind_hi = int(round(points[i+1]))
    elif i == len(points)-1:
        ind_lo = int(round(points[i-1]))
        ind_hi = int(len(r))
    else:
        ind_lo = int(round(points[i-1]))
        ind_hi = int(round(points[i+1]))
    loc_min = min(tot[ind_lo:ind_hi])
    loc_max = max(tot[ind_lo:ind_hi])
    loc_half = (loc_max - loc_min)/2 + loc_min
    half_prec.append(loc_half)
    loc_in_h = total - loc_half
    points_prec = []
    for i in range(len(in_half)-1):
        if ((loc_in_h[i] > 0) and (loc_in_h[i+1] < 0)) or \
           ((loc_in_h[i] < 0) and (loc_in_h[i+1] > 0)):
                points_prec.append(i + (abs(loc_in_h[i]) /
                                   (abs(loc_in_h[i]) + abs(loc_in_h[i+1]))))
# rysowanie
f = plt.figure()
gs = gridspec.GridSpec(1, 4,
                       height_ratios=[1, ],
                       width_ratios=[12, 3, 3, 2]
                       )
gs.update(wspace=0, hspace=0.1)  # spacing between axes
ax1 = plt.subplot(gs[0])
ax2 = plt.subplot(gs[1])
ax3 = plt.subplot(gs[2])


ax1.imshow(obrazek)
plt.text(-4*max(tot), 980, '--- = ' + str(pasek) + ' pix', color='b',
         backgroundcolor='w')

x = [i for i in range(len(r))]
ax2.plot(r, x, '-r')
ax2.plot(g, x, '-g')
ax2.plot(b, x, '-b')
ax2.set_ylim([0, len(r)])
ax2.invert_yaxis()
ax2.yaxis.set_ticklabels([])
ax2.xaxis.set_ticklabels([])
ax2.xaxis.set_ticks([])
plt.title('RBG')

ax3.plot(tot, x, '-k')
ax3.set_ylim([0, len(r)])
ax3.invert_yaxis()
plt.title(ktory_rysowac)
ax3.yaxis.set_ticklabels([])
plt.ticklabel_format(style='sci', axis='x', scilimits=(0, 0))

# rysowanie gdzie polowa wysokosci
for i in range(len(points_prec)):
    ax3.plot([0, max(tot)], [points_prec[i], points_prec[i]], color='b',
             ls='--', lw=0.5, alpha=0.5)
    ax3.scatter(half_prec[i], points_prec[i], color='b',
                linewidths=1, alpha=0.5, s=3)

# napisanie odleglosci miedzy punktami
for i in range(len(points_prec)-1):
    diff = points_prec[i+1] - points_prec[i]
    poz = (points_prec[i] + points_prec[i+1])/2
    pozx = 2.5*max(tot)
    plt.text(pozx, poz, '%02.1f nm (%2.1f pix)' % (skala*diff/pasek, diff),
             color='b', va='center', ha='right', size='xx-small')

params_fig_tgt = src + '/' + rys.split('.')[0] + '_hor_prof.png'
plt.savefig(params_fig_tgt, dpi=300)
plt.close()
