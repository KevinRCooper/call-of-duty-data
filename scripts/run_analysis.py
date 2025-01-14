import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

###############################################################################
# 1. Load & Clean Data
###############################################################################

current_directory = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
file_path = os.path.join(project_root, "data", "multiplayer_match_data.csv")

data = pd.read_csv(file_path)

# Irrelevant columns + newly excluded columns
irrelevant_columns = [
    "Map", "Team", "Operator", "Operator Skin", "Execution",
    "Weapon XP", "Operator XP", "Clan XP", "Battle Pass",
    "Prestige at Start", "Prestige at End", "Match ID",
    "Lifetime Wins", "Lifetime Losses", "Lifetime Kills", "Lifetime Deaths",
    "Lifetime Hits", "Lifetime Misses", "Lifetime Near Misses",
    "Lifetime Wall Bangs", "Lifetime Games Played", "Lifetime Time Played",
    "XP at Start", "XP at End", "Score at Start", "Score at End",
    "Rank at Start", "Rank at End", "Bonus XP", "Score XP", "Total XP",
    "Battle Pass XP", "Medal XP",
    "Armor Equipped", "Armor Destroyed", "Armor Collected",
    "Ground Vehicles Used", "Air Vehicles Used",
    "Challenge XP", "Match XP", "Misc XP", "Accolade XP"
]

data_cleaned = data.drop(columns=irrelevant_columns, errors='ignore')

###############################################################################
# 2. Create Lagged Features
###############################################################################

lagged_data = data_cleaned.shift(1).add_suffix(' (Previous Match)')
data_cleaned['Skill_t'] = data_cleaned['Skill']
lagged_data['Skill'] = data_cleaned['Skill_t']

lagged_data.dropna(inplace=True)

###############################################################################
# 3. Prepare Features & Target (EXCLUDE "Skill (Previous Match)")
###############################################################################
X = lagged_data.select_dtypes(include=['number']).drop(
    columns=['Skill', 'Skill (Previous Match)'], 
    errors='ignore'
)
y = lagged_data['Skill']

X.fillna(0, inplace=True)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

###############################################################################
# 4. Train Random Forest
###############################################################################
model = RandomForestRegressor(random_state=42)
model.fit(X_train, y_train)

importances = model.feature_importances_
rf_feature_importance = pd.DataFrame({
    'Feature': X.columns,
    'Importance': importances
}).sort_values(by='Importance', ascending=False)

# Normalize for plotting clarity
rf_feature_importance['Normalized_Importance'] = (
    rf_feature_importance['Importance'] / rf_feature_importance['Importance'].max()
)

plt.figure(figsize=(12, 6))
sns.barplot(
    data=rf_feature_importance.head(15),
    x='Normalized_Importance',
    y='Feature',
    palette='viridis'
)
plt.title("Random Forest Feature Importances (Excluding 'Skill (Previous Match)'")
plt.xlabel("Normalized Importance")
plt.ylabel("Features")
plt.tight_layout()
plt.show()

###############################################################################
# 5. Correlation Analysis with “Next Skill”
###############################################################################
numeric_columns = lagged_data.select_dtypes(include=['number']).columns
numeric_data = lagged_data[numeric_columns]
correlation_matrix = numeric_data.corr()

excluded_features = [
    "Skill (Previous Match)",  # overshadowing factor
    "Skill",                   # the target itself
]

skill_correlation = correlation_matrix['Skill'].sort_values(ascending=False)
correlation_ranking = skill_correlation.reset_index()
correlation_ranking.columns = ['Feature', 'Correlation']

filtered_correlation_ranking = correlation_ranking[
    ~correlation_ranking['Feature'].isin(excluded_features)
]

###############################################################################
# 6. Visualization: Bar Chart (Highest to Lowest)
###############################################################################
sorted_corr_desc = filtered_correlation_ranking.sort_values(
    by='Correlation', ascending=False
)

plt.figure(figsize=(12, 6))
sns.barplot(
    data=sorted_corr_desc,
    x='Correlation',
    y='Feature',
    palette='coolwarm'
)
plt.axvline(0, color='gray', linewidth=1)
plt.title("Features Ranked by Correlation with Next Skill Rating")
plt.xlabel("Correlation (Descending)")
plt.ylabel("Features")
plt.tight_layout()
plt.show()

###############################################################################
# 7. Visualization: Table of Correlations
###############################################################################
top_n = 10
table_data = sorted_corr_desc.head(top_n).copy()

fig, ax = plt.subplots(figsize=(6, 1 + 0.4*top_n))
ax.axis('off')  # Hide the main axes

table_cells = [[row['Feature'], f"{row['Correlation']:.3f}"] for _, row in table_data.iterrows()]
col_labels = ["Feature", "Correlation"]

the_table = ax.table(
    cellText=table_cells,
    colLabels=col_labels,
    loc='center',
    cellLoc='center'
)

the_table.scale(1, 2)
plt.title("Top 10 Correlations with Next Skill (Table View)")
plt.show()

###############################################################################
# 8. Visualization: “What to Improve”
###############################################################################
positive_sorted = sorted_corr_desc[sorted_corr_desc['Correlation'] > 0]
top_positive = positive_sorted.head(10)

plt.figure(figsize=(10, 6))
sns.barplot(
    data=top_positive,
    x='Correlation',
    y='Feature',
    palette='Greens'
)
plt.title("Focus on These Features to Potentially Improve Next Skill")
plt.xlabel("Correlation with Next Skill (Positive)")
plt.ylabel("Features")
plt.tight_layout()
plt.show()

###############################################################################
# 9. Print Positive vs Negative Correlations (Top 5)
###############################################################################
positive_correlations = sorted_corr_desc[sorted_corr_desc['Correlation'] > 0]
negative_correlations = sorted_corr_desc[sorted_corr_desc['Correlation'] < 0]

print("Positive Correlations (Likely to Increase Skill):")
print(positive_correlations.head(5).to_string(index=False), "\n")

print("Negative Correlations (Likely to Decrease Skill):")
print(negative_correlations.tail(5).to_string(index=False), "\n")
