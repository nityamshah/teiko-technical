.PHONY: setup pipeline dashboard clean
 
setup:
	pip install -r requirements.txt
 
pipeline: clean
	python load_data.py
	python analysis.py
 
dashboard:
	python dashboard.py
 
clean:
	rm -f *.csv *.png *.db * .txt