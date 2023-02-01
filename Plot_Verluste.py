import pandas as pd
import yaml
from matplotlib import pyplot as plt
import matplotlib.dates as mdates
import os
import matplotlib

# Schriftgrösse einstellen
matplotlib.rcParams.update({'font.size': 14})

# Informationen importieren
with open(f'Config_Verlust_Plot.yaml', 'r') as Inputs:
    inputs = yaml.safe_load(Inputs)

Pfad_Datei = inputs['Pfad Datei']
Pfad_Resultate = inputs['Pfad Resultate']
Dateiname_Verlustplot = inputs['Dateiname']
Dateiname_Gesamtenergieplot = inputs['Dateiname Gesamtenergie']
MPPT_Wirkungsgrad = inputs['MPPT_Wirkungsgrad']/100
MPPT_Eigenverbrauch = inputs['MPPT_Eigenverbrauch']
MPPT_Trackingverlust = inputs['MPPT_Trackingverlust']

# CSV-Datei einlesen
df_Daten = pd.read_csv(f"{Pfad_Datei}", index_col='Datum und Zeit')
df_Daten.index = pd.to_datetime(df_Daten.index, format='%Y-%m-%d %H:%M:%S')

# Anzahl Jahre Datensatz bestimmen
anzahl_jahre = df_Daten.index.year.max() - df_Daten.index.year.min() + 1

# Spaltenname PV-Leistung und Batteriestand bestimmen, damit diese Spalte genutzt werden kann
df_pvleistung = df_Daten.filter(regex='Leistung PV')
for spalte_pvleistung in df_pvleistung.columns:
    pvleistung = spalte_pvleistung

df_batteriestand = df_Daten.filter(regex='Batteriestand')
for spalte_batteriestand in df_batteriestand.columns:
    batteriestand = spalte_batteriestand
    # Ausserdem Batteriegrösse speichern:
    batteriegrösse = df_Daten.filter(regex='Batteriestand').max()[0]

# Siehe Projektbericht, Kapitel "limitierender Parameter" zur Erläuterung, welcher Verlust wie berechnet wird
# Verluste PV-Überschuss
df_Daten.loc[(df_Daten[batteriestand] == batteriegrösse) & (df_Daten[pvleistung] > 0), 'Verlust PV-Überschuss [Wh]'] = df_Daten[pvleistung]*0.25 - df_Daten['Energiebedarf 1/4h Lastbetrieb [Wh]']
df_Daten.loc[(df_Daten[batteriestand] < batteriegrösse) | (df_Daten[pvleistung] == 0), 'Verlust PV-Überschuss [Wh]'] = 0

# Verluste Wirkungsgrad
df_Daten['Verlust Wirkungsgrad [Wh]'] =  ((df_Daten[pvleistung]/MPPT_Wirkungsgrad)-df_Daten[pvleistung])*0.25

# Verluste Tracking
df_Daten.loc[(df_Daten['P_PV [W/Wp]'] > 0), 'Trackingverlust [Wh]'] =  MPPT_Trackingverlust*0.25
df_Daten.loc[(df_Daten['P_PV [W/Wp]'] == 0), 'Trackingverlust [Wh]'] =  0

# Verluste Eigenverbrauch
df_Daten.loc[(df_Daten[pvleistung] > 0) | (df_Daten[batteriestand] > 0), 'Eigenverbrauchsverlust [Wh]'] = MPPT_Eigenverbrauch*0.25
df_Daten.loc[(df_Daten[pvleistung] == 0) & (df_Daten[batteriestand] == 0), 'Eigenverbrauchsverlust [Wh]'] = 0

# Bei PV-Überschuss, werden die anderen Verluste auf 0 gesetzt
df_Daten.loc[(df_Daten['Verlust PV-Überschuss [Wh]'] > 0), 'Verlust Wirkungsgrad [Wh]'] = 0
df_Daten.loc[(df_Daten['Verlust PV-Überschuss [Wh]'] > 0), 'Trackingverlust [Wh]'] = 0
df_Daten.loc[(df_Daten['Verlust PV-Überschuss [Wh]'] > 0), 'Eigenverbrauchsverlust [Wh]'] = 0

# Gesamtverluste der Parameter berechnen [kWh]
Verluste_Wirkungsgrad_ges = df_Daten['Verlust Wirkungsgrad [Wh]'].sum()/1000
Verluste_Tracking_ges = df_Daten['Trackingverlust [Wh]'].sum()/1000
Verluste_Eigenverbrauch_ges = df_Daten['Eigenverbrauchsverlust [Wh]'].sum()/1000
Verluste_PV_Überschuss_ges = df_Daten['Verlust PV-Überschuss [Wh]'].sum()/1000

# PV-Leistung bestimmen, damit gesamte Input-Energie berechnet werden kann
PV_Leistung = ((df_Daten.filter(regex='Leistung PV').max()[0]/MPPT_Wirkungsgrad)+MPPT_Trackingverlust)/df_Daten['P_PV [W/Wp]'].max()
PV_Leistung = round(PV_Leistung, 2)
print(f'Die PV-Leistung der ausgewerteten Anlage beträgt: {PV_Leistung} W')

# Energie ins System berechnen
df_Daten['Energie IN [Wh]'] = df_Daten['P_PV [W/Wp]']*PV_Leistung*0.25
Energie_IN = df_Daten['Energie IN [Wh]'].sum()/1000

# Genutzte Energie Last (ohne Eigenverbrauch, der separat abgezogen wird)
df_Daten.loc[(df_Daten['Status Last'] == 1), 'Genutzte Energie [Wh]'] = df_Daten['Energiebedarf Last [Wh]']
df_Daten.loc[(df_Daten['Status Last'] == 0), 'Genutzte Energie [Wh]'] = 0
Genutzte_Energie = df_Daten['Genutzte Energie [Wh]'].sum()/1000

# Berechnung der weiteren Verluste (dies sind z.B. der Akku-Wirkungsgrad und die Selbsentladung)
# Input abzüglich aller Verluste und der genutzten Energie [kWh]
Weitere_Verluste = Energie_IN - Verluste_Wirkungsgrad_ges - Verluste_Tracking_ges - Verluste_Eigenverbrauch_ges - Verluste_PV_Überschuss_ges - Genutzte_Energie

# Pie-Chart erstellen
names = f'Wirkungsgrad \n{Verluste_Wirkungsgrad_ges:.2f} kWh', f'Tracking \n{Verluste_Tracking_ges:.2f} kWh', f'Eigenverbrauch \n{Verluste_Eigenverbrauch_ges:.2f} kWh'
sizes = [Verluste_Wirkungsgrad_ges, Verluste_Tracking_ges, Verluste_Eigenverbrauch_ges]
colors = ['#4F6272', '#B7C3F3', '#DD7596']

fig, ax1 = plt.subplots(figsize=(12, 6))
#fig.suptitle(f'Mein Titel', fontweight='bold')
patches, texts, autotexts = ax1.pie(sizes, labels=names, labeldistance=1.15, wedgeprops={'linewidth' : 5, 'edgecolor' : 'white'}, colors=colors, autopct='%1.2f%%', pctdistance=0.7, startangle=90)
for autotext in autotexts:
    autotext.set_color('white')
ax1.axis('equal')  # Ensures that pie is drawn as a circle

# Zusatzinfos in Textblock
uberschrift = f' Alle Verluste'
plt.figtext(0.78, 0.78, uberschrift, fontsize=14, weight='bold', horizontalalignment ="left", verticalalignment ="bottom")

text = f' Wirkungsgrad: \n {Verluste_Wirkungsgrad_ges:.2f} kWh \n\n Tracking: \n {Verluste_Tracking_ges:.2f} kWh \n\n Eigenverbrauch: \n {Verluste_Eigenverbrauch_ges:.2f} kWh \n\n PV-Überschuss: \n {Verluste_PV_Überschuss_ges:.2f} kWh \n\n Weitere Verluste: \n {Weitere_Verluste:.2f} kWh \n\n Genutzte Energie: \n {Genutzte_Energie:.2f} kWh'
plt.figtext(0.78, 0.76, text, fontsize=14, style='italic', horizontalalignment ="left", verticalalignment ="top")

# Donut erstellen (weisser Kreis im Zentrum)
centre_circle = plt.Circle((0, 0), 0.4, color='white')
plt.gcf().gca().add_artist(centre_circle)

# Plot zeigen und speichern
plt.tight_layout()
# plt.show()
# speichern_unter = Pfad_Resultate
# fig.savefig(f'{Pfad_Resultate}/{Dateiname_Verlustplot}.jpg', bbox_inches='tight', dpi=500)
plt.clf()
plt.close()

# Pie-Chart Genutzte Energie und Verluste erstellen
summe_verluste = Verluste_Wirkungsgrad_ges + Verluste_Tracking_ges + Verluste_Eigenverbrauch_ges + Weitere_Verluste
summe_gesamt = Genutzte_Energie + Verluste_PV_Überschuss_ges + summe_verluste
names = f'Genutzte Energie \n{Genutzte_Energie/anzahl_jahre:.2f} kWh \n{(Genutzte_Energie/summe_gesamt)*100:.1f} %', f'PV-Überschuss \n{Verluste_PV_Überschuss_ges/anzahl_jahre:.2f} kWh \n{(Verluste_PV_Überschuss_ges/summe_gesamt)*100:.1f} %', f'Verluste \n{summe_verluste/anzahl_jahre:.2f} kWh \n{(summe_verluste/summe_gesamt)*100:.1f} %'
sizes = [Genutzte_Energie/anzahl_jahre, Verluste_PV_Überschuss_ges/anzahl_jahre, summe_verluste/anzahl_jahre]
colors = ['#4F6272', '#B7C3F3', '#DD7596']

fig, ax1 = plt.subplots(figsize=(12, 6))
#fig.suptitle(f'Mein Titel', fontweight='bold')
patches, texts = ax1.pie(sizes, labels=names, labeldistance=1.15, wedgeprops={'linewidth' : 5, 'edgecolor' : 'white'}, colors=colors, pctdistance=0.7, startangle=90)
ax1.axis('equal')  # Ensures that pie is drawn as a circle

# Zusatzinfos in Textblock
uberschrift = f' Energie pro Jahr'
plt.figtext(0.78, 0.78, uberschrift, fontsize=14, weight='bold', horizontalalignment ="left", verticalalignment ="bottom")

text = f' Verluste Wirkungsgrad: \n {Verluste_Wirkungsgrad_ges/anzahl_jahre:.2f} kWh \n\n Verluste Tracking: \n {Verluste_Tracking_ges/anzahl_jahre:.2f} kWh \n\n Verluste Eigenverbrauch: \n {Verluste_Eigenverbrauch_ges/anzahl_jahre:.2f} kWh \n\n PV-Überschuss: \n {Verluste_PV_Überschuss_ges/anzahl_jahre:.2f} kWh \n\n Weitere Verluste: \n {Weitere_Verluste/anzahl_jahre:.2f} kWh \n\n Genutzte Energie: \n {Genutzte_Energie/anzahl_jahre:.2f} kWh'
plt.figtext(0.78, 0.76, text, fontsize=14, style='italic', horizontalalignment ="left", verticalalignment ="top")

# Donut erstellen (weisser Kreis im Zentrum)
centre_circle = plt.Circle((0, 0), 0.4, color='white')
plt.gcf().gca().add_artist(centre_circle)

# Plot zeigen und speichern
plt.tight_layout()
plt.show()
# speichern_unter = Pfad_Resultate
# fig.savefig(f'{Pfad_Resultate}/{Dateiname_Gesamtenergieplot}.jpg', bbox_inches='tight', dpi=500)
plt.clf()
plt.close()