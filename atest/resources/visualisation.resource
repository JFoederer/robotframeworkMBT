*** Settings ***
Documentation     Resource file for testing the visualisation of RobotMBT
Library           atest.resources.helpers.modelgenerator.ModelGenerator
Library           Collections


*** Keywords ***
test suite ${suite}
    [Documentation]     *model info*
    ...     :IN: None
    ...     :OUT: new suite
    Set Suite Variable  ${suite}

test suite ${suite} has trace info ${trace}
    [Documentation]     *model info*
    ...     :IN: suite
    ...     :OUT: new trace_info
    Variable Should Exist    ${suite}

    ${trace_info} =         Generate Trace Information
    Set Suite Variable  ${trace_info}
    
trace info ${trace} has current trace ${current}
    [Documentation]     *model info*
    ...     :IN: trace_info
    ...     :OUT: trace_info.current_trace=[]
    Variable Should Exist    ${trace_info}

current trace ${current_trace} has a tuple 'scenario ${scenario}, state ${state}'
    [Documentation]    *model info*
    ...     :IN: trace_info.current_trace
    ...     :OUT: trace_info.current_trace.append((${scenario}, ${state}))
    Variable Should Exist   ${trace_info}

    ${trace_info} =         Current Trace Contains  ${trace_info}   ${scenario}     ${state}
    Set Suite Variable  ${trace_info}

trace info ${trace} has all traces ${all}
    [Documentation]     *model info*
    ...     :IN: trace_info
    ...     :OUT: trace_info.all_traces=[]
    Variable Should Exist    ${trace_info}

all traces ${all} has list ${list}
    [Documentation]    *model info*
    ...     :IN: trace_info
    ...     :OUT: trace_info.all_traces.append([])
    Variable Should Exist   ${trace_info}

    ${trace_info} =         All Traces Contains List  ${trace_info}
    Set Suite Variable  ${trace_info}

list ${list} has a tuple 'scenario ${scenario}, state ${state}'
    [Documentation]    *model info*
    ...     :IN: trace_info.all_traces
    ...     :OUT: trace_info.all_traces.append((${scenario}, ${state}))
    Variable Should Exist   ${trace_info}

    ${trace_info} =         All Traces Contains  ${trace_info}   ${scenario}     ${state}
    Set Suite Variable  ${trace_info}

test suite ${suite} contains trace info ${ti}
    [Documentation]     *model info*
    ...     :IN: suite, trace_info
    ...     :OUT: suite, trace_info
    Variable Should Exist   ${suite}
    Variable Should Exist   ${trace_info}

test suite ${suite} is exported to json
    [Documentation]     *model info*
    ...     :IN: suite, trace_info
    ...     :OUT: new filepath
    Variable Should Exist   ${suite}
    Variable Should Exist   ${trace_info}
    
    ${filepath} =   Export Graph      ${suite}    ${trace_info}
    Set Suite Variable  ${filepath}

the file ${filename} exists
    [Documentation]     *model info*
    ...     :IN: suite, filepath
    ...     :OUT: suite, filepath 
    Variable Should Exist   ${filepath}

    ${result} =     Check File Exists   ${filepath}
    Should Be Equal     ${result}   file exists

${filename} is imported
    [Documentation]     *model info*
    ...     :IN: suite, filepath
    ...     :OUT: new new_trace_info
    Variable Should Exist   ${filepath}
    
    ${new_trace_info} =     Import JSON File    ${filepath}
    Set Suite Variable      ${new_trace_info}

trace info from ${filename} is the same as trace info ${trace}
    [Documentation]     *model info*
    ...     :IN: new_trace_info, trace_info
    ...     :OUT: new flag_cleanup
    Variable Should Exist   ${trace_info}
    Variable Should Exist   ${new_trace_info}

    ${result} =     Compare Trace Info   ${trace_info}      ${new_trace_info}
    Should Be Equal     ${result}   imported model equals exported model

${filename} is deleted
    [Documentation]     *model info*
    ...     :IN: filepath
    ...     :OUT: filepath
    Variable Should Exist   ${filepath}
    
    Delete File    ${filepath}

${filename} does not exist
    [Documentation]     *model info*
    ...     :IN: filepath
    ...     :OUT: filepath
    Variable Should Exist   ${filepath}

    ${result} =     Check File Exists   ${filepath}
    Should Be Equal     ${result}   file does not exist

flag cleanup is set
    [Documentation]     *model info*
    ...     :IN: suite
    ...     :OUT: suite
    Set Suite Variable      ${flag_cleanup}     True

flag cleanup has been set
    [Documentation]     *model info*
    ...     :IN: flag_cleanup
    ...     :OUT: flag_cleanup
    Variable Should Exist   ${flag_cleanup}
