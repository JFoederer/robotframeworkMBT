*** Settings ***
Documentation     In this suite one of the processor options is set on the higher level suite,
...               which is then reused in both sub suites. Each sub suite adds their own value
...               for a second configuration option.
Suite Setup       Set model-based options    repeat=2
Library           robotmbt    processor_lib=suiterepeater
