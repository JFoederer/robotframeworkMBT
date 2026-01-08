*** Settings ***
Documentation     In this suite one of the processor options is set on the higher level suite,
...               which is then reused in both sub suites. The first sub suite adds their own value
...               for a second configuration option, the second suite does not use that option at
...               all. The second suite should be unaffected by the option set in the preceeding
...               suite.
Suite Setup       Set model-based options    repeat=2
Library           robotmbt    processor_lib=suiterepeater
