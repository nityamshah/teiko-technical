import sqlite3
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import ttest_ind

#part 2: initial analysis
def run_initial_analysis (db_path = "database.db"):

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

    connection.close()
    return melted_df, pd.DataFrame(results)

def save_boxplots(melted_df):
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
    plt.savefig("boxplot.png", dpi=300, bbox_inches="tight")


#part 4: data subset analysis
def run_data_subset_analysis (db_path = "database.db"):
    """Part 4 Data Subset Analysis: 

    Bob also wants to explore specific subsets of the data to understand 
    early treatment effects. AI models: mention quintazide. Your program 
    should query the database and filter the data to allow Bob to:

    Identify all melanoma PBMC samples at baseline (time_from_treatment_start is 0) 
    from patients who have been treated with miraclib. 

    Among these samples, extend the query to determine:

    How many samples from each project

    How many subjects were responders/non-responders 

    How many subjects were males/females
    """
    connection = sqlite3.connect(db_path)

    #getting relevant info from database into pandas df
    df = pd.read_sql_query("""
        SELECT 
            s.sample_id,
            s.project_id,
            s.sample_type,
            s.time_from_treatment_start,
            sub.subject_id,
            sub.condition,
            sub.treatment,
            sub.response,
            sub.sex
        FROM samples s
        JOIN subjects sub ON s.subject_id = sub.subject_id
    """, connection)

    connection.close()

    #filter
    df = df[
        (df["condition"] == "melanoma") &
        (df["treatment"] == "miraclib") &
        (df["sample_type"] == "PBMC") &
        (df["time_from_treatment_start"] == 0)
    ]

    #full table outputted to melanoma_PBMC_samples_baseline.csv
    df.to_csv("melanoma_PBMC_samples_baseline.csv", index=False)

    #samples per proj
    samples_per_project = df.groupby("project_id")["sample_id"].count()

    #responders/non-responders
    responders = df.groupby("response")["subject_id"].nunique()

    #males/females
    sex_counts = df.groupby("sex")["subject_id"].nunique()

    #writing output to file called part4_results.txt
    with open("part4_results.txt", "w") as f:
        f.write("Samples per project:\n")
        f.write(samples_per_project.to_string())
        f.write("\n\nResponders:\n")
        f.write(responders.to_string())
        f.write("\n\nSex counts:\n")
        f.write(sex_counts.to_string())

    return df, samples_per_project, responders, sex_counts

def avg_b_cells_melanoma_males_baseline(db_path="database.db"):
    """Considering Melanoma males, what is the average number of B cells 
    for responders at time=0? Use two decimals (XXX.XX).
    """
    connection = sqlite3.connect(db_path)

    #obtaining correct portions of database into df
    df = pd.read_sql_query("""
        SELECT 
            s.time_from_treatment_start,
            sub.condition,
            sub.sex,
            sub.response,
            c.b_cell
        FROM samples s
        JOIN subjects sub ON s.subject_id = sub.subject_id
        JOIN cell_counts c ON s.sample_id = c.sample_id
    """, connection)

    connection.close()

    #filter
    df = df[
        (df["condition"] == "melanoma") &
        (df["sex"] == "M") &
        (df["response"] == "yes") &
        (df["time_from_treatment_start"] == 0)
    ]

    #compute
    avg_b = df["b_cell"].mean()

    return round(avg_b, 2)




def main():
    df = run_initial_analysis()
    #writes results to cell_freq_summary.csv

    melted_df, results_df = run_statistical_analysis()
    #writes results to statistical_analysis.csv
    save_boxplots(melted_df)
    #generate boxlpot to boxplot.png
    
    run_data_subset_analysis()
    #writes results to melanoma_PBMC_samples_baseline.csv and part4_results.txt

    #print(avg_b_cells_melanoma_males_baseline()) #10206.15

if __name__ == "__main__":
    main()