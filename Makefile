install:
	python -m pip install -r requirements.txt

lock:
	uv lock

install-locked:
	uv sync --frozen

lint:
	python -m compileall -q src api app

quality:
	pytest -q --disable-warnings

smoke:
	python scripts/smoke_test.py

benchmark:
	python scripts/benchmark.py

validate-release:
	python scripts/validate_release.py

profile:
	python -m src.universal.cli profile $(FILE)

app:
	streamlit run app/streamlit_app.py

api:
	uvicorn api.main:app --host 0.0.0.0 --port 8000

docker-up:
	docker compose up --build

pipeline: quality smoke

retail-pipeline:
	python -m src.data.download_uci
	python -m src.retail.prepare
	python -m src.retail.snapshots
	python -m src.retail.train

powerbi-demo:
	python -m src.universal.v4_cli powerbi --input data/processed/model_dataset.csv --output reports/powerbi --entities customerID --date tenure

release:
	$(MAKE) quality
	$(MAKE) smoke
	$(MAKE) benchmark
	$(MAKE) validate-release
