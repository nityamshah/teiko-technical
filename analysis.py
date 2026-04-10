import sqlite3
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import ttest_ind

#part 2: initial analysis
def compute_frequency_table (db_path = "database.db"):

    """Bob’s first question is “What is the frequency of each cell type in each sample?” 
    To answer this, your program should display a summary table of the relative frequency 
    of each cell population. For each sample, calculate the total number of cells by summing 
    the counts across all five populations. Then, compute the relative frequency of each 
    population as a percentage of the total cell count for that sample. Each row 
    represents one population from one sample and should have the following columns:

    sample: the sample id as in column sample in cell-count.csv
    total_count: total cell count of sample
    population: name of the immune cell population (e.g. b_cell, cd8_t_cell, etc.)
    count: cell count
    percentage: relative frequency in percentage"""

    #i will output this summary to a csv called cell_freq_summary.csv
    connection = sqlite3.connect(db_path)

    #getting all info from database into pandas dataframa
    df = pd.read_sql_query("""
        SELECT 
            sample_id,
            b_cell,
            cd8_t_cell,
            cd4_t_cell,
            nk_cell,
            monocyte
        FROM cell_counts
    """, connection)

    #calc total cell count for each sample
    df["total_count"] = (
        df["b_cell"] +
        df["cd8_t_cell"] +
        df["cd4_t_cell"] +
        df["nk_cell"] +
        df["monocyte"]
    )

    #transform it from one row per sample -> one row per population per sample
    melted_df = df.melt(
        id_vars=["sample_id", "total_count"],
        value_vars=["b_cell", "cd8_t_cell", "cd4_t_cell", "nk_cell", "monocyte"],
        var_name="population",
        value_name="count"
    )
    melted_df = melted_df.sort_values(["sample_id", "population"])
    melted_df = melted_df.reset_index(drop=True)


    #add in relative percentages
    melted_df["percentage"] = (melted_df["count"] / melted_df["total_count"]) * 100

    #renaming, reordering to match instructions
    melted_df = melted_df.rename(columns={"sample_id": "sample"})
    melted_df = melted_df[[
        "sample",
        "total_count",
        "population",
        "count",
        "percentage"
    ]]

    #save to file
    melted_df.to_csv("cell_freq_summary.csv", index=False)

    connection.close()
    return melted_df

#part 3: statistical analysis
def run_statistical_analysis(db_path = "database.db"):
    """Part 3: Statistical Analysis

    As the trial progresses, Bob wants to identify patterns that might predict treatment 
    response and share those findings with his colleague, Yah D’yada. Using the data 
    reported in the summary table, your program should provide functionality to:

    Compare the differences in cell population relative frequencies of melanoma patients 
    receiving miraclib who respond (responders) versus those who do not (non-responders), 
    with the overarching aim of predicting response to the treatment miraclib. 
    Response information can be found in column "response", with value "yes" for 
    responding and value "no" for non-responding. Please only include PBMC samples.

    Visualize the population relative frequencies comparing responders versus non-responders 
    using a boxplot of for each immune cell population.

    Report which cell populations have a significant difference in relative frequencies 
    between responders and non-responders. Statistics are needed to support any conclusion 
    to convince Yah of Bob’s findings. 
    """
    #i will output these stats to a csv called statistical_analysis.csv 
    connection = sqlite3.connect(db_path)

    #again, getting all info from database into pandas dataframe, not using summary dataframe
    #becuase I need some other info
    df = pd.read_sql_query("""
        SELECT 
            s.sample_id,
            sub.condition,
            sub.treatment,
            s.sample_type,
            sub.response,
            c.b_cell,
            c.cd8_t_cell,
            c.cd4_t_cell,
            c.nk_cell,
            c.monocyte
        FROM samples s
        JOIN subjects sub ON s.subject_id = sub.subject_id
        JOIN cell_counts c ON s.sample_id = c.sample_id
    """, connection)

    #filter for only melanoma, miraclib, and PBMC 
    df = df[
        (df["condition"] == "melanoma") &
        (df["treatment"] == "miraclib") &
        (df["sample_type"] == "PBMC")
    ]

    #similar to part 2 compute relative freqs
    cells = ["b_cell", "cd8_t_cell", "cd4_t_cell", "nk_cell", "monocyte"]
    df["total_count"] = df[cells].sum(axis=1)
    for c in cells:
        df[c] = (df[c] / df["total_count"]) * 100

    #transform/melt again to make boxplot simpler
    melted_df = df.melt(
        id_vars=["sample_id", "response"],
        value_vars=cells,
        var_name="population",
        value_name="percentage"
    )

    #box plots
    plt.figure(figsize=(10, 6))
    sns.boxplot(
        data=melted_df,
        x="population",
        y="percentage",
        hue="response"
    )
    plt.title("Responder vs Non-Responder Immune Profiles")
    plt.xticks(rotation=45)
    plt.show()

    #which have statistically significant 
    #difference in relative frequencies between responders and non-responders?
    results = []

    for pop in melted_df["population"].unique():
        population_df = melted_df[melted_df["population"] == pop]

        responders = population_df[population_df["response"] == "yes"]["percentage"]
        non_responders = population_df[population_df["response"] == "no"]["percentage"]

        stat, p = ttest_ind(responders, non_responders, equal_var=False)

        results.append({
            "population": pop,
            "p_value": p,
            "significant": p < 0.05
        })

    #save to file
    pd.DataFrame(results).to_csv("statistical_analysis.csv", index=False)

    return pd.DataFrame(results)

def main():
    df = compute_frequency_table()
    print("Printing head of summary table from part 2:\n")
    print(df.head()) # print head of summary

    df = run_statistical_analysis()
    print("Printing statistical analysis from part 3")
    print(df)

if __name__ == "__main__":
    main()