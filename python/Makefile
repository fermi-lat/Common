
all:	
	echo "Targets are: doc, clean, cleandoc, view"

doc:
	doxygen doxygen.cfg

cleandoc:
	rm -rf doc

clean:
	rm -f *~ .*~ *.pyc *.pyo

view:
	htmlview ./doc/html/index.html &
