.PHONY: venv install lint test run-hybrid

venv:
	python3 -m venv .venv

install:
	. .venv/bin/activate && pip install -r requirements.txt

test:
	. .venv/bin/activate && PYTHONPATH=. pytest -q

run-local:
	. .venv/bin/activate && PYTHONPATH=. python -m src.pipeline.main --mode local

run-hybrid:
	. .venv/bin/activate && PYTHONPATH=. python -m src.pipeline.main --mode hybrid

run-cloud:
	. .venv/bin/activate && PYTHONPATH=. python -m src.pipeline.main --mode cloud

lint:
	. .venv/bin/activate && python -m compileall src

airflow-install:
	. .venv/bin/activate && export AIRFLOW_VERSION=2.9.3 && export PYTHON_VERSION="$$(python --version | cut -d " " -f 2 | cut -d "." -f 1-2)" && export CONSTRAINT_URL="https://raw.githubusercontent.com/apache/airflow/constraints-$${AIRFLOW_VERSION}/constraints-$${PYTHON_VERSION}.txt" && pip install "apache-airflow==$${AIRFLOW_VERSION}" --constraint "$${CONSTRAINT_URL}"

airflow-init:
	. .venv/bin/activate && export AIRFLOW__CORE__DAGS_FOLDER=$$(pwd)/dags && export PYTHONPATH=$$(pwd) && airflow db migrate

airflow-run:
	. .venv/bin/activate && export AIRFLOW__CORE__DAGS_FOLDER=$$(pwd)/dags && export PYTHONPATH=$$(pwd) && export AIRFLOW__WEBSERVER__WEB_SERVER_PORT=8081 && airflow standalone