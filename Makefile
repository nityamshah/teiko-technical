.PHONY: setup pipeline dashboard clean

setup:
	pip install -r requirements.txt

pipeline:
	python load_data.py
	python analysis.py

dashboard:
	streamlit run dashboard.py

clean:
	del *.csv
	del *.png
	del *.db