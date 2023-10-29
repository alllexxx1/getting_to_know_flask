start:
	flask --app mvp --debug run --port 8000

start-public:
	flask --app mvp --debug run --host=0.0.0.0

start-gunicorn:
	python3 -m gunicorn --workers=4 --bind=127.0.0.1:8000 mvp:app
