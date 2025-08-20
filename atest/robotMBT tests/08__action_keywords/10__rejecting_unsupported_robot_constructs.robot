*** Settings ***
Documentation     Currently only linear sequential scenarios are supported for modelling. When
...               other constructs are used, the modelling should fail and report an error message.
...               Note that contrary to most failure detection scenarios, this sceanrio is not
...               skipped after detecting the failure. When modelling fails, the scenario is kept
...               as-is. The way this scenario is constructed allows it to pass as a regular
...               action-driven test. No modelling is needed to successfully complete the checks.
Suite Setup       Run keyword and expect error    *Robot construct not supported*    Treat this test suite Model-based
Resource          ../../resources/birthday_cards_action-driven.resource
Library           robotmbt

*** Test Cases ***
Modelling fails if unsupported Robot constructs are used
    Buy a birthday card
    VAR    @{name list}=    Johan    Frederique
    FOR    ${name}    IN    @{name list}
        Write name '${name}' on the birthday card
    END
    ${n_names}=    Number of names written on the birthday card
    Should be equal    ${n_names}    ${2}
