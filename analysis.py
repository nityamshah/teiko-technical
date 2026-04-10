import sqlite3
import pandas as pd

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
def run_analysis():

    return

def main():
    df = compute_frequency_table()
    print("Printing head of summary table from part 2:\n")
    print(df.head()) # print head of summary

    run_analysis()

if __name__ == "__main__":
    main()