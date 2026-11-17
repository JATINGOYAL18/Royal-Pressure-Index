# 🏏 Royal Pressure Index
### Data-Driven Cricket Analytics for Rajasthan Royals – IPL 2027 Scouting

**Royal Pressure Index** is a cricket analytics project developed for the **SupeRR Selector Season 2 Hackathon**.

The project analyzes historical ball-by-ball cricket data to identify players who demonstrate reliability and performance under high-pressure match situations.

It uses pressure-based statistical metrics, player performance analysis, multiple ranking models, and validation techniques to generate data-driven scouting insights for Rajasthan Royals ahead of IPL 2027.

---

## 🎯 Project Objective

The objective is to identify players who can deliver when match situations become challenging.

Rather than evaluating players only through conventional statistics such as total runs, wickets, or strike rates, this project focuses on performance under pressure.

The analysis aims to identify:

- Reliable batters in high-pressure situations.
- Effective bowlers under pressure.
- Consistent performers across different seasons.
- Potential scouting targets for IPL 2027.

---

## 📊 Dataset Overview

The project uses the provided ball-by-ball cricket dataset.

| Metric | Records |
|---|---:|
| Total deliveries analyzed | 87,687 |
| High and very-high pressure deliveries | 22,276 |
| Batters evaluated | 341 |
| Bowlers evaluated | 260 |

**Core analysis period:** IPL 2022–2026.

Additional competition data was considered where reliable player and competition mapping was possible.

---

## ⚙️ Methodology

### 1. Pressure Identification

Deliveries are categorized according to match pressure levels.

The analysis focuses on high-pressure and very-high-pressure situations to evaluate how players perform in challenging match conditions.

### 2. Batting Pressure Index

The batting model evaluates players using the following weighted metrics:

| Metric | Weight |
|---|---:|
| Strike Rate | 40% |
| Runs per Dismissal / Survival | 30% |
| Run Volume | 20% |
| Reliability | 10% |
| **Total** | **100%** |

Minimum qualification filters:

- At least 60 pressure deliveries.
- At least 5 matches.

### 3. Bowling Pressure Index

The bowling model evaluates:

| Metric | Weight |
|---|---:|
| Economy Rate | 25% |
| Wickets per 100 Legal Balls | 30% |
| Dot-Ball Percentage | 20% |
| Boundary Control | 15% |
| Season Consistency | 10% |
| **Total** | **100%** |

Reliability adjustments are applied to account for differences in player sample sizes.

### 4. Death-Over Pressure Analysis

A separate analysis evaluates bowling performance during overs 16–20 under high and very-high pressure.

Metrics include:

- Wickets taken.
- Legal deliveries bowled.
- Economy rate.
- Dot-ball percentage.
- Boundary percentage.

### 5. Multiple Model Validation

Multiple alternative bowling models are compared to evaluate ranking stability.

| Model Comparison | Rank Correlation |
|---|---:|
| Balanced vs Wicket | 0.957 |
| Balanced vs Control | 0.959 |
| Wicket vs Control | 0.846 |

A consensus shortlist identifies players who repeatedly perform well across different model configurations.

---

## 🏆 Key Results

### Overall Top 10 Pressure Performers

| Rank | Player | Role | Score |
|---:|---|---|---:|
| 1 | Rashid Khan | Bowler | 98.67 |
| 2 | David Miller | Batter | 98.10 |
| 3 | Shreyas Iyer | Batter | 95.16 |
| 4 | Abhishek Sharma | Batter | 94.07 |
| 5 | Jos Buttler | Batter | 93.97 |
| 6 | Rinku Singh | Batter | 93.77 |
| 7 | Prasidh Krishna | Bowler | 83.24 |
| 8 | Mohit Sharma | Bowler | 82.29 |
| 9 | Sunil Narine | Bowler | 78.86 |
| 10 | Jasprit Bumrah | Bowler | 66.48 |

*These scores represent the overall historical pressure-performance ranking. They are different from the separate batting and bowling model scores.*

---

## 📁 Project Structure

```text
Royal-Pressure-Index/
│
├── README.md
├── requirements.txt
├── .gitignore
│
├── analysis.py
│
├── datapack/
│   ├── ball_by_ball.csv
│   ├── competitions.csv
│   ├── competition_team_player_mapping.csv
│   ├── matches.csv
│   ├── playing_eleven.csv
│   └── teams.csv
│
├── FINAL_VERIFIED_TOP_10.csv
├── final_overall_top_10.csv
├── final_recommendations.csv
├── final_top_10_batters.csv
├── final_top_10_bowlers.csv
├── final_20_player_shortlist.csv
│
├── death_over_pressure_analysis.csv
├── additional_competition_mapping.csv
│
├── STEP31C_RELEASED_PLAYER_MATCHING.csv
├── STEP33_RELEASED_PLAYER_SHORTLIST.csv
├── STEP34_PLAYERS_FOUND_IN_RAW_DATA.csv
├── STEP35_PLAYER_PIPELINE_AUDIT.csv
│
├── Royal_Pressure_Index_Final.pdf
└── Royal_Pressure_Index_Final.pptx
```

---

## 🛠️ Technologies Used

- **Python** – Core programming language.
- **Pandas** – Data manipulation and analysis.
- **Statistical Analysis** – Pressure-based performance evaluation.
- **Data Processing** – Cleaning, filtering, and validating cricket data.
- **Multiple Ranking Models** – Comparing player performance under different model configurations.

---

## 🚀 How to Run the Project

### 1. Clone the repository

```bash
git clone https://github.com/JATINGOYAL18/Royal-Pressure-Index.git
```

### 2. Navigate to the project directory

```bash
cd Royal-Pressure-Index
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the analysis

```bash
python analysis.py
```

**Important:** Run the script from the project root directory. The required input dataset files must be available in the expected `datapack/` directory.

---

## 📄 Project Deliverables

The final project presentation and report are available here:

- [View Final PDF Report](Royal_Pressure_Index_Final.pdf)
- [View Final PowerPoint Presentation](Royal_Pressure_Index_Final.pptx)
- [View Verified Overall Top 10](FINAL_VERIFIED_TOP_10.csv)
- [View Final Recommendations](final_recommendations.csv)

---

## ⚠️ Limitations

- Historical performance does not guarantee future performance.
- Player sample sizes vary and can influence rankings.
- Pressure-based rankings should be considered alongside player roles, team requirements, fitness, and auction strategy.
- The dataset does not represent every domestic T20 competition.
- Historical player rankings do not confirm IPL 2027 auction participation or availability.

---

## 📌 Important Note

Royal Pressure Index is an independent data analytics project developed for the SupeRR Selector Season 2 Hackathon.

It provides analytical scouting insights and is not an official Rajasthan Royals selection or auction recommendation.

---

## 👨‍💻 Project Information

| Detail | Information |
|---|---|
| Project | Royal Pressure Index |
| Hackathon | SupeRR Selector Season 2 |
| Focus | Cricket Analytics, Data Science, Player Performance Under Pressure |
| Language | Python |
| GitHub | [JATINGOYAL18/Royal-Pressure-Index](https://github.com/JATINGOYAL18/Royal-Pressure-Index) |

**Built with Python and data-driven cricket analysis.**
