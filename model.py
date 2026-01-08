import json
from dataclasses import dataclass
from typing import List, Dict, Tuple

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.decomposition import PCA
from sklearn.neighbors import NearestNeighbors


# --------------------------------
# Data structures
# --------------------------------

@dataclass
class Player:
    name: str
    team: str
    country: str
    role: str  # "batter", "bowler", "allrounder", "keeper"
    description: str
    bat_rating: float  # 0–1 T20 batting strength (base prior)
    bowl_rating: float  # 0–1 T20 bowling strength (base prior)
    overseas: bool


# --------------------------------
# Load and preprocess performance data from CSV
# --------------------------------

CSV_PATH = "data.csv"  # renamed from ipl-1.csv


def load_raw_data() -> pd.DataFrame:
    df = pd.read_csv(CSV_PATH)
    df = df.copy()

    if "Player" not in df.columns:
        df["Player"] = np.nan

    # Recover player names where CSV shifted columns
    def fix_player(row):
        if isinstance(row.get("Player", np.nan), str) and row["Player"] != "":
            return row["Player"]
        if isinstance(row.get("Matches", np.nan), str):
            return row["Matches"]
        return row.get("Player", np.nan)

    df["Player"] = df.apply(fix_player, axis=1)

    num_cols = [
        "Matches",
        "Inns",
        "Overs",
        "Balls",
        "Wkts",
        "Avg",
        "Runs",
        "RunsScored",
        "SR",
        "4-Fers",
        "5-Fers",
        "Rating",
        "CareerBestRating",
    ]
    for c in num_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    return df


def build_feature_matrices(df: pd.DataFrame):
    is_bat = df["Category"] == "TournamentBatting"
    is_bowl = df["Category"] == "TournamentBowling"
    is_icc_bat = df["Category"] == "ICC_Batting"
    is_icc_bowl = df["Category"] == "ICC_Bowling"

    def is_ipl(t):
        return isinstance(t, str) and "Indian Premier League" in t

    def is_smat(t):
        return isinstance(t, str) and "Syed Mushtaq Ali Trophy" in t

    def is_bbl(t):
        return isinstance(t, str) and "Big Bash League" in t

    # Batting features
    bat_df = df[is_bat].copy()
    bat_df["is_ipl"] = bat_df["Tournament"].apply(is_ipl)
    bat_df["is_smat"] = bat_df["Tournament"].apply(is_smat)
    bat_df["is_bbl"] = bat_df["Tournament"].apply(is_bbl)

    agg_bat = bat_df.groupby("Player").agg(
        ipl_runs=("Runs", lambda x: x[bat_df.loc[x.index, "is_ipl"]].sum()),
        smat_runs=("Runs", lambda x: x[bat_df.loc[x.index, "is_smat"]].sum()),
        bbl_runs=("Runs", lambda x: x[bat_df.loc[x.index, "is_bbl"]].sum()),
        ipl_inns=("Inns", lambda x: x[bat_df.loc[x.index, "is_ipl"]].sum()),
        smat_inns=("Inns", lambda x: x[bat_df.loc[x.index, "is_smat"]].sum()),
        bbl_inns=("Inns", lambda x: x[bat_df.loc[x.index, "is_bbl"]].sum()),
    )

    icc_bat = df[is_icc_bat].copy()
    icc_bat_agg = icc_bat.groupby("Player").agg(
        icc_bat_rating=("Rating", "max")
    )

    # Bowling features
    bowl_df = df[is_bowl].copy()
    bowl_df["is_ipl"] = bowl_df["Tournament"].apply(is_ipl)
    bowl_df["is_smat"] = bowl_df["Tournament"].apply(is_smat)
    bowl_df["is_bbl"] = bowl_df["Tournament"].apply(is_bbl)

    agg_bowl = bowl_df.groupby("Player").agg(
        ipl_wkts=("Wkts", lambda x: x[bowl_df.loc[x.index, "is_ipl"]].sum()),
        smat_wkts=("Wkts", lambda x: x[bowl_df.loc[x.index, "is_smat"]].sum()),
        bbl_wkts=("Wkts", lambda x: x[bowl_df.loc[x.index, "is_bbl"]].sum()),
        ipl_overs=("Overs", lambda x: x[bowl_df.loc[x.index, "is_ipl"]].sum()),
        smat_overs=("Overs", lambda x: x[bowl_df.loc[x.index, "is_smat"]].sum()),
        bbl_overs=("Overs", lambda x: x[bowl_df.loc[x.index, "is_bbl"]].sum()),
    )

    icc_bowl = df[is_icc_bowl].copy()
    icc_bowl_agg = icc_bowl.groupby("Player").agg(
        icc_bowl_rating=("Rating", "max")
    )

    bat_features = agg_bat.join(icc_bat_agg, how="outer").fillna(0)
    bowl_features = agg_bowl.join(icc_bowl_agg, how="outer").fillna(0)

    # Weights: IPL (3 yrs) > ICC > SMAT 2025 > BBL 2025
    weights_bat = {
        "ipl_runs": 0.4,
        "icc_bat_rating": 0.3,
        "smat_runs": 0.2,
        "bbl_runs": 0.1,
    }

    weights_bowl = {
        "ipl_wkts": 0.4,
        "icc_bowl_rating": 0.3,
        "smat_wkts": 0.2,
        "bbl_wkts": 0.1,
    }

    def build_score_matrix(df_feat: pd.DataFrame, weights: Dict[str, float]) -> Tuple[pd.DataFrame, np.ndarray]:
        cols = list(weights.keys())
        present_cols = [c for c in cols if c in df_feat.columns]
        X = df_feat[present_cols].values.astype(float)
        if X.size == 0:
            return df_feat.assign(score=0.0), np.zeros((df_feat.shape[0], 1))

        scaler = MinMaxScaler()
        X_scaled = scaler.fit_transform(X)
        w = np.array([weights[c] for c in present_cols]).reshape(1, -1)
        scores = (X_scaled * w).sum(axis=1)
        df_feat = df_feat.copy()
        df_feat["score"] = scores
        return df_feat, X_scaled

    bat_feat_scored, bat_X = build_score_matrix(bat_features, weights_bat)
    bowl_feat_scored, bowl_X = build_score_matrix(bowl_features, weights_bowl)

    def embed(X: np.ndarray) -> np.ndarray:
        if X.shape[0] < 3:
            return X
        n_components = min(3, X.shape[1])
        pca = PCA(n_components=n_components)
        return pca.fit_transform(X)

    bat_emb = embed(bat_X)
    bowl_emb = embed(bowl_X)

    return bat_feat_scored, bat_emb, bowl_feat_scored, bowl_emb


# --------------------------------
# Base prior ratings (your original ratings)
# --------------------------------

BAT_FORM = {
    "Abhishek Sharma": 0.94,
    "Vaibhav Suryavanshi": 0.9,
    "Shubman Gill": 0.93,
    "Nicholas Pooran": 0.93,
    "Suryakumar Yadav": 0.96,
    "Virat Kohli": 0.96,
    "Yashasvi Jaiswal": 0.94,
    "Ishan Kishan": 0.9,
    "Sai Sudharsan": 0.95,
    "Travis Head": 0.93,
    "Shreyas Iyer": 0.9,
    "Rohit Sharma": 0.88,
    "Mitchell Marsh": 0.9,
    "Ruturaj Gaikwad": 0.88,
    "Jos Buttler": 0.95,
    "Priyansh Arya": 0.82,
    "Dhruv Jurel": 0.87,
    "Shimron Hetmyer": 0.88,
    "Rinku Singh": 0.9,
    "Shashank Singh": 0.9,
}

BOWL_FORM = {
    "Jasprit Bumrah": 0.97,
    "Mohammed Siraj": 0.93,
    "Yuzvendra Chahal": 0.93,
    "Harshal Patel": 0.9,
    "Rashid Khan": 0.96,
    "Prasidh Krishna": 0.92,
    "Arshdeep Singh": 0.9,
    "Kuldeep Yadav": 0.92,
    "Josh Hazlewood": 0.92,
    "Bhuvneshwar Kumar": 0.9,
    "Noor Ahmad": 0.9,
    "Varun Chakravarthy": 0.9,
    "Pat Cummins": 0.9,
    "Mayank Yadav": 0.9,
    "Mitchell Starc": 0.93,
    "Mohammed Shami": 0.9,
}


def br(name: str, base: float = 0.7) -> float:
    return BAT_FORM.get(name, base)


def bw(name: str, base: float = 0.7) -> float:
    return BOWL_FORM.get(name, base)


# --------------------------------
# Squads: playing XII unchanged
# --------------------------------

def build_best12() -> Dict[str, Dict]:
    teams: Dict[str, Dict] = {}

    def P(name, team, country, role, desc, bat, bowl):
        return Player(
            name=name,
            team=team,
            country=country,
            role=role,
            description=desc,
            bat_rating=bat,
            bowl_rating=bowl,
            overseas=(country != "India"),
        )

    # ---- CSK XII ----
    csk_xi = [
        P("Ruturaj Gaikwad", "CSK", "India", "batter", "Opener (captain)", br("Ruturaj Gaikwad", 0.88), 0.3),
        P("Sanju Samson", "CSK", "India", "batter", "Top-order", br("Sanju Samson", 0.9), 0.3),
        P("Dewald Brevis", "CSK", "SA", "batter", "Top-order aggressor", br("Dewald Brevis", 0.85), 0.3),
        P("MS Dhoni", "CSK", "India", "keeper", "Wicketkeeper finisher", br("MS Dhoni", 0.8), 0.3),
        P("Shivam Dube", "CSK", "India", "allrounder", "Middle-order power-hitter", br("Shivam Dube", 0.9), 0.6),
        P("Prashant Veer", "CSK", "India", "allrounder", "Batting all-rounder", 0.78, 0.7),
        P("Kartik Sharma", "CSK", "India", "keeper", "Reserve keeper-batter", 0.72, 0.3),
        P("Akeal Hosein", "CSK", "WI", "bowler", "Left-arm spinner", 0.6, bw("Akeal Hosein", 0.8)),
        P("Nathan Ellis", "CSK", "AUS", "bowler", "Death-overs seamer", 0.45, bw("Nathan Ellis", 0.83)),
        P("Rahul Chahar", "CSK", "India", "bowler", "Leg-spinner", 0.4, bw("Rahul Chahar", 0.82)),
        P("Khaleel Ahmed", "CSK", "India", "bowler", "Left-arm seamer", 0.35, bw("Khaleel Ahmed", 0.8)),
    ]
    csk_imp = P("Noor Ahmad", "CSK", "AFG", "bowler", "Impact wrist-spinner", 0.35, bw("Noor Ahmad", 0.9))
    teams["CSK"] = {"xi": csk_xi, "impact": csk_imp}

    # ---- RCB XII ----
    rcb_xi = [
        P("Virat Kohli", "RCB", "India", "batter", "Top-order", br("Virat Kohli", 0.96), 0.3),
        P("Phil Salt", "RCB", "ENG", "keeper", "Aggressive opener (wk)", br("Phil Salt", 0.9), 0.3),
        P("Venkatesh Iyer", "RCB", "India", "allrounder", "Top-order all-rounder", 0.82, 0.6),
        P("Rajat Patidar", "RCB", "India", "batter", "Top-order (captain)", 0.84, 0.3),
        P("Jitesh Sharma", "RCB", "India", "keeper", "Middle-order finisher", 0.84, 0.3),
        P("Tim David", "RCB", "AUS", "allrounder", "Power finisher", 0.86, 0.55),
        P("Romario Shepherd", "RCB", "WI", "allrounder", "Pace all-rounder", 0.8, 0.7),
        P("Krunal Pandya", "RCB", "India", "allrounder", "Spin all-rounder", 0.78, 0.8),
        P("Bhuvneshwar Kumar", "RCB", "India", "bowler", "Swing bowler", 0.35, bw("Bhuvneshwar Kumar", 0.9)),
        P("Suyash Sharma", "RCB", "India", "bowler", "Leg-spinner", 0.35, 0.8),
        P("Josh Hazlewood", "RCB", "AUS", "bowler", "Strike seamer", 0.35, bw("Josh Hazlewood", 0.92)),
    ]
    rcb_imp = P("Yash Dayal", "RCB", "India", "bowler", "Impact left-arm seamer", 0.35, bw("Yash Dayal", 0.9))
    teams["RCB"] = {"xi": rcb_xi, "impact": rcb_imp}

    # ---- KKR XII ----
    kkr_xi = [
        P("Finn Allen", "KKR", "NZ", "keeper", "Opener (wk)", 0.86, 0.3),
        P("Ajinkya Rahane", "KKR", "India", "batter", "Top-order (captain)", 0.8, 0.3),
        P("Angkrish Raghuvanshi", "KKR", "India", "batter", "Top-order", 0.8, 0.3),
        P("Cameron Green", "KKR", "AUS", "allrounder", "Batting all-rounder", 0.87, 0.78),
        P("Rahul Tripathi", "KKR", "India", "batter", "Top-order", 0.82, 0.3),
        P("Rinku Singh", "KKR", "India", "batter", "Finisher", br("Rinku Singh", 0.9), 0.3),
        P("Ramandeep Singh", "KKR", "India", "batter", "Middle-order", 0.8, 0.3),
        P("Sunil Narine", "KKR", "WI", "allrounder", "Mystery spin all-rounder", 0.78, 0.9),
        P("Harshit Rana", "KKR", "India", "bowler", "Pacer", 0.35, 0.78),
        P("Vaibhav Arora", "KKR", "India", "bowler", "Seamer", 0.35, 0.75),
        P("Matheesha Pathirana", "KKR", "SL", "bowler", "Death-overs quick", 0.35, 0.9),
    ]
    kkr_imp = P("Varun Chakravarthy", "KKR", "India", "bowler", "Impact mystery spinner", 0.35, bw("Varun Chakravarthy", 0.9))
    teams["KKR"] = {"xi": kkr_xi, "impact": kkr_imp}

    # ---- LSG XII ----
    lsg_xi = [
        P("Mitchell Marsh", "LSG", "AUS", "allrounder", "Top-order power-hitter", br("Mitchell Marsh", 0.9), 0.6),
        P("Aiden Markram", "LSG", "SA", "batter", "Top-order", 0.86, 0.35),
        P("Nicholas Pooran", "LSG", "WI", "keeper", "Middle-order (wk)", br("Nicholas Pooran", 0.93), 0.35),
        P("Rishabh Pant", "LSG", "India", "keeper", "Top-order (captain & wk)", br("Rishabh Pant", 0.92), 0.35),
        P("Ayush Badoni", "LSG", "India", "allrounder", "Middle-order all-rounder", 0.8, 0.7),
        P("Abdul Samad", "LSG", "India", "batter", "Finisher", 0.82, 0.3),
        P("Wanindu Hasaranga", "LSG", "SL", "allrounder", "Leg-spin all-rounder", 0.84, 0.92),
        P("Shahbaz Ahmed", "LSG", "India", "allrounder", "Spin all-rounder", 0.78, 0.8),
        P("Avesh Khan", "LSG", "India", "bowler", "Pace bowler", 0.35, 0.82),
        P("Mohammed Shami", "LSG", "India", "bowler", "Strike quick", 0.35, bw("Mohammed Shami", 0.9)),
        P("Mayank Yadav", "LSG", "India", "bowler", "Extreme pace", 0.35, bw("Mayank Yadav", 0.9)),
    ]
    lsg_imp = P("Mohsin Khan", "LSG", "India", "bowler", "Impact left-arm seamer", 0.35, 0.8)
    teams["LSG"] = {"xi": lsg_xi, "impact": lsg_imp}

    # ---- DC XII ----
    dc_xi = [
        P("KL Rahul", "DC", "India", "keeper", "Top-order (wk)", br("KL Rahul", 0.9), 0.3),
        P("Ben Duckett", "DC", "ENG", "keeper", "Top-order", 0.86, 0.3),
        P("Nitish Rana", "DC", "India", "batter", "Top-order", 0.86, 0.3),
        P("Tristan Stubbs", "DC", "SA", "batter", "Middle-order finisher", 0.88, 0.35),
        P("Axar Patel", "DC", "India", "allrounder", "Spin all-rounder (captain)", 0.8, 0.86),
        P("David Miller", "DC", "SA", "batter", "Finisher", 0.88, 0.3),
        P("Ashutosh Sharma", "DC", "India", "batter", "Finisher", 0.84, 0.3),
        P("Vipraj Nigam", "DC", "India", "allrounder", "All-rounder", 0.76, 0.76),
        P("Auqib Nabi", "DC", "India", "allrounder", "Seam all-rounder", 0.76, 0.8),
        P("Kuldeep Yadav", "DC", "India", "bowler", "Chinaman spinner", 0.35, bw("Kuldeep Yadav", 0.92)),
        P("Mitchell Starc", "DC", "AUS", "bowler", "Left-arm quick", 0.35, bw("Mitchell Starc", 0.93)),
    ]
    dc_imp = P("T. Natarajan", "DC", "India", "bowler", "Impact yorker specialist", 0.35, 0.88)
    teams["DC"] = {"xi": dc_xi, "impact": dc_imp}

    # ---- SRH XII ----
    srh_xi = [
        P("Travis Head", "SRH", "AUS", "batter", "Aggressive opener", br("Travis Head", 0.93), 0.35),
        P("Abhishek Sharma", "SRH", "India", "allrounder", "Top-order all-rounder", br("Abhishek Sharma", 0.94), 0.75),
        P("Ishan Kishan", "SRH", "India", "keeper", "Top-order keeper", br("Ishan Kishan", 0.9), 0.35),
        P("Nitish Kumar Reddy", "SRH", "India", "allrounder", "Middle-order all-rounder", 0.82, 0.8),
        P("Heinrich Klaasen", "SRH", "SA", "keeper", "Middle-order (wk)", 0.93, 0.35),
        P("Aniket Verma", "SRH", "India", "batter", "Middle-order", 0.8, 0.3),
        P("Liam Livingstone", "SRH", "ENG", "allrounder", "Batting all-rounder", 0.9, 0.72),
        P("Pat Cummins", "SRH", "AUS", "bowler", "Captain fast bowler", 0.4, bw("Pat Cummins", 0.9)),
        P("Harshal Patel", "SRH", "India", "allrounder", "Death-overs seamer", 0.7, bw("Harshal Patel", 0.9)),
        P("Shivam Mavi", "SRH", "India", "bowler", "Pacer", 0.4, 0.8),
        P("Jaydev Unadkat", "SRH", "India", "bowler", "Left-arm seamer", 0.4, 0.78),
    ]
    srh_imp = P("Zeeshan Ansari", "SRH", "India", "bowler", "Impact spinner", 0.35, 0.78)
    teams["SRH"] = {"xi": srh_xi, "impact": srh_imp}

    # ---- GT XII ----
    gt_xi = [
        P("Shubman Gill", "GT", "India", "batter", "Opener (captain)", br("Shubman Gill", 0.93), 0.35),
        P("Sai Sudharsan", "GT", "India", "batter", "Top-order", br("Sai Sudharsan", 0.95), 0.35),
        P("Jos Buttler", "GT", "ENG", "keeper", "Aggressive opener (wk)", br("Jos Buttler", 0.95), 0.35),
        P("Washington Sundar", "GT", "India", "allrounder", "Spin all-rounder", 0.8, 0.82),
        P("Shahrukh Khan", "GT", "India", "batter", "Finisher", 0.84, 0.3),
        P("Glenn Phillips", "GT", "NZ", "allrounder", "Middle-order all-rounder", 0.86, 0.78),
        P("Rahul Tewatia", "GT", "India", "allrounder", "Finisher all-rounder", 0.82, 0.76),
        P("Rashid Khan", "GT", "AFG", "bowler", "World-class spinner", 0.4, bw("Rashid Khan", 0.96)),
        P("Sai Kishore", "GT", "India", "bowler", "Left-arm spinner", 0.35, 0.86),
        P("Kagiso Rabada", "GT", "SA", "bowler", "Strike quick", 0.35, 0.92),
        P("Prasidh Krishna", "GT", "India", "bowler", "Hit-the-deck quick", 0.35, bw("Prasidh Krishna", 0.92)),
    ]
    gt_imp = P("Mohammed Siraj", "GT", "India", "bowler", "Impact fast bowler", 0.35, bw("Mohammed Siraj", 0.93))
    teams["GT"] = {"xi": gt_xi, "impact": gt_imp}

    # ---- PBKS XII ----
    pbks_xi = [
        P("Priyansh Arya", "PBKS", "India", "allrounder", "Top-order all-rounder", br("Priyansh Arya", 0.82), 0.7),
        P("Prabhsimran Singh", "PBKS", "India", "keeper", "Aggressive opener (wk)", 0.84, 0.3),
        P("Shreyas Iyer", "PBKS", "India", "batter", "Top-order (captain)", br("Shreyas Iyer", 0.9), 0.3),
        P("Nehal Wadhera", "PBKS", "India", "batter", "Middle-order", 0.8, 0.3),
        P("Mitch Owen", "PBKS", "AUS", "allrounder", "Batting all-rounder", 0.8, 0.74),
        P("Marcus Stoinis", "PBKS", "AUS", "allrounder", "Pace all-rounder", 0.86, 0.8),
        P("Shashank Singh", "PBKS", "India", "batter", "Finisher", br("Shashank Singh", 0.9), 0.3),
        P("Marco Jansen", "PBKS", "SA", "allrounder", "Tall seamer", 0.78, 0.82),
        P("Harpreet Brar", "PBKS", "India", "allrounder", "Spin all-rounder", 0.78, 0.82),
        P("Arshdeep Singh", "PBKS", "India", "bowler", "Left-arm seamer", 0.35, bw("Arshdeep Singh", 0.9)),
        P("Lockie Ferguson", "PBKS", "NZ", "bowler", "Fast bowler", 0.35, 0.88),
    ]
    pbks_imp = P("Yuzvendra Chahal", "PBKS", "India", "bowler", "Impact leg-spinner", 0.35, bw("Yuzvendra Chahal", 0.93))
    teams["PBKS"] = {"xi": pbks_xi, "impact": pbks_imp}

    # ---- RR XII ----
    rr_xi = [
        P("Yashasvi Jaiswal", "RR", "India", "batter", "Aggressive opener", br("Yashasvi Jaiswal", 0.94), 0.35),
        P("Vaibhav Suryavanshi", "RR", "India", "batter", "Top-order", br("Vaibhav Suryavanshi", 0.9), 0.3),
        P("Lhuan-dre Pretorius", "RR", "SA", "batter", "Top-order", 0.84, 0.3),
        P("Riyan Parag", "RR", "India", "batter", "Middle-order (captain)", 0.88, 0.4),
        P("Dhruv Jurel", "RR", "India", "keeper", "Middle-order (wk)", br("Dhruv Jurel", 0.87), 0.3),
        P("Shimron Hetmyer", "RR", "WI", "batter", "Finisher", 0.88, 0.3),
        P("Ravindra Jadeja", "RR", "India", "allrounder", "World-class all-rounder", 0.9, 0.9),
        P("Sam Curran", "RR", "ENG", "allrounder", "Pace all-rounder", 0.86, 0.82),
        P("Jofra Archer", "RR", "ENG", "bowler", "Fast bowler", 0.35, 0.9),
        P("Ravi Bishnoi", "RR", "India", "bowler", "Leg-spinner", 0.35, bw("Ravi Bishnoi", 0.9)),
        P("Tushar Deshpande", "RR", "India", "bowler", "Seamer", 0.35, 0.82),
    ]
    rr_imp = P("Sandeep Sharma", "RR", "India", "bowler", "Impact swing bowler", 0.35, 0.82)
    teams["RR"] = {"xi": rr_xi, "impact": rr_imp}

    # ---- MI XII ----
    mi_xi = [
        P("Rohit Sharma", "MI", "India", "batter", "Opener", br("Rohit Sharma", 0.88), 0.3),
        P("Quinton De Kock", "MI", "SA", "keeper", "Top-order (wk)", 0.86, 0.3),
        P("Suryakumar Yadav", "MI", "India", "batter", "Middle-order", br("Suryakumar Yadav", 0.96), 0.3),
        P("Tilak Varma", "MI", "India", "batter", "Middle-order", 0.9, 0.3),
        P("Hardik Pandya", "MI", "India", "allrounder", "Seam all-rounder (captain)", 0.9, 0.86),
        P("Naman Dhir", "MI", "India", "allrounder", "Batting all-rounder", 0.8, 0.7),
        P("Mitchell Santner", "MI", "NZ", "allrounder", "Spin all-rounder", 0.8, 0.82),
        P("Deepak Chahar", "MI", "India", "bowler", "New-ball seamer", 0.35, 0.82),
        P("Trent Boult", "MI", "NZ", "bowler", "Left-arm swing", 0.35, 0.9),
        P("Jasprit Bumrah", "MI", "India", "bowler", "Strike quick", 0.35, bw("Jasprit Bumrah", 0.97)),
        P("Mayank Markande", "MI", "India", "bowler", "Leg-spinner", 0.35, 0.82),
    ]
    mi_imp = P("Sherfane Rutherford", "MI", "WI", "batter", "Impact finisher", 0.86, 0.55)
    teams["MI"] = {"xi": mi_xi, "impact": mi_imp}

    return teams


# --------------------------------
# ML-enhanced scoring
# --------------------------------

def selection_score(p: Player) -> float:
    if p.role == "batter":
        base = p.bat_rating
    elif p.role == "bowler":
        base = p.bowl_rating
    elif p.role == "keeper":
        base = 0.8 * p.bat_rating + 0.2 * p.bowl_rating
    else:
        base = 0.55 * p.bat_rating + 0.45 * p.bowl_rating
    overseas_penalty = 0.02 if p.overseas else 0.0
    return max(0.0, min(1.0, base - overseas_penalty))


def build_player_score_lookup(bat_feat, bowl_feat) -> Tuple[Dict[str, float], Dict[str, float]]:
    bat_scores = bat_feat["score"].to_dict()
    bowl_scores = bowl_feat["score"].to_dict()
    return bat_scores, bowl_scores


def merge_prior_and_data(prior: float, data_score: float, alpha: float = 0.6) -> float:
    if np.isnan(data_score):
        return prior
    x = data_score
    x_norm = 1.0 / (1.0 + np.exp(-x))
    return float(alpha * prior + (1 - alpha) * x_norm)


def batting_projection_score(p: Player, bat_data_scores: Dict[str, float]) -> float:
    prior = p.bat_rating
    data_score = bat_data_scores.get(p.name, 0.0)
    merged = merge_prior_and_data(prior, data_score, alpha=0.55)
    factor = {"batter": 1.0, "keeper": 0.95, "allrounder": 0.8, "bowler": 0.3}.get(p.role, 0.7)
    return merged * factor


def bowling_projection_score(p: Player, bowl_data_scores: Dict[str, float]) -> float:
    prior = p.bowl_rating
    data_score = bowl_data_scores.get(p.name, 0.0)
    merged = merge_prior_and_data(prior, data_score, alpha=0.55)
    factor = {"bowler": 1.0, "allrounder": 0.9, "keeper": 0.3, "batter": 0.2}.get(p.role, 0.5)
    return merged * factor


def compute_team_strength(team_code: str,
                          players: List[Player],
                          bat_data_scores: Dict[str, float],
                          bowl_data_scores: Dict[str, float]) -> float:
    sel_scores = []
    for p in players:
        bat_s = batting_projection_score(p, bat_data_scores)
        bowl_s = bowling_projection_score(p, bowl_data_scores)
        if p.role == "batter":
            sel = bat_s
        elif p.role == "bowler":
            sel = bowl_s
        elif p.role == "keeper":
            sel = 0.8 * bat_s + 0.2 * bowl_s
        else:
            sel = 0.55 * bat_s + 0.45 * bowl_s
        sel_scores.append(sel)

    base = sum(sel_scores) / len(sel_scores)

    bias_map = {
        "MI": 0.06,
        "GT": 0.06,
        "RCB": 0.05,
        "PBKS": 0.04,
        "CSK": 0.03,
        "RR": 0.03,
    }
    return round(base + bias_map.get(team_code, 0.0), 3)


# --------------------------------
# Main: compute caps, top4, winner
# --------------------------------

def main():
    df = load_raw_data()
    bat_feat_scored, bat_emb, bowl_feat_scored, bowl_emb = build_feature_matrices(df)

    if bat_emb.shape[0] > 0 and bat_emb.ndim == 2:
        NearestNeighbors(n_neighbors=min(5, bat_emb.shape[0])).fit(bat_emb)

    if bowl_emb.shape[0] > 0 and bowl_emb.ndim == 2:
        NearestNeighbors(n_neighbors=min(5, bowl_emb.shape[0])).fit(bowl_emb)

    bat_data_scores, bowl_data_scores = build_player_score_lookup(bat_feat_scored, bowl_feat_scored)

    squads = build_best12()
    best12_json: Dict[str, Dict] = {}
    all_players: List[Player] = []

    for team, block in squads.items():
        xi = block["xi"]
        impact = block["impact"]
        all_players.extend(xi)
        all_players.append(impact)

        best12_json[team] = {
            "team": team,
            "xi": [
                {
                    "name": p.name,
                    "role": p.role,
                    "description": p.description,
                    "country": p.country,
                    "overseas": p.overseas,
                    "score": round(selection_score(p), 3),
                }
                for p in xi
            ],
            "impact": {
                "name": impact.name,
                "role": impact.role,
                "description": impact.description,
                "country": impact.country,
                "overseas": impact.overseas,
                "score": round(selection_score(impact), 3),
            },
        }

    orange_candidates = [
        "Abhishek Sharma", "Vaibhav Suryavanshi", "Shubman Gill",
        "Nicholas Pooran", "Suryakumar Yadav", "Virat Kohli",
        "Yashasvi Jaiswal", "Ishan Kishan", "Sai Sudharsan",
        "Travis Head", "Shreyas Iyer", "Rohit Sharma",
        "Mitchell Marsh", "Jos Buttler", "KL Rahul", "Heinrich Klaasen",
        "Priyansh Arya", "Tilak Varma", "Rinku Singh", "Shashank Singh",
    ]

    bat_scores_list = []
    for p in all_players:
        if p.name in orange_candidates:
            score = batting_projection_score(p, bat_data_scores)
            bat_scores_list.append((p, score))

    bat_scores_list.sort(key=lambda x: x[1], reverse=True)
    top_runs_pred = [
        {"name": p.name, "team": p.team, "role": p.role, "score": round(s, 3)}
        for p, s in bat_scores_list[:5]
    ]

    purple_candidates = [
        "Jasprit Bumrah", "Mohammed Siraj", "Yuzvendra Chahal", "Harshal Patel",
        "Rashid Khan", "Prasidh Krishna", "Arshdeep Singh", "Kuldeep Yadav",
        "Josh Hazlewood", "Bhuvneshwar Kumar", "Noor Ahmad", "Varun Chakravarthy",
        "Pat Cummins", "Mayank Yadav", "Mitchell Starc", "Mohammed Shami",
    ]

    bowl_scores_list = []
    for p in all_players:
        if p.name in purple_candidates:
            score = bowling_projection_score(p, bowl_data_scores)
            bowl_scores_list.append((p, score))

    bowl_scores_list.sort(key=lambda x: x[1], reverse=True)
    top_wkts_pred = [
        {"name": p.name, "team": p.team, "role": p.role, "score": round(s, 3)}
        for p, s in bowl_scores_list[:5]
    ]

    strengths = {
        team: compute_team_strength(
            team,
            block["xi"] + [block["impact"]],
            bat_data_scores,
            bowl_data_scores,
        )
        for team, block in squads.items()
    }

    max_s = max(strengths.values())
    min_s = min(strengths.values())
    scaled = {t: (s - min_s) / (max_s - min_s + 1e-6) for t, s in strengths.items()}
    total = sum(scaled.values()) or 1.0

    projections = []
    for team, val in scaled.items():
        share = val / total
        p_top4 = min(1.0, 0.25 + 0.75 * share)
        p_title = min(1.0, 0.05 + 0.9 * share)
        projections.append(
            {
                "team": team,
                "strength": strengths[team],
                "p_top4": round(p_top4, 3),
                "p_title": round(p_title, 3),
            }
        )

    projections.sort(key=lambda r: r["p_title"], reverse=True)
    top4_predicted = [
        p["team"] for p in sorted(projections, key=lambda r: r["p_top4"], reverse=True)[:4]
    ]
    title_favourite = projections[0]["team"] if projections else None

    output = {
        "best12": best12_json,
        "top_runs_pred": top_runs_pred,
        "top_wkts_pred": top_wkts_pred,
        "projections": projections,
        "top4_predicted": top4_predicted,
        "title_favourite": title_favourite,
    }

    with open("model_output.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print("model_output.json written.")


if __name__ == "__main__":
    main()
