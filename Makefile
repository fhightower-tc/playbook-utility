clean:
	rm -rf venv && rm -rf *.egg-info && rm -rf dist && rm -rf *.log* && rm -fr .cache && rm -fr .pytest_cache

# deep-clean:
# 	rm -rf ./static/app_images/* && rm -rf ./static/components_images/* && rm -rf ./static/components/* && rm -rf ./static/playbooks_images/* && rm -rf ./static/playbooks/*

venv:
	virtualenv -p python3 ~/.virtualenvs/playbook-utility && . ~/.virtualenvs/playbook-utility/bin/activate && pip3 install -r requirements.txt

run:
	~/.virtualenvs/playbook-utility/bin/python playbook_utility/playbook_utility.py

test:
	~/.virtualenvs/playbook-utility/bin/python -m pytest
