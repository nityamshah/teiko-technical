.PHONY: setup pipeline dashboard clean

setup:
	pip install -r requirements.txt

pipeline:
	python load_data.py
	python analysis.py

dashboard:
	streamlit run dashboard.py --server.headless true --browser.gatherUsageStats false

clean:
	del database.db
	del cell_freq_summary.csv
	del statistical_analysis.csv
	del boxplot.png
	del part4_results.txt
	del melanoma_PBMC_samples_baseline.csv