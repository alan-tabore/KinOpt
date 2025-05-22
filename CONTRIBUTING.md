Community Guidelines for KinOpt

Welcome to the KinOpt community! This project is open to contributors from all backgrounds, and we aim to foster a collaborative and respectful environment focused on chemical kinetics and kinetic modeling.

This document provides clear guidance for third parties who wish to:

⸻

1. Contribute to the Software

We welcome contributions that improve the functionality, performance, or usability of KinOpt. If you would like to contribute:
	•	For most users with a chemical kinetics background, your primary interest will likely be in adding new kinetic models. These should be added to the file:
kinopt/src/kinetic_models.py
	•	When adding a model:
	•	Create a function named in the format:
rate_for_[name_of_the_model]
	•	The first two arguments must be:
	•	extent: extent of reaction
	•	T: temperature of the reaction
	•	Any additional arguments should correspond to user input parameters.
	•	Please ensure your code is:
	•	Well-documented
	•	Properly tested (include tests if possible)
	•	Consistent with the existing codebase and style
	•	Submit contributions via a Pull Request on GitHub:
https://github.com/alan-tabore/KinOpt

⸻

2. Report Issues or Problems

We encourage users to report bugs, unexpected behavior, or any other problems with the software.
	•	Please check the Issues page to see if your concern has already been raised.
	•	When reporting a new issue:
	•	Be clear and concise
	•	Include your operating system, Python version, and KinOpt version
	•	If possible, provide a minimal reproducible example

⸻

3. Seek Support

If you need help using KinOpt or understanding how to contribute:
	•	Feel free to open a discussion or issue on the GitHub page:
https://github.com/alan-tabore/KinOpt
	•	When asking for help:
	•	Describe your problem clearly
	•	Include relevant code or context
	•	Be respectful of the maintainers’ time

⸻

General Conduct

While our community is primarily technical, we expect all interactions to remain professional and respectful. Disruptive or abusive behavior will not be tolerated.