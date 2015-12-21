Running SikuliX-based Scripts(Windows 7)-NOT FINAL
What you need:
Python 2.7-
	Google appropriate installer, download and install. Add Python to your path so
	you can use it from the command line. Go to Control Panel\System and Security\System,
	and click Advanced System Settings -> Environment Variables -> Edit 'Path' ->
	add C:\Python27\; or wherever you installed Python to the string using semicolons
	to separate it from the other values. Now when you use the windows command
	line(start menu -> search 'cmd' -> enter) when you type 'python' it should
	enter into the python prompt. exit() exits it.

Java-
	Similar to Python setup, but with Java. Latest version is fine. Don't bother
	with Path stuff if java works in the command line after install.

Pip-
	Package manager for python. Save https://bootstrap.pypa.io/get-pip.py as get-pip.py,
	open cmd and change your working directory to wherever you have saved the
	file using 'cd (the path to containing folder)', then run python get-pip.py

Chemspipy-
	ChemSpider package for Python. 'python -m pip install chemspipy' in cmd.

SikuliX-
	Grab the jar at https://launchpad.net/sikuli/sikulix/1.1.0
	Move it to an empty folder wherever you want sikuli to be installed. C:\SikuliX
	or ...\Users\You \SikuliX are appropriate since it's a library.
	Click it and install Packages 1 and 2.

EPI WEB 4.1, T.E.S.T, VegaNIC 1.1.0-
	You probably have these already. Different versions may break the script if
	the buttons or workflow is different.

Python Scripts-
	Unzip the included zip file to the relevant place in your documents folder.
	Open up configuration.txt and modify the paths to match your installation paths.
	Make sure to use double \\, as \ is an escape character in Python.

Running the Script:
	Inputs go into inputs.txt separated by line. They can be smiles, CAS or common
	names, but common names can get a little wonky. Make sure configuration.txt
	has been updated with the proper paths and options. Open EPI Suite, Vega and TEST.
	They must NOT be be minimized and must be fully within the bounds of the screen. Open
	cmd and navigate to the script folder using cd. Run 'python main.py'
	and wait. Outputs	should be in the designated output folder.
