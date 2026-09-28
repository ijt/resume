ijt-resume.pdf: index.html
	google-chrome-stable --headless --disable-gpu --no-pdf-header-footer --print-to-pdf=$@ file://$(CURDIR)/$< 2>/dev/null

ijt-resume-md.pdf: ijt-resume.md
	pandoc -s -o $@ $<
