# robotframeworkMBT - the oneliner

 Model-based testing in Robot framework with test case generation

## Introduction

This project is an extension to [Robot framework](https://robotframework.org/) for model-based testing. The term model-based testing, or MBT in short, has been used in many different ways. Within this context two modelling aspects are most important. The first is about domain modelling using a domain specific language, or DSL. [Robot framework](https://robotframework.org/) already has great support for this aspect, which is why it was used as a base. The second aspect is about test case generation.

Test case generation introduces a more dynamic approach to executing a test suite. A typical traditional test suite is executed front to back. For maintainability reasons, test cases are often kept independent of each other. The down side to this approach is that there is little variation and often a lot of duplication, mostly during the setup phases.

With this project we aim to get the best of both worlds. Allowing testers to write small, independent cases that are automatically combined. Finding more issues in less time, by focusing on effectively reaching the desired coverage.

## Installation

The recommended installation method is using [pip](http://pip-installer.org)

    pip install robotframework-mbt

After installation include `robotmbt` as library in your robot file to get access to the new functionality.

## Capabilities

Current capabilities focus around complete scenarios. When all steps are properly annotated with modelling info, the library can resolve their dependencies to figure out the correct execution order. To be successful, the set of scenarios in the model must be composable into a single complete sequence, without repetitions or leftovers.

To get a feel for what this library can do, have a look at our [Titanic themed demo](https://github.com/JFoederer/robotframeworkMBT/tree/main/demo/Titanic). Please note that this library is in a premature state and hasn't reached its first official release yet. Developments are ongoing within the context of the [TiCToC](https://tictoc.cs.ru.nl/) research project.
