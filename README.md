# robotframeworkMBT - the oneliner

 Model-based testing in Robot framework with test case generation

## Introduction

This project is an extension to [Robot framework](https://robotframework.org/) for model-based testing. The term model-based testing, or MBT in short, has been used in many different ways. Within this context two modelling aspects are most important. The first is about domain modelling using a domain specific language, or DSL. [Robot framework](https://robotframework.org/) already has great support for this aspect, which is why it was used as a base. The second aspect is about test case generation.

Test case generation introduces a more dynamic approach to executing a test suite. A typical traditional test suite is executed front to back. For maintainability reasons, test cases are often kept independent of each other. The down side to this approach is that there is little variation and often a lot of duplication, mostly during the setup phases.

With this project we aim to get the best of both worlds. Allowing testers to write small, independent cases that are automatically combined. Finding more issues in less time, by focusing on effectively reaching the desired coverage.

## Capabilities

RobotMBT is suitable for sequencing complete scenarios, including action refinement for when-steps. Concrete example scenarios can be generalised for added data-driven variation. When all steps are properly annotated with modelling info, the library can resolve their dependencies and figure out the correct execution order. Each run a new trace is generated from the available options.

To be successful, the set of scenarios in the model must (for now) be composable into a single complete sequence, without leftovers. The same scenario can be inserted multiple times if repetition helps to reach the entry condition for later scenarios.

## Getting started

To get a feel for what this library can do, have a look at our [Titanic themed demo](https://github.com/JFoederer/robotframeworkMBT/tree/main/demo/Titanic), which is executable as a [Robot framework](https://robotframework.org/) test suite.

The recommended installation method is using [pip](http://pip-installer.org)

    pip install --upgrade robotframework-mbt

After installation include `robotmbt` as library in your robot file to get access to the new functionality. To run your test suite model-based, use the __Treat this test suite model-based__ keyword as suite setup. Check the _How to model_ section to learn how to make your scenarios suitable for running model-based.

```
*** Settings ***
Library        robotmbt
Suite Setup    Treat this test suite model-based
```

## How to model

Modelling can be done directy from [Robot framework](https://robotframework.org/), without the need for additional tooling. The popular _Given-When-Then_ style is used to capture behaviour in scenarios, following the Specification by example approach.

### The basics

Consider these two scenarios:

```
Buying a postcard
    When you buy a new postcard
    then you have a blank postcard

Preparing for a birthday party
    Given you have a blank postcard
    When you write 'Happy birthday!' on the postcard
    then you are ready to go to the birthday party
```

Mapping the dependencies between scenarios is done by annotating the steps with modelling info. Modelling info is added to the documentation of the step as shown below. Regular documentation can still be added, as long as `*model info*` starts on a new line and a whiteline is included after the last `:OUT:` expression.

```
you buy a new postcard
    [Documentation]    *model info*
    ...    :IN: None
    ...    :OUT: new postcard

you have a blank postcard
    [Documentation]    *model info*
    ...    :IN: postcard.wish == None
    ...    :OUT: postcard.wish= None

you write '${your_wish}' on the postcard
    [Documentation]    *model info*
    ...    :IN: postcard.wish == None
    ...    :OUT: postcard.wish= ${your_wish}
```

The first scenario has no dependencies and can be executed at any time. This is evident from the fact that the scenario does not have any given-steps. From the `*model info*` we see that no dependencies need to be resolved before going into the first step: _When you buy a new postcard_. This is indicated by the `:IN:` condition which is `None`. After completing the step, a new domain term is available, `postcard`, as a result of the `:OUT:` statement `new postcard`. The following then-step adds detail to the postcard by adding a property. Setting `postcard.wish=None` in the `:OUT:` statement indicates that _you have a blank postcard_.

The second scenario has a dependency to the first scenario, due to the given-step: _Given you have a blank postcard_. This is expressed by the `:IN:` expression stating that you need a postcard, that does not have a wish on it yet. How this works, is by evaluating the expressions according to this schema:

* given-steps evaluate only the `:IN:` expressions
* when-steps evaluate both the `:IN:` and `:OUT:` expressions
* then-steps evaluate only the `:OUT:` expressions

If evaluation of any expression fails or is False, then the scenario cannot be executed at the current position. By properly annotating all steps to reflect their impact on the system or its environment, you can model the intended relations between scenarios. This forms the specification model. The step implementations use keywords to connect to, and interact with, the system under test. The keywords perform actions and check outputs to verify the specified behaviour.

There are three typical kinds of steps:

* __Action__  
  When-steps perform an action on the system that alters its state. These steps can have dependencies stated in their `:IN:` conditions that are needed before starting the action. Statements in the `:OUT:` expressions indicate what changes are expected by executing this action.
* __Stative__  
  Stative steps express a truth value. Like, _you have a blank postcard_. For these steps the `:IN:` expression is a condition. The `:OUT:` part is either identical to the `:IN:` condition or a statement. If the when-action already sets the property, then you use a condition in the `:OUT:` part. Statements, like assigning a new property, are useful to express the result of a scenario. For instance to express indirect effects of an action, or when the result of an action depends on the given system state. The step implementation of stative steps consists purely of checks.
* __Refinement__  
  Action refinement allows you to build hierarchy into your scenarios. The `:IN:` and `:OUT:` expressions are only conditions (checks), but the `:IN:` and `:OUT:` expressions are different. If for any step the `:OUT:` expression is reached for evaluation, but fails, this signals the need for refinement. A single full scenario can be inserted if all `:IN:` conditions match at the current position and the pending `:OUT:` conditions are satisfied after insertion.

### Keeping your models clean

Clean models start with tidy model info. If multiple expressions are needed you can separate them in the `*model info*` by using the pipe symbol (`|`) or by starting the next expression on a new line. A single expression cannot be split over multiple lines. Try to keep expressions simple. If expressions start becoming complex, maybe the model data needs an update.

Choosing the right model data is essential. It defines how your steps and scenarios interact. A good aproach is to do a domain analysis and organise your model data to reflect the structure of the domain. Choosing the right domain terms will make your life a lot easier when debugging modelling errors. Keep ownership local, so that only a relatively small amount of steps create and modify the data within a certain domain term.

You can keep your models small by deleting domain terms that are no longer relevant (e.g. `del postcard`). For local data, scenario variables can be used. Similar to regular domain terms, you have access to the predefined term `scenario`. Any properties assigned to `scenario` are automatically cleared at the end of the scenario.

Scenario variables can be especially useful under refinement. If a when-step is being refined by another scenario, both scenarios are _open_. This enables communication between these scenarios. The refining scenario has access to, and can modify, scenario variables of the refined scenario. If the refining scenario introduces new properties, these are removed once the refinement completes and are no longer available to the refined scenario.

## Disclaimer

Please note that this library is in a premature state and hasn't reached its first official (1.0) release yet. Developments are ongoing within the context of the [TiCToC](https://tictoc.cs.ru.nl/) research project. Interface changes are still frequent and no deprecation warnings are being issued yet.
