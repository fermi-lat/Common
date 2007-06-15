
all:	
	echo "Targets are: doc, clean, cleandoc, view"

doc:
	doxygen doxygen.cfg

cleandoc:
	rm -rf doc

clean:
	rm -f *~ .*~ *.pyc *.pyo
	rm -f pGEMcontribution.py 
	rm -f pTKRcontributionIterator.py
	rm -f pCALcontributionIterator.py
	rm -f pAEMcontributionIterator.py
	rm -f output.xml
	rm -f test.root

view:
	htmlview ./doc/html/index.html &
