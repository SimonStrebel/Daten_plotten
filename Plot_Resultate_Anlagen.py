import pandas as pd
import yaml
from matplotlib import pyplot as plt
import matplotlib
import mpl_axes_aligner
import numpy as np

# Einstellungen das alle Daten sichtbar wenn DF angezeigt werden soll:
pd.set_option('display.max_columns', 150)
pd.set_option('display.width', 2000)

# Pfad Datei und ablage Plot importieren:
with open(f'Config_Resultat_Plot.yaml', 'r') as Inputs:
    inputs = yaml.safe_load(Inputs)

Pfad_Datei = inputs['Pfad_Datei_Resultate']
Pfad_Plot = inputs['Pfad_Plot']
Pfad_Plot_Poster = inputs['Pfad_Plot_Poster']

# CSV Files einlesen
df = pd.read_csv(f'{Pfad_Datei}')
# print(f'{df} \n')

# Daten günstigste Li-Systeme für Plot in eigenes DF
df_Plot = df.nsmallest(6, 'Anlagekosten mit Li-Batterie [CHF]', keep='all')

# Nach PV-Leistung sortieren
df_Plot.sort_values(by=['PV-Leistungen [W]'], inplace=True)
print(f'{df_Plot} \n')

# Schriftgrösse einstellen
matplotlib.rcParams.update({'font.size': 14})

# Plot der Systemkosten und Batteriegrösse in Abhängigkeit der PV-Leistung (Lithium)
fig, ax1 = plt.subplots(figsize=(10, 6))
ax1_sek = ax1.twinx()
# fig.suptitle(f'Systemkosten Off-Grid-Anlage', fontweight='bold')
ax1.plot(df_Plot['PV-Leistungen [W]'], df_Plot['Anlagekosten mit Li-Batterie [CHF]'], linewidth=2.5, marker='x', markersize=8, color='#C20078')
ax1_sek.plot(df_Plot['PV-Leistungen [W]'], df_Plot['Batteriegrösse Li [Wh]'], linewidth=2.5, marker='x', markersize=8, color='#069AF3')

# Reihenfolge bei überschreitenden Linien vorgeben und sicherstellen, dass nichts ausgeblendet wird:
ax1.set_zorder(2)
ax1_sek.set_zorder(1)
ax1.set_frame_on(False)

# Darstellungen Plot:
ax1.tick_params(axis='x', labelrotation=0)
ax1.set_xlabel('PV-Leistung [Wp]', labelpad=10)
ax1.set_xticks(np.arange(120, 320, 20))

ax1.set_ylabel('Systemkosten [CHF]', color='#C20078', labelpad=5)
ax1.tick_params(axis='y', colors='#C20078')
y0_ax1 = 400
ax1.set_yticks(np.arange(y0_ax1, 660, 20))
mpl_axes_aligner.shift.yaxis(ax=ax1, org=y0_ax1 , pos=0)
#ax1.grid(linewidth=0.75, zorder=-10)

ax1_sek.set_ylabel('Batteriegrösse [Wh]', color='#069AF3', labelpad=15)
ax1_sek.tick_params(axis='y', colors='#069AF3')
y0_axsek = 150
ax1_sek.set_yticks(np.arange(y0_axsek, 700, 50))
mpl_axes_aligner.shift.yaxis(ax=ax1_sek, org=y0_axsek , pos=0)
#ax1_sek.grid(linewidth=0.75, zorder=-10)

# Ausgabe und speichern:
plt.tight_layout()
plt.show()
speichern_als = f'{Pfad_Plot}/Plot_Li_besteAnlagen.jpg'
fig.savefig(speichern_als, dpi=500)
plt.clf()
plt.close()

# POSTER-PLOT (QUADRATISCH) der Systemkosten und Batteriegrösse in Abhängigkeit der PV-Leistung (Lithium)
fig, ax1 = plt.subplots(figsize=(10, 10))
ax1_sek = ax1.twinx()
# fig.suptitle(f'Systemkosten Off-Grid-Anlage', fontweight='bold')
ax1.plot(df_Plot['PV-Leistungen [W]'], df_Plot['Anlagekosten mit Li-Batterie [CHF]'], linewidth=2.5, marker='x', markersize=8, color='#C20078')
ax1_sek.plot(df_Plot['PV-Leistungen [W]'], df_Plot['Batteriegrösse Li [Wh]'], linewidth=2.5, marker='x', markersize=8, color='#069AF3')

# Reihenfolge bei überschreitenden Linien vorgeben und sicherstellen, dass nichts ausgeblendet wird:
ax1.set_zorder(2)
ax1_sek.set_zorder(1)
ax1.set_frame_on(False)

# Darstellungen Plot:
ax1.tick_params(axis='x', labelrotation=0)
ax1.set_xlabel('PV-Leistung [Wp]', labelpad=10)
ax1.set_xticks(np.arange(120, 320, 20))

ax1.set_ylabel('Systemkosten [CHF]', color='#C20078', labelpad=5)
ax1.tick_params(axis='y', colors='#C20078')
y0_ax1 = 400
ax1.set_yticks(np.arange(y0_ax1, 660, 20))
mpl_axes_aligner.shift.yaxis(ax=ax1, org=y0_ax1 , pos=0)
#ax1.grid(linewidth=0.75, zorder=-10)

ax1_sek.set_ylabel('Batteriegrösse [Wh]', color='#069AF3', labelpad=15)
ax1_sek.tick_params(axis='y', colors='#069AF3')
y0_axsek = 150
ax1_sek.set_yticks(np.arange(y0_axsek, 700, 50))
mpl_axes_aligner.shift.yaxis(ax=ax1_sek, org=y0_axsek , pos=0)
#ax1_sek.grid(linewidth=0.75, zorder=-10)

# Ausgabe und speichern:
plt.tight_layout()
plt.show()
speichern_als = f'{Pfad_Plot_Poster}/Plot_Li_besteAnlagen.jpg'
fig.savefig(speichern_als, dpi=500)
plt.clf()
plt.close()