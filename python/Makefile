
all:	
	echo "Targets are: builddoc, clean, cleandoc, cleanall, viewdoc"

builddoc:
	doxygen doxygen.cfg

clean:
	rm -f *~ .*~ *.pyc *.pyo
	rm -rf testreport
	rm -rf *_test.*

cleandoc:
	rm -rf doc

cleanall:
	make clean
	make cleandoc

viewdoc:
	htmlview ./doc/html/index.html &
