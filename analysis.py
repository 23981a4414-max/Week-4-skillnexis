import sqlite3, pandas as pd, numpy as np
pd.set_option("display.width", 200)

df = pd.read_csv("cleaned_data.csv", parse_dates=["date"])
df["week"] = ((df["date"] - df["date"].min()).dt.days // 7) + 1

# ---------- Pandas ----------
print("== describe ==")
print(df[["duration","pulse","maxpulse","calories","cal_per_min","intensity"]].describe().round(2))
print("\n== correlations ==")
print(df[["duration","pulse","maxpulse","calories","cal_per_min","intensity"]].corr().round(2))

slope, icpt = np.polyfit(df["duration"], df["calories"], 1)
r2 = np.corrcoef(df["duration"], df["calories"])[0,1]**2
print(f"\ncalories ~ duration: slope={slope:.2f} icpt={icpt:.1f} R2={r2:.2f}")
s2, i2 = np.polyfit(df["pulse"], df["calories"], 1)
print(f"calories ~ pulse: slope={s2:.2f} R2={np.corrcoef(df['pulse'],df['calories'])[0,1]**2:.2f}")

print("\n== by session_type ==")
print(df.groupby("session_type").agg(n=("calories","size"), cal=("calories","mean"), cpm=("cal_per_min","mean"), pulse=("pulse","mean")).round(2))
print("\n== by weekend ==")
print(df.groupby("is_weekend").agg(n=("calories","size"), cal=("calories","mean"), cpm=("cal_per_min","mean"), dur=("duration","mean")).round(2))
order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
print("\n== by weekday ==")
print(df.groupby("weekday").agg(n=("calories","size"), cal=("calories","mean"), cpm=("cal_per_min","mean")).reindex(order).round(2))
print("\n== by week ==")
print(df.groupby("week").agg(n=("calories","size"), dur=("duration","sum"), cal=("calories","sum"), cpm=("cal_per_min","mean"), pulse=("pulse","mean")).round(2))
print("\n== top/bottom efficiency ==")
print(df.nlargest(3,"cal_per_min")[["date","duration","pulse","maxpulse","calories","cal_per_min"]])
print(df.nsmallest(3,"cal_per_min")[["date","duration","pulse","maxpulse","calories","cal_per_min"]])
print("\nTotals:", df.duration.sum(), "min,", df.calories.sum().round(1), "kcal")
print("Imputed calories rows share:", df.calories_imputed.mean().round(3))

# ---------- SQL ----------
con = sqlite3.connect(":memory:")
d = df.copy(); d["date"] = d["date"].dt.strftime("%Y-%m-%d")
d.to_sql("workouts", con, index=False)
q = {
 "session_type": "SELECT session_type, COUNT(*) n, ROUND(AVG(calories),1) avg_cal, ROUND(AVG(cal_per_min),2) avg_cpm FROM workouts GROUP BY session_type ORDER BY avg_cal",
 "weekend": "SELECT is_weekend, COUNT(*) n, ROUND(AVG(calories),1) avg_cal, ROUND(AVG(cal_per_min),2) avg_cpm FROM workouts GROUP BY is_weekend",
 "weekly": "SELECT week, COUNT(*) n, SUM(duration) mins, ROUND(SUM(calories),1) kcal FROM workouts GROUP BY week",
 "above_avg_eff": "SELECT COUNT(*) FROM workouts WHERE cal_per_min > (SELECT AVG(cal_per_min) FROM workouts)",
}
print("\n===== SQL =====")
for k, sql in q.items():
    print("--", k); print(pd.read_sql(sql, con).to_string(index=False))
