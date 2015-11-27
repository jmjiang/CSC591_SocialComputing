The application requires the separate running of two python scripts: runListener.py and post.py:
runListener.py:
	Keeps listening for new posts on Twitter;
	Replies to relevant posts automatically, e.g. replying to neighbors' check-in messages answering calls, and giving feedback to neighbors
post.py:
	Post check-in updates
	Post call-request updates

To run the application:
	1. In a terminal window/tab (terminal1), enter "python runListener.py" in the command line to start running runListener.py
	2. Open a new terminal window/tab (terminal2), enter "python post.py" in the command line to start running post.py
	3. In terminal2, after the prompt, enter one of the followings (including the quotation marks): "hunt", "eb2", "carmichael", "oval", "party". The check-in update will be posted in the correct format. (DO NOT terminate the process)
	4. In terminal1, it will show the information that "My check-in message is received". And the location and neighbors' responses to my check-in are also shown.
	5. In terminal2, after the prompt, enter "call". The call-request update will be posted in the correct format.
	6. In terminal1, the calls and my responses to the calls are shown. (Neighbors' feedbacks would be too many to be shown.) And the recalculated utility is displayed.
	7. 1-6 can be repeated.
	8. To terminated the program, press 'Ctrl-C' in terminal1 and terminal2.

All the relevant posts will be saved in a json file called "myprefix.<date><time>.json".
