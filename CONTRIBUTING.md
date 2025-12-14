# Contribution guidelines RobotMBT

Thank you for considering to contribute to this project. Welcome! Your contribution already starts when you use this software and share your experience with the people around you. The [Robot Framework Slack](http://slack.robotframework.org/) channels are good place to share, ask questions and if you can, answer them.

If you want to get involved on GitHub, you can so by submitting issues or offering code improvements. These guidelines will help you to find your way. These guidelines expect readers to have a basic knowledge about open source as well as why and how to contribute to an open source project. If you are new to these topics, please have a look at the generic [Open Source Guides](https://opensource.guide/) first.

## Code of conduct

If you want to be part of this community, then we expect you to respect our norms and values. These are in line with the [GitHub code of conduct](https://docs.github.com/en/site-policy/github-terms/github-community-code-of-conduct) and the [Slack code of conduct](https://docs.slack.dev/community-code-of-conduct/). In short, we expect you to:

- Be welcoming.
- Be kind.
- Look out for each other.

## Submitting issues

Defects and enhancements are tracked in the [issue tracker](https://github.com/JFoederer/robotframeworkMBT/issues). Take care to narrow down any issue to this project before submitting an issue here. RobotMBT cannot fix your computer! If you are unsure if something is worth submitting, you can first ask on [Slack](http://slack.robotframework.org/). Before submitting a new issue, it is always a good idea to check if something similar was already reported. If it is, please add your comments to the existing issue instead of creating a new one. Communication in issues on GitHub is done in English.

Take notice that issues do not get resolved by themselves. Someone will need to spend time on the topic. Be prepared to wait, contribute yourself or arrange budget to hire someone for the job.

### Reporting defects

When reporting a defect, be precise and concise in your description and write in way that helps others understand, and preferably reproduce, the issue. Screenshots can be very helpful, but when adding logging or other textual information, please keep the textual form.

Note that all information in the issue tracker is public. Do not include any confidential information there.

Be sure to add information about:

- The applicable version(s) of RobotMBT (use `pip list` and check for `robotframework-mbt`)
- Your Robot Framework version (use `pip list` and check for `robotframework`)
- Your Python version (check using `python --version`)
- Your Operating System
- Used custom settings for RobotMBT (at library and test suite level)

Version information about Robot Framework, Python and the Operating System are also reported at the start of Robot's `output.xml` file.

### Enhancement requests

When proposing an enhancement, a feature request, be clear about the use cases. Who will benefit from the enhancement and in what way? Describe the expected behaviour and use concrete examples to illustrate the intent.

## Code contributions

If you have fixed a defect or implemented an enhancement, you can contribute your changes via [GitHub's pull requests](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request). This is not restricted to code, on the contrary, fixes and enhancements to documentation and tests alone are also very valuable! 

### first steps

- [Clone](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository) and/or [Fork](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/about-forks) the RobotMBT repo. If you are not a fan of command line tools, [GitHub Desktop](https://github.com/apps/desktop) can help you.
- [Run the tests](#running-tests) to check your starting point.
- Write new failing tests to cover your intended changes.
- Implement your changes.

### Definition of Done

The Definition of Done is there to ensure that pull requests are fully self-contained, and leave no open ends. In other words: When the pull request is merged, it is 100% done. This keeps the main branch ready for release, at all times.

That means that for each pull request you need to ensure:

- No regression is introduced.
- New functionality is covered by tests.
- Code style follows the standard.
- Documentation is up to date.
- The PR branch is 0 commits behind.

### Running tests

Tests can be executed from the command line by running `python run_tests.py`. This will run all unit tests, followed by the Robot acceptance tests. Use `--help` for additional info.

### Non-regression criteria

The criteria for proving non-regression are:

- All automated regression tests pass
- All supported Python, Robot Framework and OS versions still work (see `pyproject.toml` for supported versions).
- The [demos](https://github.com/JFoederer/robotframeworkMBT/tree/main/demo/Titanic) still work.
- Manual checks are executed to cover the automation's blind spots and subjective elements (e.g. some visual inspection on layout and assessing overall look and feel).

### Guidelines for writing new tests

For this project we are not maintaining separate requirements documentation. The user documentation explains the software's purpose and scope, the tests further specify its concrete behaviour. Keep this in mind when writing tests and pay extra attention to documenting your test cases. They are more than just bug catchers. If code exists due to a technical limitation rather than a requirement, be sure to document your design decision.

Tests are located in the _atest_ and _utest_ folders, which stands for _acceptance test_ and _unit test_ respectively. The acceptance tests are Robot tests that cover user-visible behaviour using black box testing techniques. They typically do not cover all details, unless some Robot Framework interaction is involved. The unit tests do go in depth, which includes white box techniques to include coverage on the dark corners of the code. Choose the right type of test for what you are covering.

A specific challenge for this project is that there is a lot of test case generation going on. Take care that variations in the generation process can not alter the intended coverage of a test and do not yield false positives. False positives being pass results without proof for passing, like checking 'all' results in an empty list. And lastly, keep the resulting number of test cases in a run deterministic, so that we keep comparable results.

### Coding style

Maintainability is the main driver for coding style. Always write your code with the mindset that you are writing it for someone else, and that this person's experience level is slightly below the average in the project. Code is written following the [PEP 8](https://peps.python.org/pep-0008) Style guide and [SOLID](https://en.wikipedia.org/wiki/SOLID) principles.

#### Formatting

Formatting follows the default rules of [autopep8](https://pypi.org/project/autopep8/) with the exception that the maximum line length is set to 120. Note however, that the extended line length is not an invite to always write long lines.

Researchers have suggested [[ref.](https://www.academia.edu/6232736/The_influence_of_font_type_and_line_length_on_visual_search_and_information_retrieval_in_web_pages)] that longer lines are better suited for cases when the information will likely be scanned, while shorter lines (45-75 characters) are appropriate when the information is meant to be read thoroughly. Keep this in mind when writing code and documentation, taking the current indentation level into account.

#### Docstrings, comments and logging

Docstrings are written using a black box approach. One should not need to know the inside of a class or function in order to use it. Use comments to annotate code for maintainers. Prevent trivial comments and use descriptive names to make your code self-explanatory. When documenting external interfaces, also check whether the user documentation requires an update.

Useful information that is runtime dependent should be logged. Information that is useful after a passing test run is logged at info-level. Information that is useful for analysing failed tests is logged at debug-level. Be careful not to make assumptions in what you log. Recheck log statements if your changes affect the context in which the code is run. Only report about what you know to be true.
