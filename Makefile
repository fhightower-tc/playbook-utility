clean:
	rm -rf venv && rm -rf *.egg-info && rm -rf dist && rm -rf *.log* && rm -fr .cache

venv:
	virtualenv -p python3 ~/.virtualenvs/http_request_playbook_creation_ui && . ~/.virtualenvs/http_request_playbook_creation_ui/bin/activate && pip3 install -r requirements.txt

run:
	~/.virtualenvs/http_request_playbook_creation_ui/bin/python http_request_playbook_creation_ui/http_request_playbook_creation_ui.py

test:
	~/.virtualenvs/http_request_playbook_creation_ui/bin/python -m unittest
