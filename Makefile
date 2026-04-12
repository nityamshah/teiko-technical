.PHONY: setup pipeline dashboard clean

setup:
	pip install -r requirements.txt

pipeline:
	python load_data.py
	python analysis.py

dashboard:
	streamlit run dashboard.py --server.headless true --browser.gatherUsageStats false
