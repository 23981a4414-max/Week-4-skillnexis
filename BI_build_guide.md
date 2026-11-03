# Power BI / Tableau build guide

Data source: `bi_ready.csv` (31 rows, one per workout day).
Columns: Date, Week, Weekday, WeekdayNum, IsWeekend, DurationMin, Pulse, MaxPulse, Calories, CalPerMin, Intensity, SessionType, AnyDataFix.

Reference numbers to check your build against (they must match):
Sessions 31 · Total kcal 9,469 · Avg kcal/min 5.55 · Week 1 → Week 4 kcal/min: 6.71 → 5.10 (−24.1%).

---------------------------------------------------------------------
## Power BI Desktop

1. Get Data → Text/CSV → `bi_ready.csv` → Transform Data. Confirm Date = Date; Week, WeekdayNum, DurationMin, Pulse, MaxPulse = Whole Number; Calories, CalPerMin, Intensity = Decimal. Close & Apply.
2. Select the `Weekday` column → Column tools → Sort by column → `WeekdayNum`.
3. New measures (Modeling → New measure):

```DAX
Sessions        = COUNTROWS(bi_ready)
Total Calories  = SUM(bi_ready[Calories])
Total Minutes   = SUM(bi_ready[DurationMin])
Avg Cal per Min = DIVIDE([Total Calories], [Total Minutes])
Avg Pulse       = AVERAGE(bi_ready[Pulse])
Week1 CPM       = CALCULATE([Avg Cal per Min], bi_ready[Week] = 1)
Week4 CPM       = CALCULATE([Avg Cal per Min], bi_ready[Week] = 4)
CPM Change W1-W4 = DIVIDE([Week4 CPM], [Week1 CPM]) - 1
```
Note: `Avg Cal per Min` here is total calories / total minutes (weighted), so it differs slightly from the Excel
average of per-session ratios (5.55). Use `AVERAGE(bi_ready[CalPerMin])` if you want an exact match.

4. Visuals (Report view):
   - 4 Cards: Sessions, Total Calories, Avg Cal per Min, CPM Change W1-W4 (format as %).
   - Line chart: X = Date, Y = Calories.
   - Scatter chart: X = Pulse, Y = Calories, Details = Date. Analytics pane → Trend line → On.
   - Clustered column: X = Week, Y = Avg Cal per Min. Add a Week slicer or filter out Week 5 (partial week).
   - Clustered column: X = Weekday, Y = Average of Calories.
   - Slicers: SessionType, AnyDataFix (select "Original" to test sensitivity to the data fixes).
5. Format: title "December 2020 Workout Dashboard"; theme with navy (#1F3A5F) accent. Save as `workout_dashboard.pbix`.

---------------------------------------------------------------------
## Tableau Desktop / Tableau Public

1. Connect → Text file → `bi_ready.csv`. Set Date to Date; Week to Dimension (right-click → Convert to Dimension).
2. Calculated fields:
   ```
   Cal per Min (weighted)  = SUM([Calories]) / SUM([DurationMin])
   ```
3. Sheets:
   - **Calories over time:** Columns = Date (Day, continuous); Rows = Calories (SUM). Line.
   - **Pulse vs Calories:** Columns = Pulse (AVG), Rows = Calories (AVG); drag Date to Detail (so every session is a point). Analytics tab → drag Trend Line onto the view.
   - **Weekly efficiency:** Columns = Week; Rows = AVG(CalPerMin). Bar. Add a Filter: Week ≠ 5 (partial) or annotate it.
   - **By weekday:** Columns = Weekday (sort manually Mon → Sun); Rows = AVG(Calories). Bar.
4. Dashboard: new Dashboard, size Automatic; drag the four sheets in a 2×2 layout; add filters for SessionType and AnyDataFix, set to "Apply to worksheets → All using this data source".
5. Save as `.twbx` (or publish to Tableau Public).

---------------------------------------------------------------------
## Sanity check
Filter AnyDataFix = "Original" (26 sessions). The week-1 → week-4 efficiency decline should still be clearly visible; if it is, the finding does not depend on my data fixes.
