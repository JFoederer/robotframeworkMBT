# RobotMBT Titanic demo

## What is it?

The purpose of this demo is to showcase the Model-Based Testing concepts available from the [RobotMBT](https://github.com/JFoederer/robotframeworkMBT) library using a [BDD](https://en.wikipedia.org/wiki/Behavior-driven_development) style project. It is based on the principle of [specification by example](https://en.wikipedia.org/wiki/Specification_by_example), using _given-when-then_ style scenarios.

Given-steps typically describe preconditions, i.e. state, but classically given-steps are implemented as actions to get to that desired precondition. Now, consider using [specification by example](https://en.wikipedia.org/wiki/Specification_by_example). If your specification is complete, and your examples are consistent, then any given-state must be reachable by operating the system within specification, following the examples. In this demo we use [RobotMBT](https://github.com/JFoederer/robotframeworkMBT) to specify a complete story, on varying levels of detail, using small consise scenarios. Then we let [RobotMBT](https://github.com/JFoederer/robotframeworkMBT) construct a complete storyline, so we don't have to worry about how to reach all the correct preconditions.

Please keep in mind that the library and this demo are still in the early development phases and offered functionality is still limited. However, in good agile spirit, we still wanted to publish the results.

## Contents of the demo - hit or miss?

Three different story lines can be played out in this demo, which are composed from small specification scenarios. The `miss` scenario reveils the story as it was expected to happen. Titanic is not fazed by any iceberg and safely travels to New York. The `hit` scenario resembles the plot that made the history books. The `extended` scenario extends the _miss_ scenario with multiple voyages and alternative routes.

There are a total of 7 scenarios in this demo, 10 if you use the extended variant. Some are very high level, stating functional or performance requirements on Titanic's voyage as a whole. Others are zoomed in to more detail, defining what the expectations are for the vessel when encountering icebergs along the way. Two scenarios are mutually exclusive, but with either one a complete voyage can be specified when combining it with the other available scenarios.

## Why the story of Titanic?

It might seem odd at first, seeing the [story of Titanic](https://en.wikipedia.org/wiki/Sinking_of_the_Titanic) in a context that is typically used in more technical environments. However, the [BDD](https://en.wikipedia.org/wiki/Behavior-driven_development) process is mostly non-technical and using a topic like Titanic helps to prevent technical bias. Another important point is that we want to stick to writing and maintaining short, to-the-point scenarios. From these, we want to compose larger scenarios, describing behaviour of complex systems, start to end, like telling a story. What better use for that than a well known story?

The [story of Titanic](https://en.wikipedia.org/wiki/Sinking_of_the_Titanic) fits these criteria and, since it already happened, there should be little discussion on the specification. It will be interesting to see if the test case generation mechanism from [RobotMBT](https://github.com/JFoederer/robotframeworkMBT) can reconstruct the familiar story, and then some variations thereof. After all, the maiden voyage of Titanic was just one example of what could have happened...

## Running the demo

### Step 1: Downloading the demo

* Navigate to the [project's main page on GitHb]((https://github.com/JFoederer/robotframeworkMBT/tree/main/demo/Titanic))
* Click the `<> Code ⏷` button
* select _Download ZIP_
* Extract the `demo/Titanic` folder from the downloaded ZIP
* Put the extracted folder at a convenient location

### Step 2: Installing dependencies

To install the packages needed to run the demo, navigate to your local `demo/Titanic` folder and run:

    pip install -r requirements.txt

### Step 3: Run the demo

To run the demo execute the `run_demo.py` script in either of the available variants:

    python run_demo.py miss
    python run_demo.py hit
    python run_demo.py extended

If you choose the `hit` scenario, don't be surprised if you encounter some failures along the route...

### Bonus: Play the demo as game

Can you safely cross Iceberg Alley and arrive in New York?  
Be the manual tester and play the game!

Instructions:

* Install matplotlib: `pip install matplotlib`
* Based on your system, install curses
  * for Windows: `pip install windows-curses`
  * for UNIX based systems it should work out of the box
* Navigate to your local `demo/Titanic` folder
* Run: `python run_game.py`
* A matplotlib window will appear, change focus back to your terminal to play the game.

**Tip**: If you enjoy the visual feedback, you can also enable it during the automated demo runs. To do so, update the suite setup in `Titanic_scenarios` to run a second keyword:

    *** Settings ***
    Suite Setup       Run keywords    Enable map animation    Treat this test suite model-based

## Project structure

In the root Titanic folder of this demo you will find 5 subfolders:

* **Behaviour documents** [`behaviour_docs`]  
This folder contains the resulting documents after iterating through the discovery and formulation phases of the BDD process. Steps #1 to #4 as described in this [article by Seb Rose](https://cucumber.io/blog/bdd/bdd-builds-momentum/). No automation involved yet.
* **Robot Framework scenarios** [`Titanic_scenarios`]  
Contains the scenarios from the behaviour documents in [Robot Framework](https://robotframework.org/) test suites, suitable for automation. This is the folder you open when using a test IDE, like [RIDE](https://github.com/robotframework/RIDE). (Add the root Titanic folder to PYTHONPATH)
* **Domain Specific Language** [`domain_lib`]  
The keyword-driven or action word based interface forms the [Domain Specific Language](https://en.wikipedia.org/wiki/Domain-specific_language) that allows the system under test and its environment to be operated and observed. In [keyword-driven testing](https://en.wikipedia.org/wiki/Keyword-driven_testing) test case are written using this language. In BDD-scenarios step definitions can be implemented using the action and observation keywords following the [Doobcheck principle](https://github.com/JFoederer/robotframeworkNL#doobcheck).
* **System Under Test** [`system`]  
In this demo the System Under Test is the Titanic and its crew, implemented as a virtual system.
* **Test environment** [`simulation`]  
In order to be able to execute [black-box](https://en.wikipedia.org/wiki/Black-box_testing) tests on the System Under Test, the system needs a controlled environment around it. For this demo we need, among others, control over icebergs.
