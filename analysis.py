import pandas as pd

data = pd.read_csv("datapack/ball_by_ball.csv")

print("Dataset successfully loaded!")
print("Rows and Columns:", data.shape)

print("\nColumn Names:")
print(data.columns.tolist())

print("\nFirst 5 Rows:")
print(data.head())
print("\n--- DATA QUALITY CHECK ---")

print("\nMissing Values:")
print(data.isnull().sum())

print("\nData Types:")
print(data.dtypes)

print("\nExtras Types:")
print(data["extras_type"].value_counts(dropna=False))

print("\nDismissal Types:")
print(data["dismissal_type"].value_counts(dropna=False))

print("\nRuns Summary:")
print(data["runs"].describe())
print("\n--- RUNS AND EXTRAS ANALYSIS ---")

print("\nRuns Distribution:")
print(data["runs"].value_counts().sort_index())

print("\nExtras Runs Distribution:")
print(data["extras1_runs"].value_counts().sort_index())

print("\nSecond Extras Distribution:")
print(data["extras_2_runs"].value_counts().sort_index())

print("\nRuns with Extras (Sample):")
print(
    data[data["extras_type"].notna()][
        ["runs", "extras_type", "extras1_runs", "extras_2_runs"]
    ].head(15).to_string(index=False)
)

print("\nWicket Distribution:")
print(data["is_wicket"].value_counts())
print("\n--- INNINGS SUMMARY ---")

innings_summary = data.groupby(
    ["match_id", "innings"]
).agg(
    total_deliveries=("innings_ball_num", "count"),
    unique_ball_numbers=("innings_ball_num", "nunique"),
    max_ball_number=("innings_ball_num", "max"),
    batter_runs=("runs", "sum"),
    extras1=("extras1_runs", "sum"),
    extras2=("extras_2_runs", "sum"),
    wickets=("is_wicket", "sum"),
    overs=("overid", "nunique")
).reset_index()

print(innings_summary.head(15).to_string(index=False))
print("\n--- MATCHES DATASET ---")

matches = pd.read_csv("datapack/matches.csv")

print("Shape:", matches.shape)

print("\nColumns:")
print(matches.columns.tolist())

print("\nFirst 5 Matches:")
print(matches.head().to_string(index=False))
print("\n--- COMPETITIONS DATASET ---")

competitions = pd.read_csv("datapack/competitions.csv")

print("Shape:", competitions.shape)

print("\nColumns:")
print(competitions.columns.tolist())

print("\nAll Competitions:")
print(competitions.to_string(index=False))
print("\n--- IPL SEASON ANALYSIS ---")

ipl = competitions[
    competitions["comp_name"].str.contains("IPL", case=False, na=False)
].sort_values("season")

print(ipl[["comp_id", "comp_name", "season"]].to_string(index=False))

ipl_matches = matches[matches["comp_id"].isin(ipl["comp_id"])]

print("\nIPL Matches by Season:")
print(
    ipl_matches.groupby("comp_id").agg(
        total_matches=("match_id", "nunique")
    ).reset_index().merge(
        ipl[["comp_id", "comp_name", "season"]],
        on="comp_id"
    )[["season", "comp_name", "total_matches"]].to_string(index=False)
)

print("\nTotal IPL matches:", ipl_matches["match_id"].nunique())
print("\n--- IPL BALL-BY-BALL DATA ---")

ipl_data = data[data["match_id"].isin(ipl_matches["match_id"])].copy()

print("IPL Deliveries:", len(ipl_data))
print("IPL Matches:", ipl_data["match_id"].nunique())

print("\nUnique Batters:", ipl_data["striker_id"].nunique())
print("Unique Bowlers:", ipl_data["bowler_id"].nunique())

print("\nTop 10 Batters by Deliveries Faced:")
print(
    ipl_data["striker_name"]
    .value_counts()
    .head(10)
    .to_string()
)

print("\nTop 10 Bowlers by Deliveries Bowled:")
print(
    ipl_data["bowler_name"]
    .value_counts()
    .head(10)
    .to_string()
)
print("\n--- SUPPORTING DATASETS ---")

teams = pd.read_csv("datapack/teams.csv")
playing_eleven = pd.read_csv("datapack/playing_eleven.csv")
player_mapping = pd.read_csv("datapack/competition_team_player_mapping.csv")

for name, df in [
    ("TEAMS", teams),
    ("PLAYING ELEVEN", playing_eleven),
    ("PLAYER MAPPING", player_mapping)
]:
    print(f"\n--- {name} ---")
    print("Shape:", df.shape)
    print("Columns:", df.columns.tolist())
    print(df.head(5).to_string(index=False))
    print("\n--- IPL PLAYER POOL & MATCH VALIDATION ---")

# IPL competition IDs: 2022 to 2026
ipl_ids = [1358, 1715, 2193, 2725, 3298]

# 1. IPL matches
ipl_matches = matches[matches["comp_id"].isin(ipl_ids)].copy()

# 2. IPL ball-by-ball records
ipl_data = data[data["match_id"].isin(ipl_matches["match_id"])].copy()

# 3. IPL player mapping
ipl_mapping = player_mapping[
    player_mapping["comp_id"].isin(ipl_ids)
].copy()

# 4. IPL playing eleven
ipl_playing = playing_eleven[
    playing_eleven["match_id"].isin(ipl_matches["match_id"])
].copy()

print("\n1. MATCH VALIDATION")
print("IPL matches in matches.csv:", ipl_matches["match_id"].nunique())
print("IPL matches in ball-by-ball:", ipl_data["match_id"].nunique())

missing_matches = set(ipl_matches["match_id"]) - set(ipl_data["match_id"])

print("Missing match IDs:", sorted(missing_matches))
print("Number of missing matches:", len(missing_matches))


# 5. Season-wise player count
print("\n2. SEASON-WISE PLAYER MAPPING")

season_players = (
    ipl_mapping.groupby(["comp_id", "comp_name"])
    .agg(
        total_players=("player_id", "nunique"),
        total_teams=("team_id", "nunique")
    )
    .reset_index()
)

print(season_players.to_string(index=False))


# 6. Overall IPL player pool
print("\n3. OVERALL IPL PLAYER POOL")

print("Unique mapped players:", ipl_mapping["player_id"].nunique())
print("Unique mapped teams:", ipl_mapping["team_id"].nunique())
print("Playing Eleven records:", len(ipl_playing))
print("Unique players in Playing Eleven:", ipl_playing["player_id"].nunique())

print("\nFirst 15 mapped players:")
print(
    ipl_mapping[["player_id", "player_name", "team_name"]]
    .drop_duplicates("player_id")
    .head(15)
    .to_string(index=False)
)


# 7. Check whether ball-by-ball players exist in mapping
print("\n4. PLAYER ID MATCH VALIDATION")

mapped_ids = set(ipl_mapping["player_id"].unique())
batter_ids = set(ipl_data["striker_id"].unique())
bowler_ids = set(ipl_data["bowler_id"].unique())

print("Batters in ball-by-ball:", len(batter_ids))
print("Batters not found in mapping:", len(batter_ids - mapped_ids))

print("Bowlers in ball-by-ball:", len(bowler_ids))
print("Bowlers not found in mapping:", len(bowler_ids - mapped_ids))

print("\n--- STEP 11 COMPLETED ---")
print("\n--- STEP 12: IPL SCORING VALIDATION ---")

# 1. Missing matches ki details
print("\n1. MISSING IPL MATCHES")

missing_info = ipl_matches[
    ipl_matches["match_id"].isin(missing_matches)
]

print(
    missing_info[
        ["match_id", "comp_id", "match_date", "home_team",
         "away_team", "result"]
    ].to_string(index=False)
)


# 2. IPL extras distribution
print("\n2. IPL EXTRAS DISTRIBUTION")

extras_summary = (
    ipl_data.groupby("extras_type", dropna=False)
    .agg(
        deliveries=("match_id", "size"),
        batter_runs=("runs", "sum"),
        extras1_runs=("extras1_runs", "sum"),
        extras2_runs=("extras_2_runs", "sum"),
        wickets=("is_wicket", "sum")
    )
    .reset_index()
)

print(extras_summary.to_string(index=False))


# 3. Dismissal types in IPL
print("\n3. IPL DISMISSAL TYPES")

dismissal_summary = (
    ipl_data[ipl_data["is_wicket"] == True]
    .groupby("dismissal_type", dropna=False)
    .size()
    .reset_index(name="count")
    .sort_values("count", ascending=False)
)

print(dismissal_summary.to_string(index=False))


# 4. Overstep deliveries sample
print("\n4. OVERSTEP DELIVERY SAMPLE")

overstep_sample = ipl_data[
    ipl_data["extras_type"] == "Overstep"
][
    ["match_id", "innings", "overid", "runs",
     "extras1_runs", "extras_2_runs", "is_wicket",
     "dismissal_type"]
]

print(overstep_sample.head(10).to_string(index=False))


# 5. Wide deliveries sample
print("\n5. WIDE DELIVERY SAMPLE")

wide_sample = ipl_data[
    ipl_data["extras_type"] == "wide"
][
    ["match_id", "innings", "overid", "runs",
     "extras1_runs", "extras_2_runs", "is_wicket",
     "dismissal_type"]
]

print(wide_sample.head(10).to_string(index=False))


# 6. Check total run calculation
print("\n6. TOTAL RUNS CHECK")

total_batter_runs = ipl_data["runs"].sum()
total_extras1 = ipl_data["extras1_runs"].sum()
total_extras2 = ipl_data["extras_2_runs"].sum()

print("Batter runs:", total_batter_runs)
print("Extras 1:", total_extras1)
print("Extras 2:", total_extras2)
print("Combined runs (initial check):",
      total_batter_runs + total_extras1 + total_extras2)

print("\n--- STEP 12 COMPLETED ---")
print("\n--- STEP 13: EXTRAS AND WICKET VERIFICATION ---")

# 1. Extras 2 kis delivery type par aaye?
print("\n1. EXTRAS 2 BY DELIVERY TYPE")

extras2_check = (
    ipl_data.groupby("extras_type", dropna=False)
    .agg(
        deliveries=("match_id", "size"),
        extras2_total=("extras_2_runs", "sum"),
        extras2_deliveries=("extras_2_runs",
                            lambda x: (x > 0).sum())
    )
    .reset_index()
)

print(extras2_check.to_string(index=False))


# 2. Overstep par wickets ka breakdown
print("\n2. WICKETS ON OVERSTEP DELIVERIES")

overstep_wickets = ipl_data[
    (ipl_data["extras_type"] == "Overstep") &
    (ipl_data["is_wicket"] == True)
]

print(
    overstep_wickets[
        ["match_id", "innings", "bowler_name",
         "striker_name", "dismissal_type"]
    ].to_string(index=False)
)


# 3. Wide par wickets ka breakdown
print("\n3. WICKETS ON WIDE DELIVERIES")

wide_wickets = ipl_data[
    (ipl_data["extras_type"] == "wide") &
    (ipl_data["is_wicket"] == True)
]

print(
    wide_wickets[
        ["match_id", "innings", "bowler_name",
         "striker_name", "dismissal_type"]
    ].to_string(index=False)
)


# 4. Check batter runs on Overstep deliveries
print("\n4. OVERSTEP RUNS BREAKDOWN")

print(
    ipl_data[ipl_data["extras_type"] == "Overstep"]
    .groupby("runs")
    .size()
    .reset_index(name="deliveries")
    .to_string(index=False)
)


# 5. Other extras details
print("\n5. OTHER EXTRAS SAMPLE")

other_sample = ipl_data[
    ipl_data["extras_type"].isin(["other", "Penalty"])
][
    ["runs", "extras_type", "extras1_runs",
     "extras_2_runs", "is_wicket", "dismissal_type"]
]

print(other_sample.head(15).to_string(index=False))

print("\n--- STEP 13 COMPLETED ---")

print("\n--- STEP 14: BATTING & BOWLING CALCULATION VALIDATION ---")

# IPL extras categories
print("\n1. EXTRAS CATEGORY SUMMARY")

print(
    ipl_data.groupby("extras_type", dropna=False)
    .agg(
        deliveries=("match_id", "count"),
        batter_runs=("runs", "sum"),
        extras_runs=("extras1_runs", "sum"),
        extra2_runs=("extras_2_runs", "sum")
    )
    .to_string()
)

# 2. Delivery classification
print("\n2. DELIVERY CLASSIFICATION")

ipl_data["is_wide"] = ipl_data["extras_type"].eq("wide")
ipl_data["is_no_ball"] = ipl_data["extras_type"].eq("Overstep")

ipl_data["is_legal_ball"] = (
    ~ipl_data["is_wide"] & ~ipl_data["is_no_ball"]
)

print("Total deliveries:", len(ipl_data))
print("Wide deliveries:", ipl_data["is_wide"].sum())
print("No-ball deliveries:", ipl_data["is_no_ball"].sum())
print("Legal deliveries:", ipl_data["is_legal_ball"].sum())

# 3. Batter balls faced
print("\n3. BATTER BALLS FACED")

ipl_data["is_batter_ball"] = ~ipl_data["is_wide"]

print("Batter balls faced:", ipl_data["is_batter_ball"].sum())

# 4. Bowler wicket classification
print("\n4. BOWLER WICKET VALIDATION")

non_bowler_dismissals = [
    "RunOut",
    "Retire Out",
    "Obstracting the field",
    "Obstructing the field"
]

ipl_data["bowler_wicket"] = (
    ipl_data["is_wicket"]
    & ~ipl_data["dismissal_type"].isin(non_bowler_dismissals)
)

print("Total recorded wickets:", ipl_data["is_wicket"].sum())
print("Potential bowler wickets:", ipl_data["bowler_wicket"].sum())

print("\nWickets excluded from bowler credit:")
print(
    ipl_data.loc[
        ipl_data["is_wicket"]
        & ipl_data["dismissal_type"].isin(non_bowler_dismissals),
        "dismissal_type"
    ].value_counts().to_string()
)

print("\n--- STEP 14 COMPLETED ---")

print("\n--- STEP 15: PLAYER PERFORMANCE SUMMARY ---")

# BATTER SUMMARY
batting_summary = (
    ipl_data.groupby(["striker_id", "striker_name"])
    .agg(
        runs=("runs", "sum"),
        balls_faced=("is_batter_ball", "sum"),
        fours=("is_four", "sum"),
        sixes=("is_six", "sum"),
        innings=("match_id", "nunique")
    )
    .reset_index()
)

batting_summary["strike_rate"] = (
    batting_summary["runs"] /
    batting_summary["balls_faced"] * 100
)

print("\n1. TOP 10 BATTERS BY RUNS")

print(
    batting_summary.sort_values(
        "runs", ascending=False
    ).head(10).to_string(index=False)
)


# BOWLER SUMMARY
bowling_summary = (
    ipl_data.groupby(["bowler_id", "bowler_name"])
    .agg(
        deliveries=("is_legal_ball", "sum"),
        wickets=("bowler_wicket", "sum"),
        total_extras=("extras1_runs", "sum"),
        total_runs=("runs", "sum"),
        innings=("match_id", "nunique")
    )
    .reset_index()
)

print("\n2. TOP 10 BOWLERS BY WICKETS")

print(
    bowling_summary.sort_values(
        "wickets", ascending=False
    ).head(10).to_string(index=False)
)

print("\n--- STEP 15 COMPLETED ---")

print("\n--- STEP 16A: MATCH CONTEXT ANALYSIS ---")

# Match details ko IPL ball-by-ball data ke saath join karo
ipl_matches = matches[
    matches["comp_id"].isin([1358, 1715, 2193, 2725, 3298])
].copy()

context_data = ipl_data.merge(
    ipl_matches[
        ["match_id", "match_date", "venue_id",
         "home_team", "away_team", "result",
         "revised_target"]
    ],
    on="match_id",
    how="left"
)

print("\n1. MATCH CONTEXT CHECK")

print("Total IPL deliveries:", len(context_data))
print("Missing match dates:", context_data["match_date"].isna().sum())
print("Missing venues:", context_data["venue_id"].isna().sum())

# Innings and over distribution
print("\n2. INNINGS DISTRIBUTION")

print(
    context_data["innings"]
    .value_counts()
    .sort_index()
    .to_string()
)

print("\n3. OVER DISTRIBUTION")

print(
    context_data.groupby("innings")["overid"]
    .agg(["min", "max", "nunique"])
    .to_string()
)

print("\n4. SEASON-WISE DELIVERY DISTRIBUTION")

print(
    context_data.groupby("match_date")
    .size()
    .describe()
    .to_string()
)

print("\n--- STEP 16A COMPLETED ---")

print("\n--- STEP 16B: MATCH PHASE ANALYSIS ---")

# Sort deliveries in match order
context_data = context_data.sort_values(
    ["match_id", "innings", "innings_ball_num"]
).copy()

# Classify match phases
def get_phase(over):
    if over <= 6:
        return "Powerplay"
    elif over <= 15:
        return "Middle"
    else:
        return "Death"

context_data["phase"] = context_data["overid"].apply(get_phase)

# Wickets lost BEFORE the current delivery
context_data["wickets_before"] = (
    context_data.groupby(["match_id", "innings"])["is_wicket"]
    .cumsum()
    - context_data["is_wicket"].astype(int)
)

# Wickets remaining before the current delivery
context_data["wickets_remaining"] = (
    10 - context_data["wickets_before"]
)

print("\n1. DELIVERIES BY PHASE")

print(context_data["phase"].value_counts().to_string())

print("\n2. WICKETS LOST BY PHASE")

print(
    context_data.groupby("phase")["wickets_before"]
    .mean()
    .round(2)
    .to_string()
)

print("\n3. DEATH OVERS WICKET SITUATIONS")

death_data = context_data[
    context_data["phase"] == "Death"
]

print(
    death_data["wickets_remaining"]
    .value_counts()
    .sort_index()
    .to_string()
)

print("\n4. PRESSURE CANDIDATE DELIVERIES")

pressure_candidates = context_data[
    (context_data["phase"] == "Death")
    | (context_data["wickets_remaining"] <= 5)
]

print("Total candidate deliveries:", len(pressure_candidates))
print("Death-over deliveries:", len(death_data))
print(
    "Deliveries with 5 or fewer wickets remaining:",
    (context_data["wickets_remaining"] <= 5).sum()
)

print("\n--- STEP 16B COMPLETED ---")

print("\n--- STEP 16C: CHASE PRESSURE ANALYSIS ---")

# Innings-level score
innings_scores = (
    context_data.groupby(["match_id", "innings"])
    .agg(
        innings_runs=("runs", "sum"),
        extras1=("extras1_runs", "sum"),
        extras2=("extras_2_runs", "sum"),
        deliveries=("match_id", "size")
    )
    .reset_index()
)

# Total innings score
innings_scores["total_score"] = (
    innings_scores["innings_runs"]
    + innings_scores["extras1"]
    + innings_scores["extras2"]
)

# First innings score as target reference
first_innings = innings_scores[
    innings_scores["innings"] == 1
][["match_id", "total_score"]].rename(
    columns={"total_score": "first_innings_score"}
)

# Attach first innings score to second innings
second_innings = context_data[
    context_data["innings"] == 2
].merge(
    first_innings,
    on="match_id",
    how="left"
)

print("\n1. SECOND INNINGS MATCH COUNT")
print("Matches:", second_innings["match_id"].nunique())

print("\n2. FIRST INNINGS SCORE CHECK")
print(
    first_innings["first_innings_score"]
    .describe()
    .round(2)
    .to_string()
)

print("\n3. SECOND INNINGS SAMPLE")

print(
    second_innings[
        ["match_id", "innings_ball_num",
         "runs", "first_innings_score"]
    ].head(15).to_string(index=False)
)

print("\n4. MISSING FIRST INNINGS SCORES")
print(
    second_innings["first_innings_score"].isna().sum()
)

print("\n--- STEP 16C COMPLETED ---")

print("\n--- STEP 16D: TARGET VERIFICATION ---")

# Match-wise first innings score
first_scores = (
    context_data[context_data["innings"] == 1]
    .groupby("match_id")
    .agg(
        first_score=("runs", "sum"),
        extras1=("extras1_runs", "sum"),
        extras2=("extras_2_runs", "sum")
    )
    .reset_index()
)

first_scores["calculated_target"] = (
    first_scores["first_score"]
    + first_scores["extras1"]
    + first_scores["extras2"]
    + 1
)

# Match metadata
target_check = first_scores.merge(
    ipl_matches[
        ["match_id", "revised_target", "result",
         "match_date", "home_team", "away_team"]
    ],
    on="match_id",
    how="left"
)

print("\n1. TARGET DATA SUMMARY")

print("Total matches:", len(target_check))
print("Revised targets available:",
      target_check["revised_target"].notna().sum())

print("\n2. SAMPLE TARGET COMPARISON")

print(
    target_check[
        ["match_id", "match_date", "home_team",
         "away_team", "first_score", "extras1",
         "extras2", "calculated_target",
         "revised_target", "result"]
    ].head(15).to_string(index=False)
)

print("\n3. REVISED TARGET MATCHES")

print(
    target_check[
        target_check["revised_target"].notna()
    ][
        ["match_id", "calculated_target",
         "revised_target", "result"]
    ].to_string(index=False)
)

print("\n--- STEP 16D COMPLETED ---")

print("\n--- STEP 16E: CUMULATIVE SCORE ANALYSIS ---")

# Sort second innings deliveries
chase_data = second_innings.sort_values(
    ["match_id", "innings_ball_num"]
).copy()

# Runs scored on each delivery, including extras
chase_data["delivery_runs"] = (
    chase_data["runs"]
    + chase_data["extras1_runs"]
    + chase_data["extras_2_runs"]
)

# Cumulative score after each delivery
chase_data["current_score"] = (
    chase_data.groupby("match_id")["delivery_runs"]
    .cumsum()
)

print("\n1. SCORE PROGRESSION SAMPLE")

print(
    chase_data[
        ["match_id", "innings_ball_num",
         "delivery_runs", "current_score",
         "first_innings_score"]
    ].head(20).to_string(index=False)
)

print("\n2. FINAL CHASE SCORE CHECK")

final_scores = (
    chase_data.groupby("match_id")
    .agg(
        calculated_final_score=("current_score", "max"),
        first_innings_score=("first_innings_score", "first")
    )
    .reset_index()
)

print(final_scores.head(10).to_string(index=False))

print("\n3. CHASE MATCH COUNT")
print("Matches:", final_scores["match_id"].nunique())

print("\n--- STEP 16E COMPLETED ---")

print("\n--- STEP 16F: CHASE PRESSURE ANALYSIS ---")

# Remaining runs needed to win
chase_data["runs_needed"] = (
    chase_data["first_innings_score"] + 1
    - chase_data["current_score"]
)

# Legal balls remaining (120-ball T20)
chase_data["legal_ball_number"] = (
    chase_data.groupby("match_id")["is_legal_ball"]
    .cumsum()
)

chase_data["balls_remaining"] = (
    120 - chase_data["legal_ball_number"]
)

# Required run rate
chase_data["required_run_rate"] = (
    chase_data["runs_needed"] /
    chase_data["balls_remaining"].replace(0, float("nan"))
) * 6

# Pressure categories
def pressure_level(row):
    if row["runs_needed"] <= 0:
        return "Target Achieved"
    elif row["balls_remaining"] <= 30 and row["runs_needed"] >= 40:
        return "Very High"
    elif row["balls_remaining"] <= 30 and row["runs_needed"] >= 25:
        return "High"
    elif row["required_run_rate"] >= 12:
        return "High"
    elif row["required_run_rate"] >= 9:
        return "Medium"
    else:
        return "Low"

chase_data["pressure_level"] = chase_data.apply(
    pressure_level, axis=1
)

print("\n1. PRESSURE LEVEL DISTRIBUTION")
print(chase_data["pressure_level"].value_counts())

print("\n2. REQUIRED RUN RATE SUMMARY")
print(chase_data["required_run_rate"].describe())

print("\n3. HIGH PRESSURE DELIVERY SAMPLE")
print(
    chase_data[
        chase_data["pressure_level"].isin(["High", "Very High"])
    ][
        ["match_id", "innings_ball_num", "current_score",
         "runs_needed", "balls_remaining",
         "required_run_rate", "pressure_level"]
    ].head(15).to_string(index=False)
)

print("\n--- STEP 16F COMPLETED ---")

print("\n--- STEP 16G: HIGH PRESSURE BATTER ANALYSIS ---")

# Select high-pressure deliveries
high_pressure = chase_data[
    chase_data["pressure_level"].isin(["High", "Very High"])
].copy()

# Batter-wise performance
pressure_batting = high_pressure.groupby(
    ["striker_id", "striker_name"]
).agg(
    pressure_runs=("runs", "sum"),
    pressure_balls=("is_batter_ball", "sum"),
    pressure_fours=("is_four", "sum"),
    pressure_sixes=("is_six", "sum"),
    matches=("match_id", "nunique")
).reset_index()

# Strike rate under pressure
pressure_batting["pressure_strike_rate"] = (
    pressure_batting["pressure_runs"]
    / pressure_batting["pressure_balls"].replace(0, float("nan"))
) * 100

# Minimum sample size: 20 balls
qualified_batters = pressure_batting[
    pressure_batting["pressure_balls"] >= 20
].copy()

qualified_batters = qualified_batters.sort_values(
    "pressure_strike_rate", ascending=False
)

print("\n1. QUALIFIED BATTERS:", len(qualified_batters))

print("\n2. TOP 15 BATTERS UNDER PRESSURE")
print(
    qualified_batters[
        ["striker_name", "pressure_runs", "pressure_balls",
         "pressure_strike_rate", "pressure_fours",
         "pressure_sixes", "matches"]
    ].head(15).round(2).to_string(index=False)
)

print("\n--- STEP 16G COMPLETED ---")

print("\n--- STEP 16H: PRESSURE BATTING SCORE ---")

# Use qualified batters from Step 16G
scored_batters = qualified_batters.copy()

# Calculate average pressure strike rate
average_sr = scored_batters["pressure_strike_rate"].mean()

# Strike-rate contribution
scored_batters["sr_score"] = (
    scored_batters["pressure_strike_rate"] / average_sr
) * 100

# Run contribution
average_runs = scored_batters["pressure_runs"].mean()

scored_batters["run_score"] = (
    scored_batters["pressure_runs"] / average_runs
) * 100

# Combined preliminary score
scored_batters["pressure_score"] = (
    0.60 * scored_batters["sr_score"]
    + 0.40 * scored_batters["run_score"]
)

# Sort highest score first
scored_batters = scored_batters.sort_values(
    "pressure_score", ascending=False
)

print("\nAVERAGE PRESSURE STRIKE RATE:", round(average_sr, 2))

print("\nTOP 15 BATTERS BY PRELIMINARY PRESSURE SCORE")

print(
    scored_batters[
        ["striker_name", "pressure_runs",
         "pressure_balls", "pressure_strike_rate",
         "matches", "pressure_score"]
    ].head(15).round(2).to_string(index=False)
)

print("\n--- STEP 16H COMPLETED ---")

print("\n--- STEP 16I: CORRECTED PRESSURE ANALYSIS ---")

# 1. Calculate first innings total score
first_scores = (
    context_data[context_data["innings"] == 1]
    .groupby("match_id")
    .agg(
        first_score=("runs", "sum"),
        extras1=("extras1_runs", "sum"),
        extras2=("extras_2_runs", "sum")
    )
    .reset_index()
)

first_scores["target"] = (
    first_scores["first_score"]
    + first_scores["extras1"]
    + first_scores["extras2"]
    + 1
)

# 2. Select second innings deliveries
corrected_chase = context_data[
    context_data["innings"] == 2
].copy()

# 3. Add target to second innings data
corrected_chase = corrected_chase.merge(
    first_scores[["match_id", "target"]],
    on="match_id",
    how="left"
)

# 4. Prepare match rules
match_rules = ipl_matches[
    [
        "match_id",
        "first_inn_revised_overs",
        "second_inn_revised_overs",
        "revised_target"
    ]
].copy()

# Remove old rule columns if already present
columns_to_remove = [
    "first_inn_revised_overs",
    "second_inn_revised_overs",
    "revised_target"
]

corrected_chase = corrected_chase.drop(
    columns=columns_to_remove,
    errors="ignore"
)

# Merge match rules
corrected_chase = corrected_chase.merge(
    match_rules,
    on="match_id",
    how="left"
)

# 5. Keep regular 20-over matches only
corrected_chase = corrected_chase[
    corrected_chase["first_inn_revised_overs"].isna()
    & corrected_chase["second_inn_revised_overs"].isna()
    & corrected_chase["revised_target"].isna()
].copy()

# 6. Sort deliveries
corrected_chase = corrected_chase.sort_values(
    ["match_id", "innings_ball_num"]
).copy()

# 7. Calculate total runs on each delivery
corrected_chase["delivery_runs"] = (
    corrected_chase["runs"]
    + corrected_chase["extras1_runs"]
    + corrected_chase["extras_2_runs"]
)

# Score BEFORE current delivery
corrected_chase["score_before"] = (
    corrected_chase.groupby("match_id")["delivery_runs"].cumsum()
    - corrected_chase["delivery_runs"]
)

# Legal balls BEFORE current delivery
corrected_chase["legal_before"] = (
    corrected_chase.groupby("match_id")["is_legal_ball"].cumsum()
    - corrected_chase["is_legal_ball"].astype(int)
)

corrected_chase["balls_remaining"] = (
    120 - corrected_chase["legal_before"]
)

# Wickets BEFORE current delivery
corrected_chase["wickets_before"] = (
    corrected_chase.groupby("match_id")["is_wicket"].cumsum()
    - corrected_chase["is_wicket"].astype(int)
)

corrected_chase["wickets_remaining"] = (
    10 - corrected_chase["wickets_before"]
)

# 8. Calculate runs needed
corrected_chase["runs_needed"] = (
    corrected_chase["target"]
    - corrected_chase["score_before"]
)

# 9. Calculate required run rate
corrected_chase["required_run_rate"] = (
    corrected_chase["runs_needed"]
    / corrected_chase["balls_remaining"].replace(0, float("nan"))
) * 6

# 10. Classify pressure
def classify_pressure(row):

    rrr = row["required_run_rate"]
    balls = row["balls_remaining"]
    runs = row["runs_needed"]
    wickets = row["wickets_remaining"]

    if runs <= 0:
        return "Target Achieved"

    elif balls <= 18 and runs >= 24:
        return "Very High"

    elif rrr >= 14:
        return "Very High"

    elif balls <= 30 and runs >= 30:
        return "High"

    elif rrr >= 10:
        return "High"

    elif wickets <= 4 and rrr >= 8:
        return "High"

    elif rrr >= 8:
        return "Medium"

    else:
        return "Low"


corrected_chase["pressure_level"] = corrected_chase.apply(
    classify_pressure,
    axis=1
)

# 11. Remove deliveries after target is achieved
corrected_chase = corrected_chase[
    (corrected_chase["runs_needed"] > 0)
    & (corrected_chase["balls_remaining"] > 0)
].copy()

# 12. Display results
print("\n1. REGULAR CHASE MATCHES")
print("Matches:", corrected_chase["match_id"].nunique())

print("\n2. PRESSURE DISTRIBUTION")
print(corrected_chase["pressure_level"].value_counts())

print("\n3. REQUIRED RUN RATE SUMMARY")
print(corrected_chase["required_run_rate"].describe().round(2))

print("\n4. HIGH PRESSURE SAMPLE")

print(
    corrected_chase[
        corrected_chase["pressure_level"].isin(
            ["High", "Very High"]
        )
    ][
        [
            "match_id",
            "striker_name",
            "score_before",
            "runs_needed",
            "balls_remaining",
            "wickets_remaining",
            "required_run_rate",
            "pressure_level"
        ]
    ].head(15).round(2).to_string(index=False)
)

print("\n--- STEP 16I COMPLETED ---")

print("\n--- STEP 16J: BATTER PERFORMANCE UNDER PRESSURE ---")

# 1. Select High and Very High pressure deliveries
high_pressure = corrected_chase[
    corrected_chase["pressure_level"].isin(
        ["High", "Very High"]
    )
].copy()

# 2. Calculate batter-wise performance
pressure_batters = (
    high_pressure.groupby(
        ["striker_id", "striker_name"]
    )
    .agg(
        runs=("runs", "sum"),
        balls=("is_batter_ball", "sum"),
        dismissals=("is_wicket", "sum"),
        matches=("match_id", "nunique")
    )
    .reset_index()
)

# 3. Calculate strike rate
pressure_batters["strike_rate"] = (
    pressure_batters["runs"]
    / pressure_batters["balls"].replace(0, float("nan"))
) * 100

# 4. Minimum sample-size filter
qualified_batters = pressure_batters[
    (pressure_batters["balls"] >= 30)
    & (pressure_batters["matches"] >= 3)
].copy()

# 5. Sort by pressure runs
qualified_batters = qualified_batters.sort_values(
    ["runs", "strike_rate"],
    ascending=False
)

# 6. Display results
print("\nTotal high-pressure deliveries:", len(high_pressure))

print(
    "Unique batters:",
    pressure_batters["striker_id"].nunique()
)

print(
    "Qualified batters:",
    len(qualified_batters)
)

print("\nTOP 20 BATTERS BY PRESSURE RUNS")

print(
    qualified_batters[
        [
            "striker_name",
            "runs",
            "balls",
            "strike_rate",
            "dismissals",
            "matches"
        ]
    ].head(20).round(2).to_string(index=False)
)

print("\n--- STEP 16J COMPLETED ---")

print("\n--- STEP 16K: BOWLER PERFORMANCE UNDER PRESSURE ---")

# 1. Select High and Very High pressure deliveries
high_pressure_bowling = corrected_chase[
    corrected_chase["pressure_level"].isin(
        ["High", "Very High"]
    )
].copy()

# 2. Calculate runs conceded by bowler
# Byes and legbyes are not charged to the bowler.
high_pressure_bowling["bowler_runs"] = (
    high_pressure_bowling["runs"]
    + high_pressure_bowling["extras1_runs"].where(
        ~high_pressure_bowling["extras_type"].isin(
            ["byes", "legbyes"]
        ),
        0
    )
    + high_pressure_bowling["extras_2_runs"]
)

# 3. Calculate bowler-wise performance
pressure_bowlers = (
    high_pressure_bowling.groupby(
        ["bowler_id", "bowler_name"]
    )
    .agg(
        runs_conceded=("bowler_runs", "sum"),
        legal_balls=("is_legal_ball", "sum"),
        wickets=("bowler_wicket", "sum"),
        matches=("match_id", "nunique")
    )
    .reset_index()
)

# 4. Calculate economy rate
pressure_bowlers["economy"] = (
    pressure_bowlers["runs_conceded"]
    / pressure_bowlers["legal_balls"].replace(0, float("nan"))
) * 6

# 5. Minimum sample-size filter
qualified_bowlers = pressure_bowlers[
    (pressure_bowlers["legal_balls"] >= 30)
    & (pressure_bowlers["matches"] >= 3)
].copy()

# 6. Sort by wickets, then economy
qualified_bowlers = qualified_bowlers.sort_values(
    ["wickets", "economy"],
    ascending=[False, True]
)

# 7. Display results
print("\nTotal pressure bowling deliveries:",
      len(high_pressure_bowling))

print("\nUnique bowlers:",
      pressure_bowlers["bowler_id"].nunique())

print("\nQualified bowlers:",
      len(qualified_bowlers))

print("\nTOP 20 BOWLERS UNDER PRESSURE")

print(
    qualified_bowlers[
        [
            "bowler_name",
            "runs_conceded",
            "legal_balls",
            "wickets",
            "economy",
            "matches"
        ]
    ].head(20).round(2).to_string(index=False)
)

print("\n--- STEP 16K COMPLETED ---")

print("\n--- STEP 16L: PRESSURE DATA VALIDATION ---")

# 1. Check missing values
print("\n1. MISSING VALUES")

print(
    corrected_chase[
        [
            "runs_needed",
            "balls_remaining",
            "required_run_rate",
            "pressure_level"
        ]
    ].isna().sum()
)

# 2. Check invalid values
print("\n2. INVALID VALUES")

print(
    "Negative runs needed:",
    (corrected_chase["runs_needed"] < 0).sum()
)

print(
    "Negative balls remaining:",
    (corrected_chase["balls_remaining"] < 0).sum()
)

print(
    "Zero balls remaining:",
    (corrected_chase["balls_remaining"] == 0).sum()
)

print(
    "Negative required run rate:",
    (corrected_chase["required_run_rate"] < 0).sum()
)

# 3. Check pressure category distribution
print("\n3. PRESSURE CATEGORY DISTRIBUTION")

print(
    corrected_chase["pressure_level"].value_counts()
)

# 4. Validate batter data
print("\n4. BATTER DATA VALIDATION")

print(
    "Qualified batters:",
    len(qualified_batters)
)

print(
    "Batters with zero balls:",
    (qualified_batters["balls"] == 0).sum()
)

print(
    "Batters with negative runs:",
    (qualified_batters["runs"] < 0).sum()
)

# 5. Validate bowler data
print("\n5. BOWLER DATA VALIDATION")

print(
    "Qualified bowlers:",
    len(qualified_bowlers)
)

print(
    "Bowlers with zero legal balls:",
    (qualified_bowlers["legal_balls"] == 0).sum()
)

print(
    "Bowlers with negative runs conceded:",
    (qualified_bowlers["runs_conceded"] < 0).sum()
)

# 6. Show unusual bowling economy values
print("\n6. TOP 10 HIGHEST PRESSURE ECONOMIES")

print(
    qualified_bowlers.sort_values(
        "economy",
        ascending=False
    )[
        [
            "bowler_name",
            "runs_conceded",
            "legal_balls",
            "wickets",
            "economy"
        ]
    ].head(10).round(2).to_string(index=False)
)

print("\n--- STEP 16L COMPLETED ---")

print("\n--- STEP 16M: BOWLING EXTRAS VERIFICATION ---")

print("\n1. PRESSURE DELIVERIES BY EXTRAS TYPE")

print(
    high_pressure_bowling.groupby("extras_type", dropna=False)
    .agg(
        deliveries=("match_id", "count"),
        batter_runs=("runs", "sum"),
        extras1=("extras1_runs", "sum"),
        extras2=("extras_2_runs", "sum")
    )
    .to_string()
)

print("\n2. OTHER EXTRAS EXAMPLES")

print(
    high_pressure_bowling[
        high_pressure_bowling["extras_type"] == "other"
    ][
        [
            "match_id",
            "bowler_name",
            "runs",
            "extras1_runs",
            "extras_2_runs",
            "is_wicket",
            "dismissal_type"
        ]
    ].head(20).to_string(index=False)
)

print("\n--- STEP 16M COMPLETED ---")

print("\n--- STEP 16N: EXTRA 2 RUNS INVESTIGATION ---")

# 1. Find all deliveries with extras2
extra2_data = ipl_data[
    ipl_data["extras_2_runs"] > 0
].copy()

print("\n1. TOTAL DELIVERIES WITH EXTRAS2")
print("Count:", len(extra2_data))
print("Total extras2 runs:", extra2_data["extras_2_runs"].sum())

# 2. Group by extras type
print("\n2. EXTRAS2 DISTRIBUTION")

print(
    extra2_data.groupby("extras_type", dropna=False)
    .agg(
        deliveries=("match_id", "count"),
        extras2_runs=("extras_2_runs", "sum"),
        batter_runs=("runs", "sum"),
        extras1_runs=("extras1_runs", "sum")
    )
    .to_string()
)

# 3. Show every extras2 delivery
print("\n3. ALL EXTRAS2 DELIVERY EXAMPLES")

print(
    extra2_data[
        [
            "match_id",
            "innings",
            "overid",
            "bowler_name",
            "striker_name",
            "runs",
            "extras_type",
            "extras1_runs",
            "extras_2_runs",
            "is_wicket",
            "dismissal_type"
        ]
    ].to_string(index=False)
)

print("\n--- STEP 16N COMPLETED ---")

# --- STEP 16O: BOWLING RUNS VERIFICATION ---

# Runs that are normally charged to the bowler:
# Batter runs + wides + no-ball penalty
ipl_data["bowler_runs_base"] = (
    ipl_data["runs"] +
    ipl_data["extras1_runs"].where(
        ipl_data["extras_type"].isin(["wide", "Overstep"]), 0
    )
)

# Compare the effect of including extras2
ipl_data["bowler_runs_with_extras2"] = (
    ipl_data["bowler_runs_base"] +
    ipl_data["extras_2_runs"]
)

# Investigate "other" extras separately
other_extras = ipl_data[
    ipl_data["extras_type"].eq("other")
]

print("\n--- STEP 16O: BOWLING RUNS VERIFICATION ---")

print("\n1. BOWLER RUNS BASE TOTAL:")
print(ipl_data["bowler_runs_base"].sum())

print("\n2. BOWLER RUNS INCLUDING EXTRAS2:")
print(ipl_data["bowler_runs_with_extras2"].sum())

print("\n3. OTHER EXTRAS SUMMARY:")
print(
    other_extras[
        ["runs", "extras1_runs", "extras_2_runs"]
    ].sum()
)

print("\n4. OTHER EXTRAS SAMPLE:")
print(
    other_extras[
        ["match_id", "bowler_name", "runs",
         "extras1_runs", "extras_2_runs",
         "dismissal_type"]
    ].head(15).to_string(index=False)
)

print("\n--- STEP 16O COMPLETED ---")

# --- STEP 16P: TOTAL RUNS RECONCILIATION ---

print("\n--- STEP 16P: TOTAL RUNS RECONCILIATION ---")

ipl_data["delivery_total_runs"] = (
    ipl_data["runs"] +
    ipl_data["extras1_runs"] +
    ipl_data["extras_2_runs"]
)

print("\n1. RUNS BY EXTRAS CATEGORY:")

extras_check = (
    ipl_data.groupby("extras_type", dropna=False)
    .agg(
        deliveries=("match_id", "count"),
        batter_runs=("runs", "sum"),
        extras1=("extras1_runs", "sum"),
        extras2=("extras_2_runs", "sum"),
        total_runs=("delivery_total_runs", "sum")
    )
    .reset_index()
)

print(extras_check.to_string(index=False))

print("\n2. TOTAL IPL RUNS:")
print(ipl_data["delivery_total_runs"].sum())

print("\n3. BYES AND LEGBYES:")
print(
    ipl_data.loc[
        ipl_data["extras_type"].isin(["byes", "legbyes"]),
        "delivery_total_runs"
    ].sum()
)

print("\n4. OTHER EXTRAS TOTAL:")
print(
    ipl_data.loc[
        ipl_data["extras_type"].eq("other"),
        "delivery_total_runs"
    ].sum()
)

print("\n--- STEP 16P COMPLETED ---")

# --- STEP 16Q: BOWLING ECONOMY SENSITIVITY TEST ---

print("\n--- STEP 16Q: BOWLING ECONOMY SENSITIVITY ---")

# Work on a separate copy
temp_data = corrected_chase.copy()

# METHOD A:
# Batter runs + wides + no-ball penalty
temp_data["runs_method_A"] = (
    temp_data["runs"] +
    temp_data["extras1_runs"].where(
        temp_data["extras_type"].isin(["wide", "Overstep"]), 0
    )
)

# METHOD B:
# Method A + extras2
temp_data["runs_method_B"] = (
    temp_data["runs_method_A"] +
    temp_data["extras_2_runs"]
)

# METHOD C:
# Batter runs + all recorded extras
temp_data["runs_method_C"] = (
    temp_data["runs"] +
    temp_data["extras1_runs"] +
    temp_data["extras_2_runs"]
)

# 1. Total runs comparison
print("\n1. TOTAL RUNS BY METHOD")

print("Method A:", temp_data["runs_method_A"].sum())
print("Method B:", temp_data["runs_method_B"].sum())
print("Method C:", temp_data["runs_method_C"].sum())

# 2. Pressure bowling economy comparison
for method in [
    "runs_method_A",
    "runs_method_B",
    "runs_method_C"
]:

    print(f"\nTOP 10 PRESSURE BOWLERS - {method}")

    pressure_data = temp_data[
        temp_data["pressure_level"].isin(["High", "Very High"])
    ].copy()

    result = pressure_data.groupby(
        ["bowler_id", "bowler_name"]
    ).agg(
        runs_conceded=("{}".format(method), "sum"),
        legal_balls=("is_legal_ball", "sum"),
        wickets=("bowler_wicket", "sum"),
        matches=("match_id", "nunique")
    ).reset_index()

    # Minimum sample-size qualification
    result = result[
        (result["legal_balls"] >= 30) &
        (result["matches"] >= 3)
    ].copy()

    # Economy rate
    result["economy"] = (
        result["runs_conceded"] /
        result["legal_balls"] * 6
    )

    # Display best 10 economy figures
    result = result.sort_values(
        ["economy", "wickets"],
        ascending=[True, False]
    )

    print(
        result.head(10).round(2).to_string(index=False)
    )

print("\n--- STEP 16Q COMPLETED ---")

# --- STEP 16R: BOWLING RANKING IMPACT ANALYSIS ---

print("\n--- STEP 16R: BOWLING RANKING IMPACT ---")

pressure_data = corrected_chase.copy()

# Method A: Standard bowler runs
pressure_data["runs_A"] = (
    pressure_data["runs"] +
    pressure_data["extras1_runs"].where(
        pressure_data["extras_type"].isin(["wide", "Overstep"]), 0
    )
)

# Method B: Method A + extras2
pressure_data["runs_B"] = (
    pressure_data["runs_A"] +
    pressure_data["extras_2_runs"]
)

# Aggregate both methods
bowling_A = pressure_data.groupby(
    ["bowler_id", "bowler_name"]
).agg(
    runs_A=("runs_A", "sum"),
    legal_balls=("is_legal_ball", "sum"),
    wickets=("bowler_wicket", "sum"),
    matches=("match_id", "nunique")
).reset_index()

bowling_B = pressure_data.groupby(
    ["bowler_id", "bowler_name"]
).agg(
    runs_B=("runs_B", "sum")
).reset_index()

# Combine
comparison = bowling_A.merge(
    bowling_B,
    on=["bowler_id", "bowler_name"]
)

# Minimum sample size
comparison = comparison[
    (comparison["legal_balls"] >= 30) &
    (comparison["matches"] >= 3)
].copy()

# Calculate economy
comparison["economy_A"] = (
    comparison["runs_A"] / comparison["legal_balls"] * 6
)

comparison["economy_B"] = (
    comparison["runs_B"] / comparison["legal_balls"] * 6
)

# Calculate ranking
comparison["rank_A"] = comparison["economy_A"].rank(
    method="min", ascending=True
)

comparison["rank_B"] = comparison["economy_B"].rank(
    method="min", ascending=True
)

comparison["rank_change"] = (
    comparison["rank_B"] - comparison["rank_A"]
)

comparison["economy_difference"] = (
    comparison["economy_B"] - comparison["economy_A"]
)

# Display top 20
comparison = comparison.sort_values("rank_A")

print("\nTOP 20 BOWLERS: METHOD A VS METHOD B")

print(
    comparison[
        [
            "bowler_name",
            "runs_A",
            "runs_B",
            "legal_balls",
            "wickets",
            "economy_A",
            "economy_B",
            "rank_A",
            "rank_B",
            "rank_change"
        ]
    ].head(20).round(2).to_string(index=False)
)

# Overall impact
print("\nRANKING IMPACT SUMMARY")
print("Qualified bowlers:", len(comparison))
print(
    "Bowlers whose rank changed:",
    (comparison["rank_change"] != 0).sum()
)
print(
    "Maximum economy difference:",
    comparison["economy_difference"].max()
)

print("\n--- STEP 16R COMPLETED ---")

# --- STEP 16S: HIGH-PRESSURE BOWLING RANKING COMPARISON ---

print("\n--- STEP 16S: HIGH-PRESSURE RANKING COMPARISON ---")

pressure_data = corrected_chase[
    corrected_chase["pressure_level"].isin(["High", "Very High"])
].copy()

# Method A: Batter runs + wides + no-ball penalty
pressure_data["runs_A"] = (
    pressure_data["runs"] +
    pressure_data["extras1_runs"].where(
        pressure_data["extras_type"].isin(["wide", "Overstep"]), 0
    )
)

# Method B: Method A + extras2
pressure_data["runs_B"] = (
    pressure_data["runs_A"] +
    pressure_data["extras_2_runs"]
)

# Aggregate Method A
bowling_A = pressure_data.groupby(
    ["bowler_id", "bowler_name"]
).agg(
    runs_A=("runs_A", "sum"),
    legal_balls=("is_legal_ball", "sum"),
    wickets=("bowler_wicket", "sum"),
    matches=("match_id", "nunique")
).reset_index()

# Aggregate Method B
bowling_B = pressure_data.groupby(
    ["bowler_id", "bowler_name"]
).agg(
    runs_B=("runs_B", "sum")
).reset_index()

# Combine both methods
comparison = bowling_A.merge(
    bowling_B,
    on=["bowler_id", "bowler_name"]
)

# Qualification
comparison = comparison[
    (comparison["legal_balls"] >= 30) &
    (comparison["matches"] >= 3)
].copy()

# Calculate economy
comparison["economy_A"] = (
    comparison["runs_A"] / comparison["legal_balls"] * 6
)

comparison["economy_B"] = (
    comparison["runs_B"] / comparison["legal_balls"] * 6
)

# Rank both methods
comparison["rank_A"] = comparison["economy_A"].rank(
    method="min", ascending=True
)

comparison["rank_B"] = comparison["economy_B"].rank(
    method="min", ascending=True
)

comparison["rank_change"] = (
    comparison["rank_B"] - comparison["rank_A"]
)

print("\nTOP 20 HIGH-PRESSURE BOWLERS")

print(
    comparison.sort_values("rank_A")[
        [
            "bowler_name",
            "runs_A",
            "runs_B",
            "legal_balls",
            "wickets",
            "matches",
            "economy_A",
            "economy_B",
            "rank_A",
            "rank_B",
            "rank_change"
        ]
    ].head(20).round(2).to_string(index=False)
)

print("\nHIGH-PRESSURE RANKING SUMMARY")

print("Qualified bowlers:", len(comparison))

print(
    "Bowlers whose rank changed:",
    (comparison["rank_change"] != 0).sum()
)

print(
    "Maximum absolute economy difference:",
    comparison["economy_B"].sub(
        comparison["economy_A"]
    ).abs().max()
)

print("\n--- STEP 16S COMPLETED ---")

# --- STEP 16T: COMPLETE PRESSURE BOWLING METRICS ---

print("\n--- STEP 16T: PRESSURE BOWLING METRICS ---")

pressure_data = corrected_chase[
    corrected_chase["pressure_level"].isin(["High", "Very High"])
].copy()

# Method A: Provisional bowler runs
pressure_data["bowler_runs"] = (
    pressure_data["runs"] +
    pressure_data["extras1_runs"].where(
        pressure_data["extras_type"].isin(["wide", "Overstep"]), 0
    )
)

# Total runs on each delivery (for dot-ball calculation)
pressure_data["delivery_total_runs"] = (
    pressure_data["runs"] +
    pressure_data["extras1_runs"] +
    pressure_data["extras_2_runs"]
)

# Legal dot balls
pressure_data["dot_ball"] = (
    pressure_data["is_legal_ball"] &
    (pressure_data["delivery_total_runs"] == 0)
)

# Boundary deliveries
pressure_data["boundary"] = (
    pressure_data["is_four"] | pressure_data["is_six"]
)

# Aggregate bowler performance
bowler_metrics = pressure_data.groupby(
    ["bowler_id", "bowler_name"]
).agg(
    runs_conceded=("bowler_runs", "sum"),
    legal_balls=("is_legal_ball", "sum"),
    wickets=("bowler_wicket", "sum"),
    matches=("match_id", "nunique"),
    dot_balls=("dot_ball", "sum"),
    boundaries=("boundary", "sum")
).reset_index()

# Minimum sample qualification
bowler_metrics = bowler_metrics[
    (bowler_metrics["legal_balls"] >= 30) &
    (bowler_metrics["matches"] >= 3)
].copy()

# Economy rate
bowler_metrics["economy"] = (
    bowler_metrics["runs_conceded"] /
    bowler_metrics["legal_balls"] * 6
)

# Wickets per 100 legal balls
bowler_metrics["wickets_per_100_balls"] = (
    bowler_metrics["wickets"] /
    bowler_metrics["legal_balls"] * 100
)

# Bowling strike rate
bowler_metrics["bowling_strike_rate"] = (
    bowler_metrics["legal_balls"] /
    bowler_metrics["wickets"].replace(0, float("nan"))
)

# Dot ball percentage
bowler_metrics["dot_ball_percentage"] = (
    bowler_metrics["dot_balls"] /
    bowler_metrics["legal_balls"] * 100
)

# Boundary percentage per legal ball
bowler_metrics["boundary_percentage"] = (
    bowler_metrics["boundaries"] /
    bowler_metrics["legal_balls"] * 100
)

# Display top 20 by wickets
print("\nTOP 20 PRESSURE BOWLERS BY WICKETS")

print(
    bowler_metrics.sort_values(
        ["wickets", "economy"],
        ascending=[False, True]
    )[
        [
            "bowler_name",
            "runs_conceded",
            "legal_balls",
            "wickets",
            "matches",
            "economy",
            "wickets_per_100_balls",
            "bowling_strike_rate",
            "dot_ball_percentage",
            "boundary_percentage"
        ]
    ].head(20).round(2).to_string(index=False)
)

print("\nQUALIFIED BOWLERS:", len(bowler_metrics))

print("\n--- STEP 16T COMPLETED ---")

# --- STEP 16U: BOWLING METRICS VALIDATION ---

print("\n--- STEP 16U: BOWLING METRICS VALIDATION ---")

# Check missing values
metric_columns = [
    "runs_conceded",
    "legal_balls",
    "wickets",
    "matches",
    "economy",
    "wickets_per_100_balls",
    "bowling_strike_rate",
    "dot_ball_percentage",
    "boundary_percentage"
]

print("\n1. MISSING VALUES")
print(bowler_metrics[metric_columns].isnull().sum())

# Check invalid values
print("\n2. INVALID VALUES")

print(
    "Negative runs:",
    (bowler_metrics["runs_conceded"] < 0).sum()
)

print(
    "Zero legal balls:",
    (bowler_metrics["legal_balls"] == 0).sum()
)

print(
    "Negative wickets:",
    (bowler_metrics["wickets"] < 0).sum()
)

print(
    "Invalid economy:",
    (~bowler_metrics["economy"].between(0, 30)).sum()
)

print(
    "Invalid dot percentages:",
    (~bowler_metrics["dot_ball_percentage"].between(0, 100)).sum()
)

print(
    "Invalid boundary percentages:",
    (~bowler_metrics["boundary_percentage"].between(0, 100)).sum()
)

# Verify calculations
expected_economy = (
    bowler_metrics["runs_conceded"] /
    bowler_metrics["legal_balls"] * 6
)

expected_wicket_rate = (
    bowler_metrics["wickets"] /
    bowler_metrics["legal_balls"] * 100
)

print("\n3. CALCULATION CONSISTENCY")

print(
    "Economy mismatches:",
    (~(
        (bowler_metrics["economy"] - expected_economy).abs() < 0.001
    )).sum()
)

print(
    "Wicket-rate mismatches:",
    (~(
        (bowler_metrics["wickets_per_100_balls"] - expected_wicket_rate).abs() < 0.001
    )).sum()
)

print("\n4. SAMPLE SIZE SUMMARY")
print(
    bowler_metrics[
        ["legal_balls", "matches"]
    ].describe().round(2)
)

print("\n--- STEP 16U COMPLETED ---")

# --- STEP 16V: 100-POINT PRESSURE BOWLING SCORE ---

print("\n--- STEP 16V: BOWLING SCORING MODEL ---")

scoring_data = bowler_metrics.copy()

# Convert each metric into a percentile score (0-100)
# Lower economy is better
scoring_data["economy_score"] = (
    1 - scoring_data["economy"].rank(pct=True)
) * 100

# Higher wicket rate is better
scoring_data["wicket_rate_score"] = (
    scoring_data["wickets_per_100_balls"].rank(pct=True)
) * 100

# Higher dot-ball percentage is better
scoring_data["dot_score"] = (
    scoring_data["dot_ball_percentage"].rank(pct=True)
) * 100

# Lower boundary percentage is better
scoring_data["boundary_control_score"] = (
    1 - scoring_data["boundary_percentage"].rank(pct=True)
) * 100

# More pressure wickets is better
scoring_data["wickets_score"] = (
    scoring_data["wickets"].rank(pct=True)
) * 100

# Weighted score out of 100
scoring_data["raw_score"] = (
    scoring_data["economy_score"] * 0.25 +
    scoring_data["wicket_rate_score"] * 0.25 +
    scoring_data["dot_score"] * 0.20 +
    scoring_data["boundary_control_score"] * 0.15 +
    scoring_data["wickets_score"] * 0.15
)

# Sample reliability adjustment
# 120 is the initial smoothing constant
scoring_data["reliability"] = (
    scoring_data["legal_balls"] /
    (scoring_data["legal_balls"] + 120)
)

# Shrink uncertain scores towards neutral score 50
scoring_data["final_score"] = (
    50 +
    scoring_data["reliability"] *
    (scoring_data["raw_score"] - 50)
)

# Final ranking
scoring_data = scoring_data.sort_values(
    "final_score",
    ascending=False
).reset_index(drop=True)

scoring_data["final_rank"] = (
    scoring_data.index + 1
)

print("\nTOP 20 PRESSURE BOWLERS")

print(
    scoring_data[
        [
            "final_rank",
            "bowler_name",
            "final_score",
            "raw_score",
            "economy",
            "wickets",
            "wickets_per_100_balls",
            "dot_ball_percentage",
            "boundary_percentage",
            "legal_balls",
            "matches",
            "reliability"
        ]
    ].head(20).round(2).to_string(index=False)
)

print("\nTOTAL QUALIFIED BOWLERS:", len(scoring_data))

print("\n--- STEP 16V COMPLETED ---")

# --- STEP 16W: SCORING MODEL SENSITIVITY TEST ---

print("\n--- STEP 16W: SCORING SENSITIVITY ---")

test_data = bowler_metrics.copy()

# Percentile components
test_data["economy_score"] = (
    1 - test_data["economy"].rank(pct=True)
) * 100

test_data["wicket_rate_score"] = (
    test_data["wickets_per_100_balls"].rank(pct=True)
) * 100

test_data["dot_score"] = (
    test_data["dot_ball_percentage"].rank(pct=True)
) * 100

test_data["boundary_score"] = (
    1 - test_data["boundary_percentage"].rank(pct=True)
) * 100

test_data["wickets_score"] = (
    test_data["wickets"].rank(pct=True)
) * 100

# Three alternative weight combinations
weight_models = {
    "Balanced": {
        "economy_score": 0.25,
        "wicket_rate_score": 0.25,
        "dot_score": 0.20,
        "boundary_score": 0.15,
        "wickets_score": 0.15
    },
    "Wicket_Focused": {
        "economy_score": 0.15,
        "wicket_rate_score": 0.35,
        "dot_score": 0.15,
        "boundary_score": 0.10,
        "wickets_score": 0.25
    },
    "Control_Focused": {
        "economy_score": 0.30,
        "wicket_rate_score": 0.15,
        "dot_score": 0.25,
        "boundary_score": 0.25,
        "wickets_score": 0.05
    }
}

# Reliability adjustment
test_data["reliability"] = (
    test_data["legal_balls"] /
    (test_data["legal_balls"] + 120)
)

for model_name, weights in weight_models.items():

    raw_score = sum(
        test_data[column] * weight
        for column, weight in weights.items()
    )

    test_data[model_name] = (
        50 +
        test_data["reliability"] *
        (raw_score - 50)
    )

    test_data[model_name + "_rank"] = (
        test_data[model_name].rank(
            ascending=False,
            method="min"
        )
    )

# Show top 10 for each model
for model_name in weight_models:

    print(f"\nTOP 10 - {model_name.upper()}")

    print(
        test_data.sort_values(
            model_name,
            ascending=False
        )[
            [
                "bowler_name",
                model_name,
                model_name + "_rank"
            ]
        ].head(10).round(2).to_string(index=False)
    )

# Compare top 20 overlap
print("\nTOP 20 RANKING OVERLAP")

for model_name in weight_models:

    top_players = set(
        test_data.nsmallest(
            20, model_name + "_rank"
        )["bowler_id"]
    )

    print(
        model_name,
        "Top 20 players:",
        len(top_players)
    )

# Correlation between rankings
print("\nRANK CORRELATION")

print(
    test_data[
        [
            "Balanced_rank",
            "Wicket_Focused_rank",
            "Control_Focused_rank"
        ]
    ].corr().round(3)
)

print("\n--- STEP 16W COMPLETED ---")

# --- STEP 16X: ACTUAL TOP 20 OVERLAP ---

print("\n--- STEP 16X: ACTUAL RANKING OVERLAP ---")

balanced_top20 = set(
    test_data.nlargest(20, "Balanced")["bowler_id"]
)

wicket_top20 = set(
    test_data.nlargest(20, "Wicket_Focused")["bowler_id"]
)

control_top20 = set(
    test_data.nlargest(20, "Control_Focused")["bowler_id"]
)

print(
    "Balanced vs Wicket-focused:",
    len(balanced_top20 & wicket_top20),
    "/ 20 common players"
)

print(
    "Balanced vs Control-focused:",
    len(balanced_top20 & control_top20),
    "/ 20 common players"
)

print(
    "Wicket-focused vs Control-focused:",
    len(wicket_top20 & control_top20),
    "/ 20 common players"
)

common_all = (
    balanced_top20 &
    wicket_top20 &
    control_top20
)

print(
    "\nPlayers common in ALL THREE Top 20:",
    len(common_all)
)

common_names = test_data[
    test_data["bowler_id"].isin(common_all)
][["bowler_name"]].sort_values("bowler_name")

print(common_names.to_string(index=False))

print("\n--- STEP 16X COMPLETED ---")

# --- STEP 16Y: SEASON-WISE PRESSURE PERFORMANCE ---

print("\n--- STEP 16Y: SEASON-WISE CONSISTENCY ---")

season_pressure = corrected_chase[
    corrected_chase["pressure_level"].isin(["High", "Very High"])
].copy()

# Recalculate provisional bowler runs
season_pressure["bowler_runs"] = (
    season_pressure["runs"] +
    season_pressure["extras1_runs"].where(
        season_pressure["extras_type"].isin(
            ["wide", "Overstep"]
        ), 0
    )
)

# Attach season information
season_metadata = matches[
    ["match_id", "comp_id"]
].merge(
    competitions[["comp_id", "season"]],
    on="comp_id",
    how="left"
)

# Remove any old season/comp_id columns before merging
season_pressure = season_pressure.drop(
    columns=["comp_id", "season"],
    errors="ignore"
)

season_pressure = season_pressure.merge(
    season_metadata[["match_id", "season"]],
    on="match_id",
    how="left"
)

# Keep the 15 players common to all three models
season_pressure = season_pressure[
    season_pressure["bowler_id"].isin(common_all)
].copy()

# Aggregate season-wise performance
season_summary = season_pressure.groupby(
    ["bowler_id", "bowler_name", "season"]
).agg(
    runs_conceded=("bowler_runs", "sum"),
    legal_balls=("is_legal_ball", "sum"),
    wickets=("bowler_wicket", "sum"),
    matches=("match_id", "nunique")
).reset_index()

# Calculate economy
season_summary["economy"] = (
    season_summary["runs_conceded"] /
    season_summary["legal_balls"] * 6
)

print("\nSEASON-WISE PRESSURE PERFORMANCE")

print(
    season_summary.sort_values(
        ["bowler_name", "season"]
    )[
        [
            "bowler_name",
            "season",
            "matches",
            "legal_balls",
            "wickets",
            "economy"
        ]
    ].round(2).to_string(index=False)
)

print("\n--- STEP 16Y COMPLETED ---")

# --- STEP 16Z: SEASON CONSISTENCY AND SAMPLE SIZE ---

print("\n--- STEP 16Z: SEASON CONSISTENCY ---")

# 1. Match ID ke saath IPL season attach karo
season_lookup = matches[["match_id", "comp_id"]].merge(
    competitions[["comp_id", "season"]],
    on="comp_id",
    how="inner"
)

# 2. High-pressure deliveries only
season_data = corrected_chase[
    corrected_chase["pressure_level"].isin(
        ["High", "Very High"]
    )
].copy()

# 3. Season information merge karo
season_data = season_data.merge(
    season_lookup[["match_id", "season"]],
    on="match_id",
    how="left"
)

# 4. Bowler runs conceded - Method A
# Batter runs + wides + no-ball penalty
# Byes and legbyes bowler ke runs mein include nahi honge

season_data["runs_conceded"] = (
    season_data["runs"] +
    season_data["extras1_runs"].where(
        season_data["extras_type"].isin(
            ["wide", "Overstep"]
        ),
        0
    )
)

# 5. Bowler + season performance
season_summary = season_data.groupby(
    ["bowler_id", "bowler_name", "season"]
).agg(
    runs_conceded=("runs_conceded", "sum"),
    legal_balls=("is_legal_ball", "sum"),
    wickets=("bowler_wicket", "sum"),
    matches=("match_id", "nunique")
).reset_index()

# 6. Economy calculate karo
season_summary["economy"] = (
    season_summary["runs_conceded"] /
    season_summary["legal_balls"] * 6
)

# 7. Minimum 30 legal balls per season
qualified_seasons = season_summary[
    season_summary["legal_balls"] >= 30
].copy()

# 8. Player-level consistency summary
consistency = qualified_seasons.groupby(
    ["bowler_id", "bowler_name"]
).agg(
    qualified_seasons=("season", "nunique"),
    total_legal_balls=("legal_balls", "sum"),
    total_wickets=("wickets", "sum"),
    average_season_economy=("economy", "mean"),
    economy_variation=("economy", "std")
).reset_index()

# Single season ke liye variation undefined hota hai
consistency["economy_variation"] = (
    consistency["economy_variation"].fillna(0)
)

# 9. Season-wise output
print("\nSEASON-LEVEL QUALIFICATION")

print(
    qualified_seasons[
        [
            "bowler_name",
            "season",
            "matches",
            "legal_balls",
            "wickets",
            "economy"
        ]
    ].sort_values(
        ["bowler_name", "season"]
    ).round(2).to_string(index=False)
)

# 10. Player consistency output
print("\nPLAYER CONSISTENCY SUMMARY")

print(
    consistency.sort_values(
        ["qualified_seasons", "total_legal_balls"],
        ascending=[False, False]
    ).head(25).round(2).to_string(index=False)
)

# 11. Validation
print("\nSEASON CONSISTENCY VALIDATION")

print("Total bowler-season records:", len(season_summary))
print("Qualified bowler-season records:", len(qualified_seasons))
print("Players with at least 1 qualified season:", len(consistency))

print(
    "Players with 3+ qualified seasons:",
    (consistency["qualified_seasons"] >= 3).sum()
)

print("\n--- STEP 16Z COMPLETED ---")

# --- STEP 16ZA: FINAL 15 BOWLERS CONSISTENCY CHECK ---

print("\n--- STEP 16ZA: TOP 15 CONSISTENCY CHECK ---")

shortlist_consistency = consistency[
    consistency["bowler_id"].isin(common_all)
].copy()

# Include all 15 players, even if no season qualified
shortlist_names = test_data[
    test_data["bowler_id"].isin(common_all)
][["bowler_id", "bowler_name"]].drop_duplicates()

shortlist_consistency = shortlist_names.merge(
    shortlist_consistency,
    on=["bowler_id", "bowler_name"],
    how="left"
)

# Fill missing season counts and totals
numeric_columns = [
    "qualified_seasons",
    "total_legal_balls",
    "total_wickets"
]

shortlist_consistency[numeric_columns] = (
    shortlist_consistency[numeric_columns].fillna(0)
)

print("\nALL 15 SHORTLISTED BOWLERS")

print(
    shortlist_consistency.sort_values(
        ["qualified_seasons", "total_legal_balls"],
        ascending=[False, False]
    ).round(2).to_string(index=False)
)

print("\n--- STEP 16ZA COMPLETED ---")
# --- STEP 17A: CHECK EXISTING BOWLING MODEL VARIABLES ---

print("\n--- STEP 17A: EXISTING MODEL VARIABLES ---")

for name in globals():
    if "score" in name.lower() or "rank" in name.lower():
        print(name)

print("\n--- STEP 17A COMPLETED ---")
# --- STEP 17B: INSPECT BOWLING DATAFRAMES ---

print("\n--- STEP 17B: DATAFRAME INSPECTION ---")

for name, obj in globals().copy().items():
    if isinstance(obj, pd.DataFrame):
        print(f"\nDataFrame: {name}")
        print("Shape:", obj.shape)
        print("Columns:", list(obj.columns))

print("\n--- STEP 17B COMPLETED ---")
# --- STEP 17C: FIND BOWLING SCORE DATA ---

print("\n--- STEP 17C: BOWLING DATA VARIABLES ---")

for name, obj in globals().copy().items():
    if isinstance(obj, pd.DataFrame):
        if any(word in name.lower() for word in
               ["bowl", "pressure", "score", "rank"]):
            print(f"\n{name}")
            print("Shape:", obj.shape)
            print("Columns:", list(obj.columns))

print("\n--- STEP 17C COMPLETED ---")

# --- STEP 17D: FINAL BOWLING SCORING MODEL ---

print("\n--- STEP 17D: FINAL BOWLING SCORING MODEL ---")

# 1. Calculate performance percentile scores
bowling_scoring_base = bowler_metrics.copy()

bowling_scoring_base["economy_score"] = (
    1 - bowling_scoring_base["economy"].rank(pct=True)
) * 100

bowling_scoring_base["wicket_rate_score"] = (
    bowling_scoring_base["wickets_per_100_balls"].rank(pct=True)
) * 100

bowling_scoring_base["dot_score"] = (
    bowling_scoring_base["dot_ball_percentage"].rank(pct=True)
) * 100

bowling_scoring_base["boundary_control_score"] = (
    1 - bowling_scoring_base["boundary_percentage"].rank(pct=True)
) * 100

# 2. Use only the shortlisted 15 bowlers
final_bowling = bowling_scoring_base.merge(
    shortlist_consistency,
    on=["bowler_id", "bowler_name"],
    how="inner"
)

# 3. Season experience score (reference: all 121 players)
final_bowling["season_depth_score"] = (
    final_bowling["qualified_seasons"].rank(pct=True) * 100
)

# 4. Stability score
stable_players = consistency[
    consistency["qualified_seasons"] >= 2
].copy()

stable_players["stability_score"] = (
    1 - stable_players["economy_variation"].rank(pct=True)
) * 100

final_bowling = final_bowling.merge(
    stable_players[["bowler_id", "stability_score"]],
    on="bowler_id",
    how="left"
)

# One qualified season is insufficient to measure variation.
final_bowling["stability_score"] = (
    final_bowling["stability_score"].fillna(50)
)

final_bowling["consistency_score"] = (
    0.70 * final_bowling["season_depth_score"] +
    0.30 * final_bowling["stability_score"]
)

# 5. Weighted score
final_bowling["raw_final_score"] = (
    0.25 * final_bowling["economy_score"] +
    0.30 * final_bowling["wicket_rate_score"] +
    0.20 * final_bowling["dot_score"] +
    0.15 * final_bowling["boundary_control_score"] +
    0.10 * final_bowling["consistency_score"]
)

# 6. Sample-size adjustment
final_bowling["reliability"] = (
    final_bowling["legal_balls"] /
    (final_bowling["legal_balls"] + 120)
)

final_bowling["final_score"] = (
    50 + final_bowling["reliability"] *
    (final_bowling["raw_final_score"] - 50)
)

# 7. Final ranking
final_bowling = final_bowling.sort_values(
    "final_score", ascending=False
).reset_index(drop=True)

final_bowling["final_rank"] = final_bowling.index + 1

# 8. Display Top 10
print("\n========== FINAL TOP 10 BOWLERS ==========")

print(
    final_bowling[
        [
            "final_rank",
            "bowler_name",
            "final_score",
            "economy",
            "wickets",
            "wickets_per_100_balls",
            "dot_ball_percentage",
            "boundary_percentage",
            "qualified_seasons",
            "legal_balls"
        ]
    ].head(10).round(2).to_string(index=False)
)

print("\nShortlisted bowlers:", len(final_bowling))
print("\n--- STEP 17D COMPLETED ---")

# --- STEP 18: DEATH-OVER SPECIALIST ANALYSIS ---

print("\n--- STEP 18: DEATH-OVER SPECIALIST ANALYSIS ---")

# 1. Select high-pressure death-over deliveries
death_data = pressure_data[
    pressure_data["overid"].between(16, 20)
].copy()

print("Death-over pressure deliveries:", len(death_data))

# 2. Calculate bowler-wise performance
death_bowlers = death_data.groupby(
    ["bowler_id", "bowler_name"]
).agg(
    runs_conceded=("bowler_runs", "sum"),
    legal_balls=("is_legal_ball", "sum"),
    wickets=("bowler_wicket", "sum"),
    matches=("match_id", "nunique"),
    dot_balls=("dot_ball", "sum"),
    boundaries=("boundary", "sum")
).reset_index()

# 3. Calculate performance metrics
death_bowlers["economy"] = (
    death_bowlers["runs_conceded"] /
    death_bowlers["legal_balls"] * 6
)

death_bowlers["wickets_per_100_balls"] = (
    death_bowlers["wickets"] /
    death_bowlers["legal_balls"] * 100
)

death_bowlers["dot_ball_percentage"] = (
    death_bowlers["dot_balls"] /
    death_bowlers["legal_balls"] * 100
)

death_bowlers["boundary_percentage"] = (
    death_bowlers["boundaries"] /
    death_bowlers["legal_balls"] * 100
)

# 4. Apply minimum sample-size filter
qualified_death_bowlers = death_bowlers[
    (death_bowlers["legal_balls"] >= 30) &
    (death_bowlers["matches"] >= 3)
].copy()

# 5. Rank by wicket-taking and economy
qualified_death_bowlers = qualified_death_bowlers.sort_values(
    ["wickets", "economy"],
    ascending=[False, True]
).reset_index(drop=True)

print("\nQualified death-over bowlers:", len(qualified_death_bowlers))

print("\n========== TOP 15 DEATH-OVER BOWLERS ==========")

print(
    qualified_death_bowlers[
        [
            "bowler_name",
            "runs_conceded",
            "legal_balls",
            "wickets",
            "matches",
            "economy",
            "wickets_per_100_balls",
            "dot_ball_percentage",
            "boundary_percentage"
        ]
    ].head(15).round(2).to_string(index=False)
)

print("\n--- STEP 18 COMPLETED ---")

# --- STEP 19: VERIFY OVER NUMBERING ---

print("\n--- STEP 19: VERIFY OVER NUMBERING ---")

print("Minimum overid:", pressure_data["overid"].min())
print("Maximum overid:", pressure_data["overid"].max())

print("\nUnique over IDs:")
print(sorted(pressure_data["overid"].dropna().unique()))

print("\nDelivery count by over ID:")
print(
    pressure_data["overid"]
    .value_counts()
    .sort_index()
    .to_string()
)

print("\n--- STEP 19 COMPLETED ---")

# ============================================================
# STEP 22: FINAL BATTING SCORING MODEL - CONSISTENT DATA
# ============================================================

print("\n--- STEP 22: FINAL BATTING SCORING MODEL ---")

# 1. Use ONE consistent high-pressure batting dataset
final_batting = pressure_batters.copy()

# 2. Minimum sample qualification
final_batting = final_batting[
    (final_batting["balls"] >= 60) &
    (final_batting["matches"] >= 5)
].copy()

print("Total high-pressure batters:", len(pressure_batters))
print("Qualified batters:", len(final_batting))

# 3. Calculate runs per dismissal
final_batting["runs_per_dismissal"] = (
    final_batting["runs"] /
    final_batting["dismissals"].replace(0, float("nan"))
)

# Handle zero dismissals
median_rpd = final_batting["runs_per_dismissal"].median()

final_batting["runs_per_dismissal"] = (
    final_batting["runs_per_dismissal"].fillna(median_rpd)
)

# 4. Calculate percentile scores
# Higher strike rate = better
final_batting["strike_rate_score"] = (
    final_batting["strike_rate"].rank(pct=True) * 100
)

# Higher runs per dismissal = better
final_batting["survival_score"] = (
    final_batting["runs_per_dismissal"].rank(pct=True) * 100
)

# Higher total pressure runs = better
final_batting["run_volume_score"] = (
    final_batting["runs"].rank(pct=True) * 100
)

# 5. Sample reliability
final_batting["reliability_score"] = (
    final_batting["balls"] /
    (final_batting["balls"] + 60)
) * 100

# 6. Final weighted score
final_batting["final_score"] = (
    0.40 * final_batting["strike_rate_score"] +
    0.30 * final_batting["survival_score"] +
    0.20 * final_batting["run_volume_score"] +
    0.10 * final_batting["reliability_score"]
)

# 7. Rank batters
final_batting = final_batting.sort_values(
    "final_score",
    ascending=False
).reset_index(drop=True)

final_batting["final_rank"] = (
    final_batting.index + 1
)

# 8. Display Top 10
print("\n========== FINAL TOP 10 BATTERS ==========")

print(
    final_batting[
        [
            "final_rank",
            "striker_name",
            "final_score",
            "runs",
            "balls",
            "strike_rate",
            "runs_per_dismissal",
            "matches",
            "dismissals"
        ]
    ].head(10).round(2).to_string(index=False)
)

print("\n--- STEP 22 COMPLETED ---")

# ============================================================
# STEP 23: FINAL COMBINED RECOMMENDATION LIST
# ============================================================

print("\n--- STEP 23: FINAL COMBINED RECOMMENDATIONS ---")

# Top 10 batters
top_batters = final_batting.head(10).copy()

top_batters["role"] = "Batting"
top_batters["player_name"] = top_batters["striker_name"]
top_batters["score"] = top_batters["final_score"]

# Top 10 bowlers
top_bowlers = final_bowling.head(10).copy()

top_bowlers["role"] = "Bowling"
top_bowlers["player_name"] = top_bowlers["bowler_name"]
top_bowlers["score"] = top_bowlers["final_score"]

# Combine
final_recommendations = pd.concat(
    [
        top_batters[["player_name", "role", "score"]],
        top_bowlers[["player_name", "role", "score"]]
    ],
    ignore_index=True
)

print("\n========== FINAL 20 PLAYER RECOMMENDATIONS ==========")

print(
    final_recommendations.round(2).to_string(index=False)
)

# Export CSV
final_recommendations.to_csv(
    "final_recommendations.csv",
    index=False
)

print("\nSaved: final_recommendations.csv")
print("\n--- STEP 23 COMPLETED ---")

# ============================================================
# STEP 24: FINAL RANKING VALIDATION
# ============================================================

print("\n--- STEP 24: FINAL RANKING VALIDATION ---")

# 1. Check Top 10 batter rankings
top10_batters_check = final_batting.head(10)

print("\nBATTER VALIDATION")
print("Number of batters:", len(top10_batters_check))
print("Unique batter IDs:", top10_batters_check["striker_id"].nunique())
print("Missing values:", top10_batters_check[
    ["striker_name", "final_score", "runs", "balls",
     "strike_rate", "runs_per_dismissal"]
].isnull().sum().sum())

print("Minimum balls:", top10_batters_check["balls"].min())
print("Minimum matches:", top10_batters_check["matches"].min())

# 2. Check Top 10 bowler rankings
top10_bowlers_check = final_bowling.head(10)

print("\nBOWLER VALIDATION")
print("Number of bowlers:", len(top10_bowlers_check))
print("Unique bowler IDs:", top10_bowlers_check["bowler_id"].nunique())
print("Missing values:", top10_bowlers_check[
    ["bowler_name", "final_score", "economy",
     "wickets", "legal_balls"]
].isnull().sum().sum())

print("Minimum legal balls:", top10_bowlers_check["legal_balls"].min())
print("Minimum wickets:", top10_bowlers_check["wickets"].min())

# 3. Check ranking order
print("\nRANKING ORDER CHECK")

print(
    "Batting scores descending:",
    top10_batters_check["final_score"].is_monotonic_decreasing
)

print(
    "Bowling scores descending:",
    top10_bowlers_check["final_score"].is_monotonic_decreasing
)

# 4. Check players appearing in both lists
batter_names = set(top10_batters_check["striker_name"])
bowler_names = set(top10_bowlers_check["bowler_name"])

common_players = batter_names.intersection(bowler_names)

print("\nPLAYERS IN BOTH LISTS:")
print(sorted(common_players))

# 5. Final status
print("\n--- STEP 24 COMPLETED ---")

# ============================================================
# STEP 25A: DOMESTIC COMPETITION DISCOVERY
# ============================================================

print("\n--- STEP 25A: COMPETITION DISCOVERY ---")

competitions_df = pd.read_csv("datapack/competitions.csv")
mapping_df = pd.read_csv(
    "datapack/competition_team_player_mapping.csv"
)

print("\nCOMPETITIONS FILE COLUMNS:")
print(competitions_df.columns.tolist())

print("\nALL AVAILABLE COMPETITIONS:")
print(competitions_df.to_string(index=False))

print("\nPLAYER MAPPING FILE COLUMNS:")
print(mapping_df.columns.tolist())

print("\nPLAYER MAPPING SAMPLE:")
print(mapping_df.head(10).to_string(index=False))

print("\n--- STEP 25A COMPLETED ---")

# ============================================================
# STEP 25B: SHORTLISTED PLAYERS IN OTHER T20 COMPETITIONS
# ============================================================

print("\n--- STEP 25B: OTHER T20 COMPETITION CHECK ---")

# Find T20 competitions excluding IPL
other_t20 = competitions_df[
    (competitions_df["match_format"] == "T20") &
    (~competitions_df["comp_name"].str.contains(
        "IPL", case=False, na=False
    ))
].copy()

print("\nOTHER T20 COMPETITIONS:")
print(
    other_t20[
        ["comp_id", "comp_name", "season"]
    ].to_string(index=False)
)

print("\nTotal other T20 competitions:", len(other_t20))

# Get unique shortlisted players
shortlisted_names = (
    final_recommendations["player_name"]
    .dropna()
    .unique()
)

# Filter player mapping
other_t20_mapping = mapping_df[
    mapping_df["comp_id"].isin(other_t20["comp_id"])
].copy()

# Add season using competition ID
other_t20_mapping = other_t20_mapping.merge(
    other_t20[["comp_id", "season"]],
    on="comp_id",
    how="left"
)

# Find shortlisted players
shortlisted_mapping = other_t20_mapping[
    other_t20_mapping["player_name"].isin(shortlisted_names)
]

print("\nSHORTLISTED PLAYERS FOUND:")

if shortlisted_mapping.empty:
    print("No exact-name matches found.")
else:
    print(
        shortlisted_mapping[
            ["player_name", "comp_name", "season", "team_name"]
        ]
        .drop_duplicates()
        .sort_values(["player_name", "season"])
        .to_string(index=False)
    )

print(
    "\nUnique shortlisted players found:",
    shortlisted_mapping["player_name"].nunique()
)

print("\n--- STEP 25B COMPLETED ---")

# ============================================================
# STEP 25C: VERIFY OTHER T20 BALL-BY-BALL DATA
# ============================================================

print("\n--- STEP 25C: BALL-BY-BALL DATA VERIFICATION ---")

matches_check = pd.read_csv("datapack/matches.csv")
balls_check = pd.read_csv("datapack/ball_by_ball.csv")

print("\nMATCHES COLUMNS:")
print(matches_check.columns.tolist())

print("\nBALL-BY-BALL COLUMNS:")
print(balls_check.columns.tolist())

print("\nMATCH DATA SAMPLE:")
print(matches_check.head(3).to_string(index=False))

# Find competition ID column
comp_columns = [
    col for col in matches_check.columns
    if "comp" in col.lower()
]

print("\nPOSSIBLE COMPETITION COLUMNS:", comp_columns)

print("\n--- STEP 25C COMPLETED ---")

# ============================================================
# STEP 25D: ACTUAL PERFORMANCE IN OTHER T20 COMPETITIONS
# ============================================================

print("\n--- STEP 25D: ACTUAL PLAYER PERFORMANCE ---")

# Get match IDs from the two other T20 competitions
other_match_ids = matches_check[
    matches_check["comp_id"].isin(other_t20["comp_id"])
][["match_id", "comp_id"]]

# Connect match IDs to ball-by-ball data
other_deliveries = balls_check.merge(
    other_match_ids,
    on="match_id",
    how="inner"
)

# Get shortlisted player IDs in these competitions
player_ids = shortlisted_mapping[
    ["player_id", "player_name", "comp_id", "comp_name"]
].drop_duplicates()

# Merge player information with competition deliveries
batting_data = other_deliveries.merge(
    player_ids,
    left_on=["striker_id", "comp_id"],
    right_on=["player_id", "comp_id"],
    how="inner"
)

bowling_data = other_deliveries.merge(
    player_ids,
    left_on=["bowler_id", "comp_id"],
    right_on=["player_id", "comp_id"],
    how="inner"
)

print("\nCOMPETITION DATA COVERAGE:")
print("Total matches:", len(other_match_ids))
print("Total ball-by-ball deliveries:", len(other_deliveries))

print("\nSHORTLISTED BATTER PERFORMANCE:")

if batting_data.empty:
    print("No batting deliveries found.")
else:
    batting_summary = batting_data.groupby(
        ["player_name", "comp_name"]
    ).agg(
        runs=("runs", "sum"),
        balls=("match_id", "count"),
        dismissals=("is_wicket", "sum"),
        matches=("match_id", "nunique")
    ).reset_index()

    batting_summary["strike_rate"] = (
        batting_summary["runs"] /
        batting_summary["balls"] * 100
    ).round(2)

    print(batting_summary.to_string(index=False))

print("\nSHORTLISTED BOWLER PERFORMANCE:")

if bowling_data.empty:
    print("No bowling deliveries found.")
else:
    bowling_summary = bowling_data.groupby(
        ["player_name", "comp_name"]
    ).agg(
        deliveries=("match_id", "count"),
        wickets=("is_wicket", "sum"),
        matches=("match_id", "nunique")
    ).reset_index()

    print(bowling_summary.to_string(index=False))

print("\n--- STEP 25D COMPLETED ---")

# ============================================================
# STEP 25E: COMPETITION FORMAT AUDIT
# ============================================================

print("\n--- STEP 25E: COMPETITION FORMAT AUDIT ---")

print("\nCOMPETITION COUNTS BY FORMAT:")
print(
    competitions_df["match_format"]
    .value_counts(dropna=False)
    .to_string()
)

print("\nNON-IPL T20 COMPETITIONS:")
print(
    competitions_df[
        (competitions_df["match_format"] == "T20") &
        (~competitions_df["comp_name"].str.contains(
            "IPL", case=False, na=False
        ))
    ][["comp_id", "comp_name", "season"]]
    .to_string(index=False)
)

print("\nALL COMPETITION NAMES CONTAINING LEAGUE:")
print(
    competitions_df[
        competitions_df["comp_name"].str.contains(
            "league|premier|big bash|hundred|super smash",
            case=False,
            na=False
        )
    ][["comp_id", "comp_name", "match_format", "season"]]
    .to_string(index=False)
)

print("\n--- STEP 25E COMPLETED ---")

# ==========================================
# STEP 26: EXPORT FINAL ANALYSIS TABLES
# ==========================================

print("\n--- STEP 26: EXPORTING FINAL ANALYSIS TABLES ---")

# 1. Export Top 10 Batters
final_batting.to_csv(
    "final_top_10_batters.csv",
    index=False
)

# 2. Export Top 10 Bowlers
final_bowling.to_csv(
    "final_top_10_bowlers.csv",
    index=False
)

# 3. Export Death-Over Pressure Analysis
death_bowlers.to_csv(
    "death_over_pressure_analysis.csv",
    index=False
)

# 4. Export Combined 20-Player Shortlist
final_recommendations.to_csv(
    "final_20_player_shortlist.csv",
    index=False
)

# 5. Export Additional Competition Mapping
shortlisted_mapping.to_csv(
    "additional_competition_mapping.csv",
    index=False
)

print("\nEXPORTED FILES:")

print("1. final_top_10_batters.csv")
print("2. final_top_10_bowlers.csv")
print("3. death_over_pressure_analysis.csv")
print("4. final_20_player_shortlist.csv")
print("5. additional_competition_mapping.csv")

print("\n--- STEP 26 COMPLETED ---")
print("All final analysis CSV files exported successfully.")

# ==========================================
# STEP 27: FINAL RANKING DATA INSPECTION
# ==========================================

print("\n--- STEP 27: FINAL RANKING DATA INSPECTION ---")

print("\nTOP 10 BATTERS:")
print(final_batting.to_string(index=False))

print("\nBATTER COLUMNS:")
print(final_batting.columns.tolist())

print("\nTOP 10 BOWLERS:")
print(final_bowling.to_string(index=False))

print("\nBOWLER COLUMNS:")
print(final_bowling.columns.tolist())

print("\nCOMBINED SHORTLIST COLUMNS:")
print(final_recommendations.columns.tolist())

print("\n--- STEP 27 COMPLETED ---")
print("\nBATTER COLUMNS:")
print(final_batting.columns.tolist())

print("\nBATTER SAMPLE:")
print(final_batting.head(3).to_string(index=False))

# ============================================================
# STEP 28: FINAL OVERALL TOP 10 RELIABLE PLAYERS
# CORRECTED SAMPLE-SIZE NORMALIZATION
# ============================================================

print("\n--- STEP 28: FINAL OVERALL TOP 10 ---")

# ------------------------------------------------------------
# PART A: PREPARE THE COMPLETE BATTING RANKING
# ------------------------------------------------------------

batting_pool = final_batting.copy()

batting_pool["player_name"] = batting_pool["striker_name"]
batting_pool["role"] = "Batter"

batting_pool["role_rank"] = batting_pool["final_rank"]

# Rank-based performance percentile
batting_pool["performance_percentile"] = (
    1 - (
        (batting_pool["final_rank"] - 1) /
        (len(batting_pool) - 1)
    )
) * 100

# Calculate sample-size percentile across ALL batters
batting_pool["sample_size"] = batting_pool["balls"]

batting_pool["sample_percentile"] = (
    batting_pool["sample_size"].rank(pct=True) * 100
)

# Select top 5 batters
top_batters = (
    batting_pool
    .sort_values("final_rank")
    .head(5)
    .copy()
)

# ------------------------------------------------------------
# PART B: PREPARE THE COMPLETE BOWLING RANKING
# ------------------------------------------------------------

bowling_pool = final_bowling.copy()

bowling_pool["player_name"] = bowling_pool["bowler_name"]
bowling_pool["role"] = "Bowler"

bowling_pool["role_rank"] = bowling_pool["final_rank"]

# Rank-based performance percentile
bowling_pool["performance_percentile"] = (
    1 - (
        (bowling_pool["final_rank"] - 1) /
        (len(bowling_pool) - 1)
    )
) * 100

# Calculate sample-size percentile across ALL bowlers
bowling_pool["sample_size"] = bowling_pool["legal_balls"]

bowling_pool["sample_percentile"] = (
    bowling_pool["sample_size"].rank(pct=True) * 100
)

# Select top 5 bowlers
top_bowlers = (
    bowling_pool
    .sort_values("final_rank")
    .head(5)
    .copy()
)

# ------------------------------------------------------------
# PART C: CALCULATE OVERALL SCORES
# ------------------------------------------------------------

top_batters["overall_score"] = (
    0.80 * top_batters["performance_percentile"] +
    0.20 * top_batters["sample_percentile"]
)

top_bowlers["overall_score"] = (
    0.80 * top_bowlers["performance_percentile"] +
    0.20 * top_bowlers["sample_percentile"]
)

# ------------------------------------------------------------
# PART D: COMBINE BOTH ROLES
# ------------------------------------------------------------

batting_final = top_batters[
    [
        "player_name",
        "role",
        "role_rank",
        "runs",
        "balls",
        "matches",
        "strike_rate",
        "final_score",
        "performance_percentile",
        "sample_size",
        "sample_percentile",
        "overall_score"
    ]
].copy()

bowling_final = top_bowlers[
    [
        "player_name",
        "role",
        "role_rank",
        "runs_conceded",
        "legal_balls",
        "wickets",
        "matches",
        "economy",
        "final_score",
        "performance_percentile",
        "sample_size",
        "sample_percentile",
        "overall_score"
    ]
].copy()

# Combine
final_overall_top10 = pd.concat(
    [batting_final, bowling_final],
    ignore_index=True,
    sort=False
)

# Sort overall ranking
final_overall_top10 = (
    final_overall_top10
    .sort_values(
        ["overall_score", "sample_size"],
        ascending=[False, False]
    )
    .reset_index(drop=True)
)

final_overall_top10["overall_rank"] = (
    final_overall_top10.index + 1
)

# ------------------------------------------------------------
# PART E: DISPLAY FINAL TOP 10
# ------------------------------------------------------------

print("\nFINAL TOP 10 RELIABLE PLAYERS UNDER PRESSURE")

print(
    final_overall_top10[
        [
            "overall_rank",
            "player_name",
            "role",
            "role_rank",
            "overall_score",
            "sample_size",
            "matches"
        ]
    ].round(2).to_string(index=False)
)

# ------------------------------------------------------------
# PART F: VALIDATION
# ------------------------------------------------------------

print("\nVALIDATION:")

print("Total selected players:", len(final_overall_top10))
print(
    "Batters:",
    (final_overall_top10["role"] == "Batter").sum()
)
print(
    "Bowlers:",
    (final_overall_top10["role"] == "Bowler").sum()
)
print(
    "Unique players:",
    final_overall_top10["player_name"].nunique()
)

# ------------------------------------------------------------
# PART G: EXPORT
# ------------------------------------------------------------

final_overall_top10.to_csv(
    "final_overall_top_10.csv",
    index=False
)

print("\nSaved: final_overall_top_10.csv")

print("\n--- STEP 28 COMPLETED ---")
# ============================================================
# STEP 29: FINAL OUTPUT FILE CHECK
# ============================================================

import os

print("\n--- STEP 29: FINAL OUTPUT FILE CHECK ---")

files_to_check = [
    "final_recommendations.csv",
    "final_overall_top_10.csv"
]

for file in files_to_check:
    if os.path.exists(file):
        print(f"{file} : SAVED")
        print("Rows:", len(pd.read_csv(file)))
    else:
        print(f"{file} : NOT FOUND")

print("\n--- STEP 29 COMPLETED ---")

# ============================================================
# STEP 30A: FINAL TOP 10 DATA VERIFICATION
# ============================================================

import pandas as pd

print("\n--- STEP 30A: FINAL TOP 10 VERIFICATION ---")

final_top10 = pd.read_csv("final_overall_top_10.csv")

print("\nFINAL TOP 10 PLAYERS:")
print(final_top10.to_string(index=False))

print("\nCHECK 1: TOTAL PLAYERS")
print("Total:", len(final_top10))

print("\nCHECK 2: UNIQUE PLAYER NAMES")
print("Unique:", final_top10["player_name"].nunique())

print("\nCHECK 3: MISSING VALUES")
print(final_top10.isnull().sum().to_string())

print("\nCHECK 4: ROLE DISTRIBUTION")
print(final_top10["role"].value_counts().to_string())

print("\nCHECK 5: SCORE ORDER")
print(
    "Descending:",
    final_top10["overall_score"].is_monotonic_decreasing
)

print("\nCHECK 6: SAMPLE SIZE")
print("Minimum sample:", final_top10["sample_size"].min())
print("Minimum matches:", final_top10["matches"].min())

print("\n--- STEP 30A COMPLETED ---")

# ============================================================
# STEP 30B: EXPORT CLEAN FINAL TOP 10
# ============================================================

print("\n--- STEP 30B: EXPORT CLEAN FINAL TOP 10 ---")

final_columns = [
    "overall_rank",
    "player_name",
    "role",
    "overall_score",
    "performance_percentile",
    "sample_size",
    "matches",
    "final_score",
    "runs",
    "balls",
    "strike_rate",
    "runs_conceded",
    "legal_balls",
    "wickets",
    "economy"
]

final_report = final_top10[final_columns].copy()

final_report = final_report.sort_values(
    "overall_rank"
)

final_report.to_csv(
    "FINAL_VERIFIED_TOP_10.csv",
    index=False
)

print("\nFINAL VERIFIED TOP 10:")
print(final_report.round(2).to_string(index=False))

print("\nSaved: FINAL_VERIFIED_TOP_10.csv")
print("\n--- STEP 30B COMPLETED ---")
# STEP 31: SAVE COMPLETE PLAYER RECOMMENDATIONS

final_recommendations.to_csv(
    "final_recommendations.csv",
    index=False
)

print("\nFINAL RECOMMENDATIONS SAVED:")
print(final_recommendations.to_string(index=False))

print("\n--- STEP 31 COMPLETED ---")
# STEP 31B: FULL PLAYER RANKING AUDIT

print("\n--- STEP 31B: FULL PLAYER RANKING AUDIT ---")

print("Total qualified batters:", len(batting_pool))
print("Total qualified bowlers:", len(bowling_pool))

print("\nTOP 10 BATTERS:")
print(
    batting_pool.sort_values("final_rank")
    .head(10)
    .to_string(index=False)
)

print("\nTOP 10 BOWLERS:")
print(
    bowling_pool.sort_values("final_rank")
    .head(10)
    .to_string(index=False)
)

print("\n--- STEP 31B COMPLETED ---")

# STEP 31C: MATCH RELEASED PLAYERS WITH FULL PERFORMANCE RANKINGS

print("\n--- STEP 31C: RELEASED PLAYER MATCHING ---")

released_players = {
    "Shimron Hetmyer": "RR",
    "Trent Boult": "MI",
    "Deepak Chahar": "MI",
    "Mitchell Starc": "DC",
    "Nitish Rana": "DC",
    "Abishek Porel": "DC",
    "Matheesha Pathirana": "KKR",
    "Rachin Ravindra": "KKR",
    "Rahul Tripathi": "KKR",
    "Avesh Khan": "LSG",
    "Anrich Nortje": "LSG",
    "Wanindu Hasaranga": "LSG",
    "Nehal Wadhera": "PBKS",
    "Lockie Ferguson": "PBKS",
    "Shahrukh Khan": "GT",
    "Ishant Sharma": "GT",
    "Jacob Bethell": "RCB",
    "Richard Gleeson": "RCB",
    "Travis Head": "SRH",
    "Gerald Coetzee": "SRH",
    "Matthew Short": "CSK",
    "Matt Henry": "CSK",
    "Akash Madhwal": "CSK"
}

# Normalise names for matching
def normalise_player_name(name):
    return str(name).strip().casefold()

released_names = {
    normalise_player_name(name): franchise
    for name, franchise in released_players.items()
}

# Match against complete batting ranking
batting_matches = batting_pool[
    batting_pool["player_name"].apply(
        lambda x: normalise_player_name(x) in released_names
    )
].copy()

batting_matches["previous_franchise"] = batting_matches[
    "player_name"
].apply(lambda x: released_names[normalise_player_name(x)])

batting_matches["matched_role"] = "Batter"

# Match against complete bowling ranking
bowling_matches = bowling_pool[
    bowling_pool["player_name"].apply(
        lambda x: normalise_player_name(x) in released_names
    )
].copy()

bowling_matches["previous_franchise"] = bowling_matches[
    "player_name"
].apply(lambda x: released_names[normalise_player_name(x)])

bowling_matches["matched_role"] = "Bowler"

# Combine both matching results
released_matches = pd.concat(
    [batting_matches, bowling_matches],
    ignore_index=True,
    sort=False
)

# Find released players not present in either ranking
matched_names = set(
    released_matches["player_name"].apply(normalise_player_name)
)

unmatched_players = [
    name for name in released_players
    if normalise_player_name(name) not in matched_names
]

# Display results
print("\nRELEASED PLAYERS MATCHED WITH OUR DATA:")

if not released_matches.empty:
    display_columns = [
        col for col in [
            "player_name",
            "matched_role",
            "previous_franchise",
            "final_score",
            "final_rank",
            "matches",
            "sample_size"
        ]
        if col in released_matches.columns
    ]

    print(
        released_matches[display_columns]
        .sort_values("final_score", ascending=False)
        .to_string(index=False)
    )
else:
    print("No released players matched.")

print("\nMATCHED PLAYER COUNT:", len(matched_names))

print("\nRELEASED PLAYERS NOT FOUND IN OUR DATA:")
for player in unmatched_players:
    print(player)

print("\nUNMATCHED PLAYER COUNT:", len(unmatched_players))

# Save results
released_matches.to_csv(
    "STEP31C_RELEASED_PLAYER_MATCHING.csv",
    index=False
)

print("\nSaved: STEP31C_RELEASED_PLAYER_MATCHING.csv")
print("\n--- STEP 31C COMPLETED ---")

# STEP 32: AUDIT UNMATCHED RELEASED PLAYERS

print("\n--- STEP 32: UNMATCHED PLAYER DATA AUDIT ---")

unmatched_players = [
    "Trent Boult", "Deepak Chahar", "Mitchell Starc",
    "Avesh Khan", "Anrich Nortje", "Wanindu Hasaranga",
    "Lockie Ferguson", "Shahrukh Khan", "Ishant Sharma",
    "Jacob Bethell", "Richard Gleeson", "Gerald Coetzee",
    "Matthew Short", "Matt Henry", "Akash Madhwal"
]

# Collect all names from complete batting and bowling rankings
batting_names = (
    final_batting["striker_name"]
    .dropna().astype(str).str.strip().str.lower()
)

bowling_names = (
    final_bowling["bowler_name"]
    .dropna().astype(str).str.strip().str.lower()
)

print("\nPLAYER PRESENCE CHECK:")

for player in unmatched_players:
    name = player.strip().lower()

    in_batting = name in set(batting_names)
    in_bowling = name in set(bowling_names)

    print(
        f"{player:22} | "
        f"Batting: {in_batting} | "
        f"Bowling: {in_bowling}"
    )

print("\n--- STEP 32 COMPLETED ---")

# STEP 33: RELEASED PLAYER SHORTLIST

print("\n--- STEP 33: RELEASED PLAYER SHORTLIST ---")

# Load the matching results from Step 31C
released_matches = pd.read_csv(
    "STEP31C_RELEASED_PLAYER_MATCHING.csv"
)

# Sort candidates using the existing model score
released_shortlist = released_matches.sort_values(
    "final_score",
    ascending=False
).copy()

# Add transparent sample-size labels
released_shortlist["sample_quality"] = released_shortlist[
    "sample_size"
].apply(
    lambda x: (
        "Substantial sample" if x >= 200
        else "Limited sample"
    )
)

# Assign shortlist priority based on existing rank
released_shortlist["priority"] = range(
    1, len(released_shortlist) + 1
)

# Arrange final columns
released_shortlist = released_shortlist[
    [
        "priority",
        "player_name",
        "matched_role",
        "previous_franchise",
        "final_score",
        "final_rank",
        "matches",
        "sample_size",
        "sample_quality"
    ]
]

print("\nRANKED RELEASED PLAYER SHORTLIST:")
print(
    released_shortlist.round(2).to_string(index=False)
)

print("\nROLE DISTRIBUTION:")
print(
    released_shortlist["matched_role"].value_counts()
)

released_shortlist.to_csv(
    "STEP33_RELEASED_PLAYER_SHORTLIST.csv",
    index=False
)

print("\nSaved: STEP33_RELEASED_PLAYER_SHORTLIST.csv")
print("\n--- STEP 33 COMPLETED ---")

# STEP 34: OPTIMIZED FULL DATASET PLAYER SEARCH

print("\n--- STEP 34: OPTIMIZED PLAYER SEARCH ---")

unmatched_players = [
    "Trent Boult", "Deepak Chahar", "Mitchell Starc",
    "Avesh Khan", "Anrich Nortje", "Wanindu Hasaranga",
    "Lockie Ferguson", "Shahrukh Khan", "Ishant Sharma",
    "Jacob Bethell", "Richard Gleeson", "Gerald Coetzee",
    "Matthew Short", "Matt Henry", "Akash Madhwal"
]

target_names = {p.lower() for p in unmatched_players}
found_players = []

for df_name, df in list(globals().items()):

    if not isinstance(df, pd.DataFrame):
        continue

    name_columns = [
        col for col in df.columns
        if any(word in str(col).lower()
               for word in ["batter", "bowler", "player", "striker", "name"])
    ]

    for col in name_columns:
        names = set(
            df[col].dropna().astype(str).str.strip().str.lower()
        )

        matches = target_names.intersection(names)

        for player in matches:
            found_players.append({
                "player_name": player,
                "dataframe": df_name,
                "column": col
            })

if found_players:
    found_df = pd.DataFrame(found_players).drop_duplicates()
    print("\nPLAYERS FOUND:")
    print(found_df.to_string(index=False))
    found_df.to_csv("STEP34_PLAYERS_FOUND_IN_RAW_DATA.csv", index=False)
else:
    print("\nNo exact-name matches found in loaded dataframes.")

print("\n--- STEP 34 COMPLETED ---")

# STEP 35: PLAYER PIPELINE AUDIT

print("\n--- STEP 35: PLAYER PIPELINE AUDIT ---")

targets = [
    "Trent Boult", "Deepak Chahar", "Mitchell Starc",
    "Avesh Khan", "Anrich Nortje", "Wanindu Hasaranga",
    "Lockie Ferguson", "Shahrukh Khan", "Ishant Sharma",
    "Jacob Bethell", "Richard Gleeson", "Gerald Coetzee",
    "Matthew Short", "Matt Henry", "Akash Madhwal"
]

stages = {
    "season_data": ("season_data", [
        "striker_name", "non_striker_name", "bowler_name"
    ]),
    "qualified_seasons": ("qualified_seasons", ["bowler_name"]),
    "bowling_scoring_base": ("bowling_scoring_base", ["bowler_name"]),
    "consistency": ("consistency", ["bowler_name"]),
    "stable_players": ("stable_players", ["bowler_name"]),
    "death_bowlers": ("death_bowlers", ["bowler_name"]),
    "qualified_death_bowlers": ("qualified_death_bowlers", ["bowler_name"]),
    "final_bowling": ("final_bowling", ["bowler_name"]),
    "mapping_df": ("mapping_df", ["player_name"])
}

audit_rows = []

for player in targets:
    row = {"player_name": player}

    for stage, (df_name, columns) in stages.items():
        df = globals().get(df_name)

        found = False

        if isinstance(df, pd.DataFrame):
            for col in columns:
                if col in df.columns:
                    names = (
                        df[col].dropna().astype(str)
                        .str.strip().str.lower()
                    )

                    if player.lower() in set(names):
                        found = True
                        break

        row[stage] = "YES" if found else "NO"

    audit_rows.append(row)

audit_df = pd.DataFrame(audit_rows)

print(audit_df.to_string(index=False))

audit_df.to_csv(
    "STEP35_PLAYER_PIPELINE_AUDIT.csv",
    index=False
)

print("\nSaved: STEP35_PLAYER_PIPELINE_AUDIT.csv")
print("\n--- STEP 35 COMPLETED ---")

# STEP 36: INVESTIGATE BOWLING SHORTLIST EXCLUSIONS

print("\n--- STEP 36: BOWLING SHORTLIST EXCLUSION ANALYSIS ---")

players_to_check = [
    "Trent Boult",
    "Deepak Chahar",
    "Mitchell Starc",
    "Avesh Khan",
    "Anrich Nortje",
    "Wanindu Hasaranga",
    "Lockie Ferguson",
    "Ishant Sharma",
    "Gerald Coetzee",
    "Matthew Short",
    "Matt Henry",
    "Akash Madhwal",
    "Richard Gleeson"
]

for df_name in ["qualified_seasons", "bowling_scoring_base"]:
    df = globals().get(df_name)

    print(f"\n--- {df_name.upper()} ---")

    if df is None or "bowler_name" not in df.columns:
        print("DataFrame or bowler_name column not found.")
        continue

    result = df[
        df["bowler_name"].astype(str).str.strip().str.lower().isin(
            [p.lower() for p in players_to_check]
        )
    ]

    if result.empty:
        print("No matching records.")
    else:
        print(result.to_string(index=False))

print("\n--- STEP 36 COMPLETED ---")

# STEP 37: FINAL BOWLING QUALIFICATION AUDIT

print("\n--- STEP 37: FINAL BOWLING QUALIFICATION AUDIT ---")

players_to_check = [
    "Trent Boult",
    "Deepak Chahar",
    "Mitchell Starc",
    "Avesh Khan",
    "Anrich Nortje",
    "Wanindu Hasaranga",
    "Lockie Ferguson",
    "Ishant Sharma",
    "Gerald Coetzee",
    "Akash Madhwal"
]

for player in players_to_check:

    print(f"\nPLAYER: {player}")

    for df_name in ["qualified_seasons", "final_bowling"]:

        df = globals().get(df_name)

        if df is None or "bowler_name" not in df.columns:
            continue

        result = df[
            df["bowler_name"].astype(str).str.strip().str.lower()
            == player.lower()
        ]

        print(f"{df_name}: {len(result)} records")

        if not result.empty:
            print(result.to_string(index=False))

print("\n--- STEP 37 COMPLETED ---")

# STEP 39: CONSISTENCY SHORTLIST AUDIT

print("\n--- STEP 39: CONSISTENCY SHORTLIST AUDIT ---")

print("Total shortlisted bowlers:", len(shortlist_consistency))

print(
    shortlist_consistency[
        ["bowler_name"]
    ].to_string(index=False)
)

print("\n--- CHECKING OUR TARGET PLAYERS ---")

target_players = [
    "Trent Boult",
    "Deepak Chahar",
    "Mitchell Starc",
    "Avesh Khan",
    "Anrich Nortje",
    "Wanindu Hasaranga",
    "Lockie Ferguson",
    "Ishant Sharma",
    "Gerald Coetzee",
    "Akash Madhwal"
]

shortlisted_names = set(
    shortlist_consistency["bowler_name"]
    .astype(str).str.strip().str.lower()
)

for player in target_players:
    status = (
        "IN SHORTLIST"
        if player.lower() in shortlisted_names
        else "NOT IN SHORTLIST"
    )
    print(f"{player:22} {status}")

print("\n--- STEP 39 COMPLETED ---")

# ============================================================
# STEP 40: TARGET BOWLER DATASET TRACE
# ============================================================

print("\n--- STEP 40: TARGET BOWLER DATASET TRACE ---")

target_players = [
    "Trent Boult",
    "Deepak Chahar",
    "Mitchell Starc",
    "Avesh Khan",
    "Anrich Nortje",
    "Wanindu Hasaranga",
    "Lockie Ferguson",
    "Ishant Sharma",
    "Gerald Coetzee",
    "Akash Madhwal"
]

datasets_to_check = [
    "pressure_bowlers",
    "qualified_bowlers",
    "bowling_scoring_base",
    "qualified_seasons",
    "shortlist_consistency",
    "final_bowling"
]

for df_name in datasets_to_check:

    df = globals().get(df_name)

    print(f"\nDATASET: {df_name}")

    if df is None:
        print("Dataset not found")
        continue

    if "bowler_name" not in df.columns:
        print("No bowler_name column")
        continue

    for player in target_players:

        result = df[
            df["bowler_name"].astype(str).str.strip().str.lower()
            == player.lower()
        ]

        if not result.empty:
            print(f"{player}: {len(result)} records")

            useful_columns = [
                col for col in [
                    "bowler_name", "season", "legal_balls",
                    "wickets", "matches", "economy",
                    "runs_conceded"
                ]
                if col in result.columns
            ]

            print(result[useful_columns].to_string(index=False))

print("\n--- STEP 40 COMPLETED ---")
# ============================================================
# STEP 41: TARGET BOWLERS PRESSURE DATA AUDIT
# ============================================================

print("\n--- STEP 41: TARGET BOWLERS PRESSURE DATA AUDIT ---")

target_players = [
    "Trent Boult",
    "Deepak Chahar",
    "Mitchell Starc",
    "Avesh Khan",
    "Anrich Nortje",
    "Wanindu Hasaranga",
    "Lockie Ferguson",
    "Ishant Sharma",
    "Gerald Coetzee",
    "Akash Madhwal"
]

for df_name in ["pressure_bowlers", "qualified_bowlers",
                "bowling_scoring_base"]:

    df = globals().get(df_name)

    print(f"\nDATASET: {df_name}")

    if df is None:
        print("Not available")
        continue

    print("Total records:", len(df))

    if "bowler_name" not in df.columns:
        print("No bowler_name column")
        continue

    for player in target_players:

        result = df[
            df["bowler_name"].astype(str).str.strip().str.lower()
            == player.lower()
        ]

        if not result.empty:
            print(f"\n{player}")
            print(result.to_string(index=False))

print("\n--- STEP 41 COMPLETED ---")
