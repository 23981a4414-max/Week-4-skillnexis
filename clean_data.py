import pandas as pd
import numpy as np

df = pd.read_csv("/mnt/user-data/uploads/data.csv")
print("Raw shape:", df.shape)

# --- 1. Standardize column names -------------------------------------------
df.columns = df.columns.str.lower()

# --- 2. Remove exact duplicates ---------------------------------------------
df = df.drop_duplicates().reset_index(drop=True)

# --- 3. Fix dates -----------------------------------------------------------
# Strip stray quotes, then parse both "2020/12/01" and "20201226" styles.
raw = df["date"].astype("string").str.strip("'\" ")
df["date"] = pd.to_datetime(raw.str.replace("/", "", regex=False),
                            format="%Y%m%d", errors="coerce")

# Rows are one-per-day, so a missing date can be interpolated from its neighbours.
df["date_imputed"] = df["date"].isna()
origin = df["date"].min()
day_num = (df["date"] - origin).dt.days.astype("float").interpolate().round()
df["date"] = origin + pd.to_timedelta(day_num, unit="D")

# --- 4. Flag and fix invalid values -----------------------------------------
# Duration 450 is almost certainly a typo for 45 (calories match a 45-min session).
df["duration_fixed"] = df["duration"] > 300
df.loc[df["duration_fixed"], "duration"] = df.loc[df["duration_fixed"], "duration"] // 10

# Average pulse cannot exceed max pulse -> the two values were likely swapped.
swap = df["pulse"] > df["maxpulse"]
df["pulse_swapped"] = swap
df.loc[swap, ["pulse", "maxpulse"]] = df.loc[swap, ["maxpulse", "pulse"]].values

# --- 5. Missing calories: median of sessions with the same duration ---------
df["calories_imputed"] = df["calories"].isna()
df["calories"] = df["calories"].fillna(
    df.groupby("duration")["calories"].transform("median")
)

# --- 6. Filter ---------------------------------------------------------------
df = df[(df["duration"] > 0) & (df["calories"] > 0)]

# --- 7. New columns ---------------------------------------------------------
df["cal_per_min"] = (df["calories"] / df["duration"]).round(2)
df["intensity"] = (df["pulse"] / df["maxpulse"]).round(3)
df["weekday"] = df["date"].dt.day_name()
df["is_weekend"] = df["date"].dt.dayofweek >= 5
df["session_type"] = pd.cut(df["duration"], bins=[0, 30, 45, np.inf],
                            labels=["Short", "Medium", "Long"])

df = df.reset_index(drop=True)
df.to_csv("/mnt/user-data/outputs/cleaned_data.csv", index=False)

print("Clean shape:", df.shape)
print(df.isna().sum().sum(), "missing values remain")
print(df.head(10).to_string())
