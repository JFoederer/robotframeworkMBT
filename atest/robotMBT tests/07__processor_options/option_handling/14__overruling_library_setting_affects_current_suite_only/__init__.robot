*** Settings ***
Documentation     In this suite one of the processor options is set on the higher level suite,
...               which is then used in both sub suites. The first sub suite overrules the library
...               setting with their own value, the second library doesn't. The second suite should
...               be unaffected by the overruled option from the preceeding suite.
Suite Setup       Set model-based options    repeat=2
Library           robotmbt    processor_lib=suiterepeater
