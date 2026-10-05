# ijt-resume.md is the source of truth. Edit it, then run `make`.

CHROME ?= $(shell command -v google-chrome-stable 2>/dev/null || echo "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")

all: index.html motion.html ijt-resume.pdf

index.html motion.html: ijt-resume.md template.html build.py motion.css motion.js
	python3 build.py

ijt-resume.pdf: index.html
	"$(CHROME)" --headless --disable-gpu --no-pdf-header-footer --print-to-pdf=$@ file://$(CURDIR)/$< 2>/dev/null

.PHONY: all
