# RobotMBT - the oneliner

 Model-based testing in Robot framework with test case generation

## Introduction

This project is an extension to [Robot framework](https://robotframework.org/) for model-based testing. The term model-based testing, or MBT in short, has been used in many different ways. Within this context two modelling aspects are most important. The first is about domain modelling using a domain specific language, or DSL. [Robot framework](https://robotframework.org/) already has great support for this aspect, which is why it was used as a base. The second aspect is about test case generation.

Test case generation introduces a more dynamic approach to executing a test suite. A typical traditional test suite is executed front to back. For maintainability reasons, test cases are often kept independent of each other. The downside to this approach is that there is little variation and often a lot of duplication, mostly during the setup phases.

With this project we aim to get the best of both worlds. Allowing testers to write small, independent scenarios that are automatically combined and expanded. Finding more issues in less time, by focusing on effectively reaching the desired coverage.

## Approach

The popular _Given-When-Then_ style is used to capture behaviour in scenarios, following the Specification by example approach. In Specification by example, you specify a system by writing down the minimum set of key examples to clearly convey the intended behaviour of the system. As a tester you need to go beyond these examples and verify that the system behaves as intended for the broader expressed intent. Roughly speaking this implies that variations need to be tested covering two axis: _when_ and _what_.

The _when_ is about sequencing and entry conditions. When, or in which exact state, do you start a scenario? Given-steps define the entry condition for a scenario, which can be less or more specific. The less specific the condition is, the more situations there are in which the specified behaviour should hold. It can be challenging to find and select a good set of concrete situations to use as a starting point. We build on the assumption that, for a well specified system, any scenario's entry condition can be reached via a sequence of other scenarios. There can be many valid and relevant variations to do so.

The _what_ reflects on the fact that examples are just that, examples. There can be many more, equally valid examples. As a tester you want to explore the available options and confirm that the system functions as expected under all possible operating conditions.

RobotMBT offers features to cover both _when_ and _what_ variations.

## Capabilities

RobotMBT is suitable for sequencing complete scenarios, including action refinement for when-steps. Concrete example scenarios can be generalised for added data-driven variation. When all steps are properly annotated with modelling info, the library can resolve their dependencies and figure out the correct execution order. Each run a new test sequence is generated from the available options.

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

Modelling can be done directly from [Robot framework](https://robotframework.org/), without the need for additional tooling besides [RobotMBT](https://github.com/JFoederer/robotframeworkMBT).

### The basics

Consider these two scenarios:

```
Buying a postcard
    When you buy a new postcard
    then you have a blank postcard

Preparing for a birthday party
    Given you have a blank postcard
    When you write 'Happy birthday!' on the postcard
    then the postcard is a birthday card
```

Mapping the dependencies between scenarios is done by annotating the steps with modelling info. Modelling info is added to the documentation of the step as shown below. Regular documentation can still be added, as long as `*model info*` starts on a new line and a white line is included after the last `:OUT:` expression.

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

Note: Action keywords, i.e. keywords without one of these prefixes, behave as when-steps.

If evaluation of any expression fails or is False, then the scenario cannot be executed at the current position. By properly annotating all steps to reflect their impact on the system or its environment, you can model the intended relations between scenarios. This forms the specification model. The step implementations use keywords to connect to, and interact with, the system under test. The keywords perform actions and check outputs to verify the specified behaviour.

There are three typical kinds of steps:

* __Action__  
  When-steps perform an action on the system that alters its state. These steps can have dependencies stated in their `:IN:` conditions that are needed before starting the action. Statements in the `:OUT:` expressions indicate what changes are expected by executing this action.
* __Stative__  
  Stative steps express a truth value. Like, _you have a blank postcard_. For these steps, the `:IN:` expression is a condition. The `:OUT:` part is either identical to the `:IN:` condition or a statement. If the when-action already sets the property, then you use a condition in the `:OUT:` part. Statements, like assigning a new property, are useful to express the result of a scenario. For instance, to express indirect effects of an action, or when the result of an action depends on the given system state. The step implementation of stative steps consists purely of checks.
* __Refinement__  
  Action refinement allows for hierarchy in scenarios by delegating implementation of a when-step to another scenario. The `:IN:` and `:OUT:` expressions of the when-step contain conditions (checks), but the `:IN:` and `:OUT:` expressions contradict. A single full scenario can be inserted to resolve the contradiction. For a scenario to be a valid refinement, all `:IN:` conditions must match at the current position and the pending `:OUT:` conditions must be satisfied after insertion. The step implementation should check and confirm the end state of the system under test after refinement.

### Keeping your models clean

Clean models start with tidy model info. If multiple expressions are needed, you can separate them in the `*model info*` by using the pipe symbol (`|`) or by starting the next expression on a new line. A single expression cannot be split over multiple lines. Try to keep expressions simple. If expressions start becoming complex, maybe the model data needs an update.

Choosing the right model data is essential. It defines how your steps and scenarios interact. A good approach is to do a domain analysis and organise your model data to reflect the structure of the domain. Choosing the right domain terms will make your life a lot easier when debugging modelling errors. Keep ownership local, so that only a relatively small number of steps create and modify the data within a certain domain term.

You can keep your models small by deleting domain terms that are no longer relevant (e.g. `del postcard`). For local data, scenario variables can be used. Similar to regular domain terms, you have access to the predefined term `scenario`. Any properties assigned to `scenario` are automatically cleared at the end of the scenario.

Scenario variables can be especially useful under refinement. If a when-step is being refined by another scenario, both scenarios are _open_. This enables communication between these scenarios. The refining scenario has access to, and can modify, scenario variables of the refined scenario. If the refining scenario introduces new properties, these are removed once the refinement completes and are no longer available to the refined scenario.

### Variable data

All example scenarios naturally contain data. This information is embedded in their steps. Step definitions typically have arguments that allow you to write different sets of examples, reusing the same step definitions. RobotMBT offers _step modifiers_ that leverages this to generate new examples on the fly.

#### Step argument modifiers

```
Personalising a birthday card
    Given there is a birthday card
    when Johan writes their name on the birthday card
    then the birthday card has a personal touch
```

The above scenario uses the name `Johan` to create a concrete example. But now suppose that from a testing perspective `Johan` and `Frederique` are part of the same equivalence class. Then the step `Frederique writes their name on the birthday card` would yield an equally valid scenario. This can be achieved by adding a modifier (`:MOD:`) to the model info of the step. The format of a modifier is a Robot argument to which you assign a list of options. The modifier updates the argument value to a randomly chosen value from the specified options.

```
${person} writes their name on the birthday card
    [Documentation]    *model info*
    ...    :MOD: ${person}= [Johan, Frederique]
    ...    :IN:  birthday_card
    ...    :OUT: birthday_card.name= ${person}
```

#### Multiple modifiers

When constructing examples, they often express relations between multiple actors, where each actor can appear in multiple steps. This makes it important to know how modifiers behave when there are multiple modifiers in a scenario.

```
Addressing a birthday card
   Given Tannaz is having their birthday
   and Johan has a birthday card
   when Johan writes the address of Tannaz on the birthday card
   then the birthday card is ready to be send
```

Have a look at the when-step above. We will assume the model already contains a domain term with two properties: `birthday.celebrant = Tannaz` and `birthday.guests = [Johan, Frederique]`.

```
${sender} writes the address of ${receiver} on the birthday card
    [Documentation]    *model info*
    ...    :MOD: ${sender}= birthday.guests
    ...          ${receiver}= [birthday.celebrant]
    ...    :IN:  birthday_card | scenario.sender= ${sender}
    ...    :OUT: birthday_card.addressee == ${receiver}
```

When a step has multiple arguments, any of them can have a modifier. Arguments without a modifier will keep the value from the scenario text. Modifiers are separated by a pipe symbol (`|`) or by starting on a new line. Each modifier is assigned a list of options. Since `birthday.guests` is already a list, it can be use directly. List comprehensions are an easy way to filter out relevant options from a larger list. The scalar value `Tannaz` for the celebrant is turned into a list using the square brackets (`[ ]`).

If an example value is used multiple times in a scenario, like `Johan` in the above scenario, then RobotMBT makes sure that all modifiers referring to this example value are combined. So, given `Frederique` has the birthday card, then `Frederique` will also write the address, because the respective given- and when-steps refer to the same example value. There must be at least one example value that is a valid option for each of the steps in order to generate a scenario.

The opposite is also true. Any example values that differ in the original scenario text, are guaranteed to get distinct values in the generated scenario. That means that in the above example, where `Johan` sends a card to `Tannaz`, you can be sure that the generated scenario will not include a variant where `Tannaz` sends a birthday card to herself, even if `Tannaz` were a valid option for both arguments. If, however, this is a relevant scenario for you, you can include it as a new key example in your test suite.

Modifiers can be used on any type of argument: embedded, positional or named. If an argument is optional and it is ommitted in the scenario, then the argument's default value is used and the modifier is not triggered. Passing a variable number of arguments using modifiers is supported for both varargs and free named arguments. The modifier must yield a list vor varargs or a dict for free named arguments. They are used directly as-is without matching against other arguments. Just like optional arguments, when no arguments are provided, the modifier is not triggered.

#### Technicalities

Please note that all modifiers in the scenario are processed before processing the regular `:IN:` and `:OUT:` expressions. This implies that when model data is used in a modifier, that it will use the model data as it is at the start of the scenario. Any updates to the model data during the scenario steps do not affect the possible choices for the example values.

It is possible to use the argument value itself as one of the options. Using the actual argument as the only option (e.g. `:MOD: ${receiver}= [${receiver}]`) can force all other steps into a specific option, chosen directly from the scenario. For this to work, the single option must be a valid option for all steps using the same example value.

It is not possible to add new options to an existing example value. Any constraints set by a previous modifier still hold, meaning that any new option values will not fit that constraint and will be filtered out. Adding the same option value multiple times to a single option list has no affect.

It is possible for a step to keep the same options. The special `.*` notation lets you keep the available options as-is. Preceding steps must then supply the possible options. Some steps can, or must, deal with multiple independent sets of options that must not be mixed, because the expected results should differ. Suppose you have a set of valid and invalid passwords. You might be reluctant to include the superset of these as options to an authentication step. Instead, you can use `:MOD: ${password}= .*` as the modifier for that step. Like in the when-step for this scenario:

```
Given 'secret' is too weak a password
When user tries to update their password to 'secret'
then the password is rejected
```

In a then-step, modifiers behave slightly different. In then-steps no new option constraints are accepted for an argument. Its value must already have been determined during the given- and when-steps. In other words, regardless of the actual modifier, the expression behaves as if it were `.*`. The exception to this is when a then-step signals the first use of a new example value. In that case the argument value from the original scenario text is used.

#### Limitations

For now, variable data considers strict equivalence classes only. This means that all variants are considered equal for all purposes. If, for a certain scenario, a single valid example variant has been generated and executed, then this scenario is considered covered. There are no options yet to indicate deeper coverage targets based on data variations. It also implies that whenever any variant is valid, all scenario variants must be valid. And that regardless of which variant is chosen, the exact same scenarios can be chosen as the next one. This does however not mean that once a variant is chosen, that this variant will be used throughout the whole trace. If a scenario is selected multiple times in the same trace, then each occurrence will get new randomly selected data.

## Configuration options

### Random seed

By default, trace generation is random. The random seed used for the trace is logged by _Treat this test suite model-based_. This seed can be used to rerun the same trace, if no external random factors influence the test run. To activate the seed, pass it as argument:

```
Treat this test suite model-based    seed=eag-etou-cxi-leamv-jsi
```

Using `seed=new` will force generation of a new reusable seed and is identical to omitting the seed argument. To completely bypass seed generation and use the system's random source, use `seed=None`. This has even more variation but does not produce a reusable seed.

### Option management

If you want to set configuration options for use in multiple test suites without having to repeat them, the keywords __Set model-based options__ and __Update model-based options__ can be used to configure RobotMBT library options. _Set_ takes the provided options and discards any previously set options. _Update_ allows you to modify existing options or add new ones. Reset all options by calling _Set_ without arguments. Direct options provided to __Treat this test suite model-based__ take precedence over library options and affect only the current test suite.

Tip: [Robot dictionaries](https://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#dictionary-variable) (`&{ }`) can be used to group related options and pass them as one set.


### Graphs

By default, no graphs are generated for test-runs. For development purposes, having a visual representation of the test-suite you are working on can be very useful. To have robotmbt generate a graph, ensure you have installed the optional dependencies (`pip install .[visualization]`) and pass the type as an argument:

```
Treat this test suite Model-based  graph=[type]
```

Here, `[type]` can be any of the supported graph types. Currently, the types included are:
- `scenario-delta-value`

Once the test suite has run, a graph will be included in the test's log, under the suite's `Treat this test suite Model-based` setup header.

#### JSON exporting

It is possible to extract the exploration data after the library has found a covering trace. To enable this feature, set the following argument to true:

```
Treat this test suite Model-based  export_graph_data=[directory]
```

A JSON file named after the test suite will be created containing said information.

#### JSON importing

It is possible to skip running the exploration step and produce a graph (e.g. of another type) from previously exported data.

```
Treat this test suite Model-based  graph=[type]  import_graph_data=[directory+file_name.json]
```

A graph will be created from the imported data.

### Option management

If you want to set configuration options for use in multiple test suites without having to repeat them, the keywords __Set model-based options__ and __Update model-based options__ can be used to configure RobotMBT library options. _Set_ takes the provided options and discards any previously set options. _Update_ allows you to modify existing options or add new ones. Reset all options by calling _Set_ without arguments. Direct options provided to __Treat this test suite model-based__ take precedence over library options and affect only the current test suite.

Tip: [Robot dictionaries](https://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#dictionary-variable) (`&{ }`) can be used to group related options and pass them as one set.

## Contributing

If you have feedback, ideas, or want to get involved in coding, then check out the [Contribution guidelines](https://github.com/JFoederer/robotframeworkMBT/blob/main/CONTRIBUTING.md).

## Disclaimer

Please note that this library is in a premature state and hasn't reached its first official (1.0) release yet. Developments are ongoing within the context of the [TiCToC](https://tictoc.cs.ru.nl/) research project. Interface changes are still frequent, and no deprecation warnings are being issued yet.
