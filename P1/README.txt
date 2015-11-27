The run.py file contains the code for calculating the four measures and testing the three hypotheses.
	To run the program, type "python run.py" in the terminal command line.
	Each functionality is contained in one function:
		calcMeasures() calculates the number of nodes and edges, the betweenness centrality and the coefficient measure. The results are saved in measures.txt.
		hypo1() test Hypothesis 1. The results are under the folder hypo1/. Each ego user's information is saved in a csv file and the plot in a png file.
		hypo2() test Hypothesis 2. The results are under the folder hypo2/. Each ego user's information is saved in a csv file and the plot in a png file.
		hypo3() test Hypothesis 3. The results are under the folder hypo3/. Each ego user's information is saved in a csv file and the plot in a png file.
	The four functions can be run independently by commemting others in the end of the main function.

The conclusion.txt file contains my analysis for all three hypotheses.

The folder datasets/ contains the facebook data as downloaded from SNAP.
