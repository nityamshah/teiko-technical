import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt

from analysis import (
    run_initial_analysis,
    run_statistical_analysis,
    run_data_subset_analysis
)

st.title("Immune Cell Analysis Dashboard")

tab1, tab2, tab3 = st.tabs(["Part 2", "Part 3", "Part 4"])

#part 2
with tab1:
    st.header("Cell Frequency Summary")

    df2 = run_initial_analysis()

    st.dataframe(df2)

    st.download_button(
        "Download Part 2 CSV",
        data=df2.to_csv(index=False),
        file_name="cell_freq_summary.csv",
        mime="text/csv"
    )

#part 3
with tab2:
    st.header("Responder vs Non-Responder Analysis")

    df3, results_df = run_statistical_analysis()

    fig, ax = plt.subplots()

    sns.boxplot(
        data=df3,
        x="population",
        y="percentage",
        hue="response",
        ax=ax
    )

    plt.xticks(rotation=45)
    st.pyplot(fig)

    st.subheader("Significant Differences (t-test results)")

    results_df = run_statistical_analysis()  # make sure this returns the results table

    st.dataframe(results_df)

    significant = results_df[results_df["significant"] == True]["population"].tolist()

    st.write("### Cell populations with significant differences:")
    st.write(significant)

    st.caption("Statistical results saved in statistical_analysis.csv")

#part 4
with tab3:
    st.header("Subset Analysis")

    df4, samples_per_project, responders, sex_counts = run_data_subset_analysis()

    st.subheader("Melanoma PBMC Baseline Samples (Miraclib, t=0)")
    st.dataframe(df4)   

    st.subheader("Samples per project")
    st.dataframe(samples_per_project)

    st.subheader("Responders vs Non-Responders")
    st.dataframe(responders)

    st.subheader("Sex distribution")
    st.dataframe(sex_counts)

    st.download_button(
        "Download Part 4 Results",
        data=open("part4_results.txt").read(),
        file_name="part4_results.txt",
        mime="text/plain"
    )