# Zola

ZOLA := zola

all: build

preview:
	$(ZOLA) serve --drafts

build:
	$(ZOLA) build

clean:
	rm -rf public

push:
	git add .
	git commit -m "update website"
	git push origin main

.PHONY: all preview build clean push