# teiko-technical

to run this code: 
- clean up existing files with make clean (optional)
- make sure you have the requirements in requirements.txt 
    - (make setup or pip install -r requirements.txt)
- load the data and run the analysis 
    - (make pipeline or python load_data.py followed by python analysis.py)
    - database created will be called database.db
    - outputs will be generated in the following files 
        - cell_freq_summary.csv
        - statistical_analysis.csv
        - boxplot.png
        - part4_results.txt
        - melanoma_PBMC_samples_baseline.csv
- set up dashboard 
    - (make dashboard or streamlit run dashboard.py --server.headless true --browser.gatherUsageStats false)

schema explanation: 
    I organized this relational database schema to the implicit hierarchies in the clinical trial
    data given. By this I mean, theres a couple of projects, each with individual patients, 
    each with multiple samples over time, each with cell counts for the five populations.
    So, to represent this, I split the database into four tables (projects, subjects, samples, and cell_counts) connected by the appropriate foreign keys. I chose to split the data instead
    of having one big table for clarity, less repetition/reduncancy, and so this data scales well. 
    This scales well because the separate tables allow for faster lookup, ease of adding and 
    removing samples or populations or variables, and efficient filtering and no duplication.

code structure: 
    The code structure has three main components. load_data.py builds the SQLite database
    from the csv file. analysis.py is sectioned into three parts. part 2 (immune cell frequency summaries), part 3 (statistical comparisons between responders and non-responders) and part 4
    (subset based clinical analysis). Finally, dashboard.py builds an interactive streamlit 
    dashboard based on the results of parts 1-4. I designed it this way so different parts are 
    reusable, its easy to debug, and easy to extend.

dashboard link: http://localhost:8501