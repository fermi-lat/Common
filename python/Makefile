
all:	
	echo "Targets are: doxygen, clean, cleandoc, cleanall, viewdoc"

doxygen:
	doxygen doxygen.cfg

cleandoc:
	rm -rf doc

clean:
	rm -f *~ .*~ *.pyc *.pyo
	rm -rf testreport

cleanall:
	make clean
	make cleandoc

viewdoc:
	htmlview ./doc/html/index.html &
