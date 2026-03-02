# TIDAL ANALYSIS GOOGLE COLAB → GITHUB ACTIONS VERSION
import requests
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # FIX: Non-interactive backend
import matplotlib.pyplot as plt
import pytz
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

print("🚀 Tidal Analysis SR01 SUNGSANG mulai...")

# Download ThingSpeak
print("📥 Download data...")
url = "https://api.thingspeak.com/channels/3097834/feeds.json?results=8000"
try:
    r = requests.get(url, timeout=30)
    data = r.json()
    feeds = data['feeds']
    print(f"Got {len([f for f in feeds if f['field2']])} valid entries")
except:
    print("❌ ThingSpeak error")
    exit(1)

# Process data
df_list = []
jakarta = pytz.timezone('Asia/Jakarta')
for f in feeds:
    if f['field2']:
        dt = pd.to_datetime(f['created_at']).tz_localize('UTC').tz_convert(jakarta)
        df_list.append({'datetime':dt, 'entry_id':int(f['entry_id']), 'field2':float(f['field2'])})

df = pd.DataFrame(df_list)
tmp = df[df.entry_id>=1859][['datetime','entry_id','field2']].reset_index(drop=True)
n = len(tmp)

# Time sequence
start_time = pd.Timestamp("2026-03-01 01:46:02", tz='Asia/Jakarta')
datetime_seq = pd.date_range(start=start_time, freq='10T', periods=n)

# Main dataframe
extract_data = tmp.copy()
extract_data['datetime'] = datetime_seq
extract_data['field2_neg'] = extract_data['field2'] * -1
extract_data.to_csv("field2_tidal_entry1859_2026.csv", index=False)

# Deviations
mean_f2 = extract_data['field2'].mean()
extract_data['field2_deviasi'] = extract_data['field2'] - mean_f2
mean_f2n = extract_data['field2_neg'].mean()
extract_data['field2_neg_deviasi'] = extract_data['field2_neg'] - mean_f2n
extract_data.to_csv("field2_tidal_entry1859_deviasi_2026.csv", index=False)

print(f"✅ {n} points saved. Range: {extract_data.datetime.min()} to {extract_data.datetime.max()}")

# 4 PLOTS
def save_plot(x, y, title, fname, color='red', meanline=0):
    plt.figure(figsize=(12,7))
    plt.plot(x, y, color=color, linewidth=2)
    plt.axhline(meanline, color='blue', linewidth=3, linestyle='--')
    plt.title(title)
    plt.xlabel('Waktu (WIB)')
    plt.ylabel('Tinggi Air (m)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(fname, dpi=150, bbox_inches='tight')
    plt.close()

save_plot(extract_data.datetime, extract_data.field2, 'Jarak Alat', 'plot1_fielddata_dari_alat.png', meanline=mean_f2)
save_plot(extract_data.datetime, extract_data.field2_neg, 'Tinggi Air', 'plot2_field2_neg_entry1859.png', meanline=mean_f2n)
save_plot(extract_data.datetime, extract_data.field2_deviasi, 'Deviasi Alat', 'plot3_field2_deviasi_entry1859.png')
save_plot(extract_data.datetime, extract_data.field2_neg_deviasi, 'Deviasi Negatif', 'plot4_field2_neg_deviasi_entry1859.png')

print("🎉 All 2 CSV + 4 PNG generated!")
print("Files ready for GitHub Release!")


