install:
	python -m pip install -U pip
	python -m pip install -r requirements.txt

api:
	python -m uvicorn proctoring_assistant.api:app --host 0.0.0.0 --port 8000

ui:
	python -m streamlit run proctoring_assistant/ui.py

test:
	python -m pytest -q
