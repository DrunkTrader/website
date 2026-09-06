# Zola

ZOLA := zola
PYTHON := python
PROJECTS_DATA := content/projects/data.toml
PROJECTS_DATA_TMP := $(PROJECTS_DATA).tmp

all: build

preview:
	$(ZOLA) serve --drafts

update-projects:
	$(PYTHON) scripts/fetch_all_github_projects.py > $(PROJECTS_DATA_TMP) && mv $(PROJECTS_DATA_TMP) $(PROJECTS_DATA)

build: update-projects
	$(ZOLA) build

clean:
	rm -rf public

push:
	git add .
	git commit -m "update website"
	git push origin main

.PHONY: all preview update-projects build clean push