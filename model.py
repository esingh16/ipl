import json
from dataclasses import dataclass, asdict
from typing import List, Dict

# ---- Data structures ----

@dataclass
class Player:
    name: str
    team: str
    country: str  # "India" or others
    role: str     # "batter", "bowler", "allrounder", "keeper"
    description: str  # human role description
    form_bat: float   # 0–1
    form_bowl: float  # 0–1

    def is_overseas(self) -> bool:
        return self.country != "India"

@dataclass
class TeamBest12:
    team: str
    xi: List[Dict]
    impact: Dict

@dataclass
class LeagueProjection:
    team: str
    strength: float
    p_top4: float
    p_title: float


# ---- 2025 form anchor from stats ----
# Using 2025 top runs/wickets & points as form indicators. [web:51][web:52][web:59][web:60][web:65][web:55][web:58][web:63][web:66]

# Normalized batting form (0–1) for some stars based on 2025 Orange Cap table. [web:51][web:52][web:59][web:65]
BAT_FORM_2025 = {
    "Sai Sudharsan": 1.00,
    "Suryakumar Yadav": 0.95,
    "Virat Kohli": 0.92,
    "Shubman Gill": 0.9,
    "Mitchell Marsh": 0.88,
    "KL Rahul": 0.86,
    "Jos Buttler": 0.85,
    "Nicholas Pooran": 0.84,
    "Rishabh Pant": 0.84,
    "Abhishek Sharma": 0.86,
    "Tilak Varma": 0.82,
    "Yashasvi Jaiswal": 0.83,
}

# Normalized bowling form from 2025 Purple Cap / wickets lists. [web:54][web:57][web:60][web:64]
BOWL_FORM_2025 = {
    "Mitchell Starc": 0.95,
    "Prasidh Krishna": 0.92,
    "Noor Ahmad": 0.9,
    "Yash Dayal": 0.9,
    "E Malinga": 0.88,   # SRH seamer
    "Mohammed Siraj": 0.9,
    "Jasprit Bumrah": 0.93,
    "Pat Cummins": 0.9,
    "Ravi Bishnoi": 0.88,
    "Arshdeep Singh": 0.88,
    "Yuzvendra Chahal": 0.9,
    "Mayank Yadav": 0.86,
}

def bat_form(name: str) -> float:
    return BAT_FORM_2025.get(name, 0.6)

def bowl_form(name: str) -> float:
    return BOWL_FORM_2025.get(name, 0.6)


# ---- Squads (2026) from your message ----

def build_squads() -> Dict[str, List[Player]]:
    squads: Dict[str, List[Player]] = {}

    # CSK
    csk = [
        Player("Ruturaj Gaikwad", "CSK", "India", "batter", "Top‑order captain", bat_form("Ruturaj Gaikwad"), 0.4),
        Player("MS Dhoni", "CSK", "India", "keeper", "Wicketkeeper finisher", 0.7, 0.3),
        Player("Dewald Brevis", "CSK", "SA", "batter", "Aggressive top‑order", 0.78, 0.3),
        Player("Ayush Mhatre", "CSK", "India", "batter", "Young batter", 0.6, 0.3),
        Player("Urvil Patel", "CSK", "India", "keeper", "Backup keeper", 0.55, 0.3),
        Player("Anshul Kamboj", "CSK", "India", "allrounder", "Pace all‑rounder", 0.6, 0.65),
        Player("Jamie Overton", "CSK", "ENG", "bowler", "Fast bowling all‑rounder", 0.55, 0.78),
        Player("Ramakrishna Ghosh", "CSK", "India", "allrounder", "Domestic all‑rounder", 0.58, 0.58),
        Player("Shivam Dube", "CSK", "India", "allrounder", "Middle‑order power‑hitter", bat_form("Shivam Dube"), 0.6),
        Player("Khaleel Ahmed", "CSK", "India", "bowler", "Left‑arm seamer", 0.4, 0.7),
        Player("Noor Ahmad", "CSK", "AFG", "bowler", "Left‑arm wrist‑spinner", 0.4, bowl_form("Noor Ahmad")),
        Player("Mukesh Choudhary", "CSK", "India", "bowler", "Left‑arm swing", 0.4, 0.6),
        Player("Nathan Ellis", "CSK", "AUS", "bowler", "Death‑overs seamer", 0.4, 0.72),
        Player("Shreyas Gopal", "CSK", "India", "bowler", "Leg‑spinner", 0.35, 0.6),
        Player("Gurjapneet Singh", "CSK", "India", "bowler", "Seamer", 0.4, 0.55),
        Player("Sanju Samson", "CSK", "India", "keeper", "Top‑order keeper", bat_form("Sanju Samson"), 0.35),
        Player("Akeal Hosein", "CSK", "WI", "bowler", "Left‑arm spinner", 0.35, 0.7),
        Player("Prashant Veer", "CSK", "India", "allrounder", "Big‑money all‑rounder", 0.65, 0.68),
        Player("Kartik Sharma", "CSK", "India", "keeper", "Young keeper", 0.5, 0.3),
        Player("Matthew Short", "CSK", "AUS", "allrounder", "Top‑order all‑rounder", 0.68, 0.6),
        Player("Aman Khan", "CSK", "India", "allrounder", "Pace‑all‑rounder", 0.6, 0.6),
        Player("Sarfaraz Khan", "CSK", "India", "batter", "Middle‑order batter", 0.65, 0.3),
        Player("Rahul Chahar", "CSK", "India", "bowler", "Leg‑spinner", 0.35, 0.7),
        Player("Matt Henry", "CSK", "NZ", "bowler", "New‑ball seamer", 0.4, 0.75),
        Player("Zak Foulkes", "CSK", "NZ", "allrounder", "Seam all‑rounder", 0.6, 0.65),
    ]
    squads["CSK"] = csk

    # DC
    dc = [
        Player("KL Rahul", "DC", "India", "keeper", "Top‑order keeper", bat_form("KL Rahul"), 0.35),
        Player("Karun Nair", "DC", "India", "batter", "Top‑order batter", 0.6, 0.3),
        Player("Abishek Porel", "DC", "India", "keeper", "Young keeper", 0.58, 0.3),
        Player("Tristan Stubbs", "DC", "SA", "batter", "Middle‑order finisher", 0.72, 0.35),
        Player("Axar Patel", "DC", "India", "allrounder", "Spin all‑rounder", 0.66, 0.75),
        Player("Sameer Rizvi", "DC", "India", "batter", "Power‑hitter", 0.62, 0.3),
        Player("Ashutosh Sharma", "DC", "India", "batter", "Finisher", 0.65, 0.3),
        Player("Vipraj Nigam", "DC", "India", "allrounder", "All‑rounder", 0.58, 0.55),
        Player("Ajay Mandal", "DC", "India", "allrounder", "Spin all‑rounder", 0.56, 0.58),
        Player("Tripurana Vijay", "DC", "India", "allrounder", "All‑rounder", 0.55, 0.55),
        Player("Madhav Tiwari", "DC", "India", "allrounder", "All‑rounder", 0.55, 0.55),
        Player("Mitchell Starc", "DC", "AUS", "bowler", "Left‑arm pace spearhead", 0.4, bowl_form("Mitchell Starc")),
        Player("T. Natarajan", "DC", "India", "bowler", "Left‑arm yorker specialist", 0.4, 0.78),
        Player("Mukesh Kumar", "DC", "India", "bowler", "Seamer", 0.4, 0.65),
        Player("Dushmantha Chameera", "DC", "SL", "bowler", "Right‑arm pace", 0.4, 0.7),
        Player("Kuldeep Yadav", "DC", "India", "bowler", "Chinaman spinner", 0.35, 0.78),
        Player("Nitish Rana", "DC", "India", "batter", "Top‑order bat", 0.68, 0.35),
        Player("Auqib Dar", "DC", "India", "allrounder", "All‑rounder", 0.6, 0.6),
        Player("Ben Duckett", "DC", "ENG", "keeper", "Top‑order keeper", 0.68, 0.35),
        Player("David Miller", "DC", "SA", "batter", "Middle‑order finisher", 0.75, 0.35),
        Player("Pathum Nissanka", "DC", "SL", "batter", "Top‑order anchor", 0.72, 0.3),
        Player("Lungi Ngidi", "DC", "SA", "bowler", "Pace bowler", 0.4, 0.7),
        Player("Sahil Parakh", "DC", "India", "batter", "Batter", 0.55, 0.3),
        Player("Prithvi Shaw", "DC", "India", "batter", "Aggressive opener", 0.65, 0.3),
        Player("Kyle Jamieson", "DC", "NZ", "bowler", "Tall seamer", 0.4, 0.68),
    ]
    squads["DC"] = dc

    # GT
    gt = [
        Player("Shubman Gill", "GT", "India", "batter", "Top‑order anchor", bat_form("Shubman Gill"), 0.35),
        Player("Sai Sudharsan", "GT", "India", "batter", "Top‑order run‑machine", bat_form("Sai Sudharsan"), 0.35),
        Player("Kumar Kushagra", "GT", "India", "keeper", "Young keeper", 0.58, 0.3),
        Player("Anuj Rawat", "GT", "India", "keeper", "Keeper‑batter", 0.6, 0.3),
        Player("Jos Buttler", "GT", "ENG", "keeper", "Explosive opener", bat_form("Jos Buttler"), 0.35),
        Player("Nishant Sindhu", "GT", "India", "allrounder", "Spin all‑rounder", 0.6, 0.6),
        Player("Glenn Phillips", "GT", "NZ", "allrounder", "Middle‑order all‑rounder", 0.72, 0.62),
        Player("Washington Sundar", "GT", "India", "allrounder", "Spin all‑rounder", 0.62, 0.7),
        Player("Arshad Khan", "GT", "India", "bowler", "Seamer", 0.4, 0.6),
        Player("Shahrukh Khan", "GT", "India", "batter", "Finisher", 0.7, 0.35),
        Player("Rahul Tewatia", "GT", "India", "allrounder", "Finisher all‑rounder", 0.68, 0.6),
        Player("Kagiso Rabada", "GT", "SA", "bowler", "Strike fast bowler", 0.4, 0.9),
        Player("Mohammed Siraj", "GT", "India", "bowler", "Fast bowler", 0.4, bowl_form("Mohammed Siraj")),
        Player("Prasidh Krishna", "GT", "India", "bowler", "Fast bowler", 0.4, bowl_form("Prasidh Krishna")),
        Player("Ishant Sharma", "GT", "India", "bowler", "Experienced seamer", 0.35, 0.65),
        Player("Gurnoor Singh Brar", "GT", "India", "bowler", "Seamer", 0.4, 0.55),
        Player("Rashid Khan", "GT", "AFG", "bowler", "World‑class spinner", 0.42, 0.93),
        Player("Manav Suthar", "GT", "India", "bowler", "Spinner", 0.35, 0.6),
        Player("Sai Kishore", "GT", "India", "bowler", "Left‑arm spinner", 0.35, 0.68),
        Player("Jayant Yadav", "GT", "India", "bowler", "Off‑spinner", 0.35, 0.6),
        Player("Ashok Sharma", "GT", "India", "bowler", "Pacer", 0.4, 0.6),
        Player("Jason Holder", "GT", "WI", "allrounder", "Pace all‑rounder", 0.7, 0.72),
        Player("Tom Banton", "GT", "ENG", "batter", "Top‑order", 0.64, 0.3),
        Player("Luke Wood", "GT", "ENG", "bowler", "Left‑arm pace", 0.4, 0.68),
        Player("Prithviraj Yarra", "GT", "India", "bowler", "Seamer", 0.4, 0.58),
    ]
    squads["GT"] = gt

    # KKR
    kkr = [
        Player("Ajinkya Rahane", "KKR", "India", "batter", "Top‑order", 0.6, 0.3),
        Player("Rinku Singh", "KKR", "India", "batter", "Finisher", 0.78, 0.3),
        Player("Angkrish Raghuvanshi", "KKR", "India", "batter", "Young top‑order", 0.6, 0.3),
        Player("Manish Pandey", "KKR", "India", "batter", "Top‑order", 0.6, 0.3),
        Player("Rovman Powell", "KKR", "WI", "allrounder", "Power‑hitting all‑rounder", 0.72, 0.62),
        Player("Anukul Roy", "KKR", "India", "allrounder", "Spin all‑rounder", 0.6, 0.6),
        Player("Ramandeep Singh", "KKR", "India", "batter", "Middle‑order", 0.6, 0.3),
        Player("Vaibhav Arora", "KKR", "India", "bowler", "Seamer", 0.4, 0.6),
        Player("Sunil Narine", "KKR", "WI", "allrounder", "Mystery spin all‑rounder", 0.7, 0.85),
        Player("Varun Chakaravarthy", "KKR", "India", "bowler", "Mystery spinner", 0.35, 0.8),
        Player("Harshit Rana", "KKR", "India", "bowler", "Pacer", 0.4, 0.65),
        Player("Umran Malik", "KKR", "India", "bowler", "Express pace", 0.4, 0.68),
        Player("Cameron Green", "KKR", "AUS", "allrounder", "Pace all‑rounder", 0.78, 0.75),
        Player("Matheesha Pathirana", "KKR", "SL", "bowler", "Death‑overs quick", 0.4, bowl_form("M Pathirana") if "M Pathirana" in BOWL_FORM_2025 else 0.9),
        Player("Finn Allen", "KKR", "NZ", "keeper", "Aggressive opener", 0.7, 0.3),
        Player("Tejasvi Singh", "KKR", "India", "keeper", "Keeper‑batter", 0.55, 0.3),
        Player("Prashant Solanki", "KKR", "India", "bowler", "Leg‑spinner", 0.35, 0.6),
        Player("Kartik Tyagi", "KKR", "India", "bowler", "Fast bowler", 0.4, 0.65),
        Player("Rahul Tripathi", "KKR", "India", "batter", "Top‑order", 0.68, 0.3),
        Player("Tim Seifert", "KKR", "NZ", "keeper", "Keeper‑batter", 0.65, 0.3),
        Player("Sarthak Ranjan", "KKR", "India", "allrounder", "All‑rounder", 0.58, 0.58),
        Player("Daksh Kamra", "KKR", "India", "allrounder", "All‑rounder", 0.58, 0.58),
        Player("Akash Deep", "KKR", "India", "bowler", "Seamer", 0.4, 0.7),
        Player("Rachin Ravindra", "KKR", "NZ", "allrounder", "Batting all‑rounder", 0.72, 0.7),
    ]
    squads["KKR"] = kkr

    # LSG
    lsg = [
        Player("Rishabh Pant", "LSG", "India", "keeper", "Top‑order keeper", bat_form("Rishabh Pant"), 0.35),
        Player("Ayush Badoni", "LSG", "India", "allrounder", "Middle‑order all‑rounder", 0.7, 0.65),
        Player("Abdul Samad", "LSG", "India", "batter", "Power‑hitter", 0.68, 0.3),
        Player("Aiden Markram", "LSG", "SA", "batter", "Top‑order", 0.7, 0.35),
        Player("Himmat Singh", "LSG", "India", "batter", "Batter", 0.6, 0.3),
        Player("Matthew Breetzke", "LSG", "SA", "batter", "Batter", 0.64, 0.3),
        Player("Nicholas Pooran", "LSG", "WI", "keeper", "Middle‑order keeper", bat_form("Nicholas Pooran"), 0.35),
        Player("Mitchell Marsh", "LSG", "AUS", "batter", "Top‑order power‑hitter", bat_form("Mitchell Marsh"), 0.4),
        Player("Shahbaz Ahamad", "LSG", "India", "allrounder", "Spin all‑rounder", 0.6, 0.6),
        Player("Arshin Kulkarni", "LSG", "India", "allrounder", "All‑rounder", 0.6, 0.6),
        Player("Mayank Yadav", "LSG", "India", "bowler", "Pace bowler", 0.4, bowl_form("Mayank Yadav")),
        Player("Avesh Khan", "LSG", "India", "bowler", "Pace bowler", 0.4, 0.7),
        Player("Mohsin Khan", "LSG", "India", "bowler", "Left‑arm seamer", 0.4, 0.68),
        Player("M. Siddharth", "LSG", "India", "bowler", "Spinner", 0.35, 0.6),
        Player("Digvesh Rathi", "LSG", "India", "bowler", "Bowler", 0.4, 0.55),
        Player("Prince Yadav", "LSG", "India", "bowler", "Bowler", 0.4, 0.55),
        Player("Akash Singh", "LSG", "India", "bowler", "Bowler", 0.4, 0.55),
        Player("Arjun Tendulkar", "LSG", "India", "bowler", "Left‑arm seamer", 0.4, 0.6),
        Player("Mohammed Shami", "LSG", "India", "bowler", "Senior fast bowler", 0.4, 0.88),
        Player("Anrich Nortje", "LSG", "SA", "bowler", "Fast bowler", 0.4, 0.82),
        Player("Wanindu Hasaranga", "LSG", "SL", "allrounder", "Leg‑spin all‑rounder", 0.7, 0.9),
        Player("Mukul Choudhary", "LSG", "India", "keeper", "Keeper‑batter", 0.55, 0.3),
        Player("Naman Tiwari", "LSG", "India", "allrounder", "All‑rounder", 0.58, 0.58),
        Player("Akshat Raghuwanshi", "LSG", "India", "batter", "Batter", 0.6, 0.3),
        Player("Josh Inglis", "LSG", "AUS", "batter", "Top‑order", 0.68, 0.3),
    ]
    squads["LSG"] = lsg

    # MI
    mi = [
        Player("Rohit Sharma", "MI", "India", "batter", "Opener", 0.7, 0.3),
        Player("Suryakumar Yadav", "MI", "India", "batter", "Middle‑order", bat_form("Suryakumar Yadav"), 0.3),
        Player("Robin Minz", "MI", "India", "keeper", "Young keeper", 0.58, 0.3),
        Player("Ryan Rickelton", "MI", "SA", "keeper", "Top‑order keeper", 0.68, 0.3),
        Player("Tilak Varma", "MI", "India", "batter", "Middle‑order", bat_form("Tilak Varma"), 0.3),
        Player("Hardik Pandya", "MI", "India", "allrounder", "Seam all‑rounder", 0.75, 0.8),
        Player("Naman Dhir", "MI", "India", "allrounder", "All‑rounder", 0.6, 0.6),
        Player("Mitchell Santner", "MI", "NZ", "allrounder", "Spin all‑rounder", 0.64, 0.75),
        Player("Will Jacks", "MI", "AUS", "allrounder", "Batting all‑rounder", 0.7, 0.65),
        Player("Corbin Bosch", "MI", "SA", "allrounder", "Pace all‑rounder", 0.62, 0.68),
        Player("Raj Bawa", "MI", "India", "allrounder", "Batting all‑rounder", 0.6, 0.6),
        Player("Trent Boult", "MI", "NZ", "bowler", "Left‑arm swing", 0.4, 0.86),
        Player("Jasprit Bumrah", "MI", "India", "bowler", "World‑class seamer", 0.4, bowl_form("Jasprit Bumrah")),
        Player("Deepak Chahar", "MI", "India", "bowler", "New‑ball seamer", 0.4, 0.7),
        Player("Ashwani Kumar", "MI", "India", "bowler", "Bowler", 0.4, 0.55),
        Player("Raghu Sharma", "MI", "India", "bowler", "Bowler", 0.4, 0.55),
        Player("Allah Ghazanfar", "MI", "AFG", "bowler", "Spinner", 0.35, 0.68),
        Player("Mayank Markande", "MI", "India", "bowler", "Leg‑spinner", 0.35, 0.68),
        Player("Shardul Thakur", "MI", "India", "allrounder", "Seam all‑rounder", 0.66, 0.7),
        Player("Sherfane Rutherford", "MI", "WI", "batter", "All‑round finisher", 0.7, 0.6),
        Player("Quinton De Kock", "MI", "SA", "keeper", "Top‑order keeper", 0.72, 0.35),
        Player("Atharva Ankolekar", "MI", "India", "allrounder", "Spin all‑rounder", 0.6, 0.6),
        Player("Mohammad Izhar", "MI", "India", "bowler", "Bowler", 0.4, 0.55),
        Player("Danish Malewar", "MI", "India", "batter", "Batter", 0.6, 0.3),
        Player("Mayank Rawat", "MI", "India", "allrounder", "All‑rounder", 0.6, 0.6),
    ]
    squads["MI"] = mi

    # PBKS
    pbks = [
        Player("Shreyas Iyer", "PBKS", "India", "batter", "Top‑order", 0.7, 0.3),
        Player("Nehal Wadhera", "PBKS", "India", "batter", "Middle‑order", 0.6, 0.3),
        Player("Vishnu Vinod", "PBKS", "India", "keeper", "Keeper‑batter", 0.58, 0.3),
        Player("Harnoor Pannu", "PBKS", "India", "batter", "Batter", 0.6, 0.3),
        Player("Pyla Avinash", "PBKS", "India", "batter", "Batter", 0.6, 0.3),
        Player("Prabhsimran Singh", "PBKS", "India", "keeper", "Aggressive keeper", 0.65, 0.3),
        Player("Shashank Singh", "PBKS", "India", "batter", "Middle‑order finisher", 0.9, 0.3),
        Player("Marcus Stoinis", "PBKS", "AUS", "allrounder", "Pace all‑rounder", 0.72, 0.7),
        Player("Harpreet Brar", "PBKS", "India", "allrounder", "Spin all‑rounder", 0.62, 0.7),
        Player("Marco Jansen", "PBKS", "SA", "allrounder", "Tall pace all‑rounder", 0.68, 0.72),
        Player("Azmatullah Omarzai", "PBKS", "AFG", "allrounder", "Pace all‑rounder", 0.68, 0.72),
        Player("Priyansh Arya", "PBKS", "India", "allrounder", "All‑rounder", 0.6, 0.6),
        Player("Musheer Khan", "PBKS", "India", "allrounder", "Batting all‑rounder", 0.62, 0.6),
        Player("Suryansh Shedge", "PBKS", "India", "allrounder", "All‑rounder", 0.6, 0.6),
        Player("Mitch Owen", "PBKS", "AUS", "allrounder", "All‑rounder", 0.62, 0.65),
        Player("Arshdeep Singh", "PBKS", "India", "bowler", "Left‑arm seamer", 0.4, bowl_form("Arshdeep Singh")),
        Player("Yuzvendra Chahal", "PBKS", "India", "bowler", "Leg‑spinner", 0.35, bowl_form("Yuzvendra Chahal")),
        Player("Vyshak Vijaykumar", "PBKS", "India", "bowler", "Bowler", 0.4, 0.6),
        Player("Yash Thakur", "PBKS", "India", "bowler", "Bowler", 0.4, 0.6),
        Player("Xavier Bartlett", "PBKS", "AUS", "bowler", "Pace bowler", 0.4, 0.7),
        Player("Lockie Ferguson", "PBKS", "NZ", "bowler", "Fast bowler", 0.4, 0.72),
        Player("Cooper Connolly", "PBKS", "AUS", "allrounder", "Batting all‑rounder", 0.64, 0.6),
        Player("Ben Dwarshuis", "PBKS", "AUS", "allrounder", "Pace all‑rounder", 0.64, 0.68),
        Player("Vishal Nishad", "PBKS", "India", "bowler", "Bowler", 0.4, 0.55),
        Player("Pravin Dubey", "PBKS", "India", "bowler", "Leg‑spinner", 0.35, 0.6),
    ]
    squads["PBKS"] = pbks

    # RR
    rr = [
        Player("Shubham Dubey", "RR", "India", "batter", "Batter", 0.6, 0.3),
        Player("Vaibhav Suryavanshi", "RR", "India", "batter", "Batter", 0.6, 0.3),
        Player("Lhuan-dre Pretorius", "RR", "SA", "batter", "Top‑order", 0.64, 0.3),
        Player("Shimron Hetmyer", "RR", "WI", "batter", "Finisher", 0.72, 0.3),
        Player("Yashasvi Jaiswal", "RR", "India", "batter", "Aggressive opener", bat_form("Yashasvi Jaiswal"), 0.3),
        Player("Dhruv Jurel", "RR", "India", "keeper", "Keeper‑batter", 0.68, 0.3),
        Player("Riyan Parag", "RR", "India", "batter", "Middle‑order", 0.7, 0.35),
        Player("Yudhvir Singh Charak", "RR", "India", "allrounder", "All‑rounder", 0.6, 0.6),
        Player("Jofra Archer", "RR", "ENG", "bowler", "Fast bowler", 0.4, 0.82),
        Player("Tushar Deshpande", "RR", "India", "bowler", "Seamer", 0.4, 0.68),
        Player("Sandeep Sharma", "RR", "India", "bowler", "Swing bowler", 0.4, 0.7),
        Player("Kwena Maphaka", "RR", "SA", "bowler", "Left‑arm seamer", 0.4, 0.7),
        Player("Nandre Burger", "RR", "SA", "bowler", "Left‑arm seamer", 0.4, 0.7),
        Player("Ravindra Jadeja", "RR", "India", "allrounder", "World‑class all‑rounder", 0.78, 0.86),
        Player("Sam Curran", "RR", "ENG", "allrounder", "Pace all‑rounder", 0.7, 0.75),
        Player("Donovan Ferreira", "RR", "SA", "keeper", "Middle‑order keeper", 0.68, 0.3),
        Player("Ravi Bishnoi", "RR", "India", "bowler", "Leg‑spinner", 0.35, bowl_form("Ravi Bishnoi")),
        Player("Sushant Mishra", "RR", "India", "bowler", "Bowler", 0.4, 0.6),
        Player("Vignesh Puthur", "RR", "India", "bowler", "Bowler", 0.4, 0.55),
        Player("Yash Raj Punja", "RR", "India", "bowler", "Bowler", 0.4, 0.55),
        Player("Ravi Singh", "RR", "India", "keeper", "Keeper", 0.55, 0.3),
        Player("Brijesh Sharma", "RR", "India", "bowler", "Bowler", 0.4, 0.55),
        Player("Aman Rao", "RR", "India", "batter", "Batter", 0.6, 0.3),
        Player("Adam Milne", "RR", "NZ", "bowler", "Fast bowler", 0.4, 0.7),
        Player("Kuldeep Sen", "RR", "India", "bowler", "Pacer", 0.4, 0.68),
    ]
    squads["RR"] = rr

    # RCB
    rcb = [
        Player("Rajat Patidar", "RCB", "India", "batter", "Top‑order", 0.7, 0.3),
        Player("Virat Kohli", "RCB", "India", "batter", "Top‑order run‑machine", bat_form("Virat Kohli"), 0.3),
        Player("Tim David", "RCB", "AUS", "allrounder", "Power‑hitting all‑rounder", 0.7, 0.6),
        Player("Devdutt Padikkal", "RCB", "India", "batter", "Top‑order", 0.7, 0.3),
        Player("Phil Salt", "RCB", "ENG", "keeper", "Aggressive keeper", 0.7, 0.3),
        Player("Jitesh Sharma", "RCB", "India", "keeper", "Keeper‑finisher", 0.7, 0.3),
        Player("Krunal Pandya", "RCB", "India", "allrounder", "Spin all‑rounder", 0.66, 0.72),
        Player("Jacob Bethell", "RCB", "ENG", "allrounder", "All‑rounder", 0.62, 0.65),
        Player("Romario Shepherd", "RCB", "WI", "allrounder", "Power all‑rounder", 0.68, 0.7),
        Player("Swapnil Singh", "RCB", "India", "allrounder", "Spin all‑rounder", 0.6, 0.6),
        Player("Josh Hazlewood", "RCB", "AUS", "bowler", "Fast bowler", 0.4, 0.78),
        Player("Bhuvneshwar Kumar", "RCB", "India", "bowler", "Swing bowler", 0.4, 0.82),
        Player("Rasikh Salam", "RCB", "India", "bowler", "Bowler", 0.4, 0.6),
        Player("Yash Dayal", "RCB", "India", "bowler", "Left‑arm seamer", 0.4, bowl_form("Yash Dayal")),
        Player("Suyash Sharma", "RCB", "India", "bowler", "Leg‑spinner", 0.35, 0.68),
        Player("Nuwan Thushara", "RCB", "SL", "bowler", "Slingy seamer", 0.4, 0.7),
        Player("Abhinandan Singh", "RCB", "India", "bowler", "Bowler", 0.4, 0.55),
        Player("Venkatesh Iyer", "RCB", "India", "allrounder", "Batting all‑rounder", 0.7, 0.6),
        Player("Jacob Duffy", "RCB", "NZ", "bowler", "Fast bowler", 0.4, 0.68),
        Player("Mangesh Yadav", "RCB", "India", "allrounder", "All‑rounder", 0.6, 0.6),
        Player("Satvik Deswal", "RCB", "India", "allrounder", "All‑rounder", 0.6, 0.6),
        Player("Jordan Cox", "RCB", "ENG", "batter", "Batter", 0.64, 0.3),
        Player("Kanishk Chouhan", "RCB", "India", "allrounder", "All‑rounder", 0.6, 0.6),
        Player("Vihaan Malhotra", "RCB", "India", "allrounder", "All‑rounder", 0.6, 0.6),
        Player("Vicky Ostwal", "RCB", "India", "allrounder", "Spin all‑rounder", 0.6, 0.65),
    ]
    squads["RCB"] = rcb

    # SRH
    srh = [
        Player("Travis Head", "SRH", "AUS", "batter", "Aggressive opener", 0.8, 0.35),
        Player("Abhishek Sharma", "SRH", "India", "allrounder", "Top‑order all‑rounder", bat_form("Abhishek Sharma"), 0.7),
        Player("Aniket Verma", "SRH", "India", "batter", "Batter", 0.6, 0.3),
        Player("R Smaran", "SRH", "India", "batter", "Batter", 0.6, 0.3),
        Player("Ishan Kishan", "SRH", "India", "keeper", "Top‑order keeper", bat_form("Ishan Kishan"), 0.35),
        Player("Heinrich Klaasen", "SRH", "SA", "keeper", "Middle‑order keeper", 0.78, 0.35),
        Player("Nitish Kumar Reddy", "SRH", "India", "allrounder", "All‑rounder", 0.7, 0.68),
        Player("Harsh Dubey", "SRH", "India", "allrounder", "All‑rounder", 0.6, 0.6),
        Player("Kamindu Mendis", "SRH", "SL", "allrounder", "All‑rounder", 0.66, 0.68),
        Player("Harshal Patel", "SRH", "India", "allrounder", "Seam all‑rounder", 0.66, 0.78),
        Player("Brydon Carse", "SRH", "ENG", "allrounder", "Pace all‑rounder", 0.64, 0.7),
        Player("Pat Cummins", "SRH", "AUS", "bowler", "Fast bowler", 0.4, bowl_form("Pat Cummins")),
        Player("Jaydev Unadkat", "SRH", "India", "bowler", "Left‑arm seamer", 0.4, 0.68),
        Player("Eshan Malinga", "SRH", "SL", "bowler", "Seamer", 0.4, bowl_form("E Malinga")),
        Player("Zeeshan Ansari", "SRH", "India", "bowler", "Spinner", 0.35, 0.6),
        Player("Shivang Kumar", "SRH", "India", "allrounder", "All‑rounder", 0.6, 0.6),
        Player("Salil Arora", "SRH", "India", "keeper", "Keeper‑batter", 0.6, 0.3),
        Player("Krains Fuletra", "SRH", "India", "bowler", "Bowler", 0.4, 0.55),
        Player("Praful Hinge", "SRH", "India", "bowler", "Bowler", 0.4, 0.55),
        Player("Amit Kumar", "SRH", "India", "bowler", "Bowler", 0.4, 0.55),
        Player("Onkar Tarmale", "SRH", "India", "bowler", "Bowler", 0.4, 0.55),
        Player("Sakib Hussain", "SRH", "India", "bowler", "Bowler", 0.4, 0.55),
        Player("Liam Livingstone", "SRH", "ENG", "allrounder", "Batting all‑rounder", 0.76, 0.7),
        Player("Shivam Mavi", "SRH", "India", "bowler", "Pacer", 0.4, 0.7),
        Player("Jack Edwards", "SRH", "AUS", "allrounder", "All‑rounder", 0.62, 0.64),
    ]
    squads["SRH"] = srh

    return squads


# ---- Scoring functions ----

def selection_score(p: Player) -> float:
    """
    XI selection score: mix batting and bowling form.
    All‑rounders get bonus; overseas get small penalty to favour Indian depth.
    """
    if p.role == "batter":
        base = p.form_bat
    elif p.role == "bowler":
        base = p.form_bowl
    elif p.role == "keeper":
        base = 0.7 * p.form_bat + 0.3 * p.form_bowl
    else:  # allrounder
        base = 0.55 * p.form_bat + 0.45 * p.form_bowl

    bonus = 0.04 if p.role == "allrounder" else 0.0
    overseas_penalty = 0.02 if p.is_overseas() else 0.0
    return max(0.0, min(1.0, base + bonus - overseas_penalty))

def batting_projection_score(p: Player) -> float:
    """
    Season runs projection: emphasise batting form; all‑rounders lower volume.
    """
    role_factor = {"batter": 1.0, "keeper": 0.95, "allrounder": 0.8, "bowler": 0.4}.get(p.role, 0.7)
    return p.form_bat * role_factor

def bowling_projection_score(p: Player) -> float:
    """
    Season wickets projection: emphasise bowling form; batters mostly ignored.
    """
    role_factor = {"bowler": 1.0, "allrounder": 0.9, "keeper": 0.3, "batter": 0.2}.get(p.role, 0.5)
    return p.form_bowl * role_factor


# ---- XI + Impact selection per team ----

def pick_best12_for_team(players: List[Player]) -> TeamBest12:
    enriched = [(p, selection_score(p)) for p in players]
    enriched.sort(key=lambda x: x[1], reverse=True)

    xi: List[Player] = []
    overseas_count = 0

    for p, s in enriched:
        if len(xi) == 11:
            break
        if p.is_overseas() and overseas_count >= 4:
            continue
        xi.append(p)
        if p.is_overseas():
            overseas_count += 1

    # ensure at least 5 bowling options (bowler/allrounder)
    def is_bowling_option(pp: Player) -> bool:
        return pp.role in ("bowler", "allrounder")

    bow_count = sum(is_bowling_option(pp) for pp in xi)
    if bow_count < 5:
        needed = 5 - bow_count
        for p, s in enriched:
            if needed == 0:
                break
            if p in xi:
                continue
            if not is_bowling_option(p):
                continue
            if p.is_overseas() and overseas_count >= 4:
                continue
            # replace lowest‑score pure batter/keeper
            pure_bats = [pp for pp in xi if not is_bowling_option(pp)]
            if not pure_bats:
                break
            to_drop = pure_bats[-1]
            xi.remove(to_drop)
            xi.append(p)
            if p.is_overseas():
                overseas_count += 1
            needed -= 1

    xi_with_scores = [(pp, selection_score(pp)) for pp in xi]
    remaining = [(p, s) for p, s in enriched if p not in xi]
    remaining.sort(key=lambda x: x[1], reverse=True)
    impact_player = remaining[0][0] if remaining else None

    return TeamBest12(
        team=players[0].team,
        xi=[{
            "name": p.name,
            "role": p.role,
            "description": p.description,
            "country": p.country,
            "overseas": p.is_overseas(),
            "score": round(selection_score(p), 3),
        } for p, _ in xi_with_scores],
        impact={
            "name": impact_player.name,
            "role": impact_player.role,
            "description": impact_player.description,
            "country": impact_player.country,
            "overseas": impact_player.is_overseas(),
            "score": round(selection_score(impact_player), 3),
        } if impact_player else {}
    )


# ---- League‑wide predictions ----

def predict_top_batters(all_players: List[Player], top_n: int = 5):
    scored = [(p, batting_projection_score(p)) for p in all_players]
    scored.sort(key=lambda x: x[1], reverse=True)
    return [{
        "name": p.name,
        "team": p.team,
        "role": p.role,
        "score": round(s, 3)
    } for p, s in scored[:top_n]]

def predict_top_bowlers(all_players: List[Player], top_n: int = 5):
    scored = [(p, bowling_projection_score(p)) for p in all_players]
    scored.sort(key=lambda x: x[1], reverse=True)
    return [{
        "name": p.name,
        "team": p.team,
        "role": p.role,
        "score": round(s, 3)
    } for p, s in scored[:top_n]]


# ---- Team strength & playoff odds (using 2025 table as prior) ----
# 2025 points / strength anchor. [web:55][web:58][web:63][web:66]
POINTS_2025 = {
    "PBKS": 19,
    "RCB": 19,
    "GT": 18,
    "MI": 16,
    "DC": 15,
    "SRH": 13,
    "LSG": 12,
    "KKR": 12,
    "RR": 8,
    "CSK": 8,
}

def compute_team_strength(team: str, players: List[Player]) -> float:
    avg_sel = sum(selection_score(p) for p in players) / len(players)
    pts = POINTS_2025.get(team, 12)
    pts_norm = (pts - 8) / (19 - 8)  # roughly 0–1
    return 0.55 * avg_sel + 0.45 * pts_norm

def compute_league_projections(squads: Dict[str, List[Player]]) -> List[LeagueProjection]:
    strengths = {team: compute_team_strength(team, players) for team, players in squads.items()}
    max_s = max(strengths.values())
    min_s = min(strengths.values())
    # scale 0–1
    scaled = {t: (s - min_s) / (max_s - min_s + 1e-6) for t, s in strengths.items()}

    # simple mapping: p_top4 and p_title proportional to strength
    total_strength = sum(scaled.values())
    projections = []
    for team, s in scaled.items():
        share = s / total_strength if total_strength > 0 else 0
        p_top4 = min(1.0, 0.25 + 0.8 * share)   # base + bonus
        p_title = min(1.0, 0.05 + 0.9 * share)
        projections.append(LeagueProjection(team, round(strengths[team], 3),
                                            round(p_top4, 3), round(p_title, 3)))
    projections.sort(key=lambda x: x.p_title, reverse=True)
    return projections


# ---- Main: generate JSON file ----

def main():
    squads = build_squads()
    best12_by_team = {}
    all_players: List[Player] = []
    for team, players in squads.items():
        best = pick_best12_for_team(players)
        best12_by_team[team] = {
            "team": best.team,
            "xi": best.xi,
            "impact": best.impact,
        }
        all_players.extend(players)

    top_batters = predict_top_batters(all_players, top_n=5)
    top_bowlers = predict_top_bowlers(all_players, top_n=5)
    projections = compute_league_projections(squads)

    winner = projections[0].team if projections else None
    top4 = [p.team for p in sorted(projections, key=lambda x: x.p_top4, reverse=True)[:4]]

    output = {
        "best12": best12_by_team,
        "top_runs_pred": top_batters,
        "top_wkts_pred": top_bowlers,
        "projections": [
            {"team": p.team, "strength": p.strength,
             "p_top4": p.p_top4, "p_title": p.p_title}
            for p in projections
        ],
        "top4_predicted": top4,
        "title_favourite": winner,
    }

    with open("model_output.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)
    print("model_output.json written.")


if __name__ == "__main__":
    main()
