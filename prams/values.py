import pandas as pd
import numpy as np

df = pd.read_excel("C:\\Users\\sahit\\Downloads\\DataForModel.xlsx")
print("First few rows:")
print(df.head())

# Example BP flag function (from earlier)
def bp_to_bpg_hbp8(bp_string):
    if pd.isna(bp_string) or str(bp_string).strip() in ['', '.B']:
        return np.nan
    try:
        sys, dia = bp_string.split('/')
        sys = int(sys)
        dia = int(dia)
        if sys >= 140 or dia >= 90:
            return 2  # YES → High BP
        else:
            return 1  # NO → Not High BP
    except:
        return np.nan

# Apply function to BP column
df['BPG_HBP8'] = df['BP'].apply(bp_to_bpg_hbp8)

print("\nUpdated dataframe:")
print(df[['BP', 'BPG_HBP8']].head())

# Save to new file back to Downloads
df.to_excel("C:\\Users\\sahit\\Downloads\\DataForModel_With_HBP8.xlsx", index=False)

print("\n✅ New file saved: DataForModel_With_HBP8.xlsx in Downloads.")