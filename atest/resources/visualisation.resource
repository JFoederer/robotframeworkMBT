*** Settings ***
Documentation     Resource file for testing the visualisation of RobotMBT
Library           atest.resources.helpers.modelgenerator.ModelGenerator
Library           Collections


*** Keywords ***
test suite ${suite} has trace info ${trace}
    [Documentation]     *model info*
    ...     :IN: new trace_info | trace_info.current_trace=0 | trace_info.all_traces=0 | 
    ...     trace_info.name = ${trace} | new graph
    ...     :OUT: None
    ${trace_info} =     Generate Trace Information
    Set Suite Variable  ${trace_info}

trace info ${trace}
        [Documentation]     *model info*
    ...     :IN: trace_info.name == ${trace}
    ...     :OUT: trace_info.name == ${trace}
    No operation

the algorithm inserts '${scenario_name}' with state "${state_str}"
    [Documentation]    *model info*
    ...    :IN: trace_info
    ...    :OUT: trace_info.current_trace+=1
    Variable Should Exist    ${trace_info}
    ${trace_info} =    The Algorithm Inserts    ${trace_info}    ${scenario_name}    ${state_str}

test suite ${suite} has ${n} steps in its current trace 
    [Documentation]    *model info*
    ...    :IN: trace_info.current_trace==${n}
    ...    :OUT: trace_info.current_trace==${n}
    No operation

test suite ${suite} has ${n} total traces
    [Documentation]    *model info*
    ...    :IN: trace_info.current_trace | trace_info.all_traces==${n}-1
    ...    :OUT: trace_info.current_trace | trace_info.all_traces==${n}-1
    No operation

${graph_type} graph ${name} is generated
    [Documentation]    *model info*
    ...    :IN: trace_info
    ...    :OUT: graph.name=${name} | graph.type=${graph_type}
    Variable Should Exist    ${trace_info}

    ${graph} =  Generate Graph   ${trace_info}   ${graph_type}
    ${network_visualiser} =    Generate Network Graph    ${graph}
    Set Suite Variable  ${graph}
    Set Suite Variable  ${network_visualiser}

graph ${name} contains vertex '${scenario}'
    [Documentation]    *model info*
    ...    :IN: graph.name==${name}
    ...    :OUT: graph.name==${name}
    Variable Should Exist    ${graph}

    ${id} =     Get NodeID      ${graph}        ${scenario}
    ${result} =     Graph Contains Vertex With No Text        ${graph}      ${id}
    Run Keyword If      ${result} == False
    ...    Fail     Fail: Graph does not contain '${scenario}'

graph ${name} contains vertex '${scenario}' with text "${text}"
    [Documentation]    *model info*
    ...    :IN: graph.name==${name}
    ...    :OUT: graph.name==${name}
    Variable Should Exist    ${graph}

    ${result} =     Graph Contains Vertex With Text        ${graph}      ${scenario}       ${text}
    Run Keyword If      "${result}" == "None"
    ...    Fail     Fail: Graph does not contain '${scenario}' with "${text}"

graph ${name} does not contain vertex '${scenario}'
    [Documentation]    *model info*
    ...    :IN: graph.name==${name}
    ...    :OUT: graph.name==${name}
    Variable Should Exist    ${graph}

    ${id} =     Get NodeID      ${graph}        ${scenario}
    ${result} =     Graph Contains Vertex With No Text        ${graph}      ${id}
    Run Keyword If      "${result}" != "None"
    ...    Fail     Fail: Graph contains '${scenario}'"

graph ${name} does not contain vertex '${scenario}' with text "${text}"
    [Documentation]    *model info*
    ...    :IN: graph.name==${name}
    ...    :OUT: graph.name==${name}
    Variable Should Exist    ${graph}

    ${result} =     Graph Contains Vertex With Text        ${graph}      ${scenario}       ${text}
    Run Keyword If      "${result}" != "None"
    ...    Fail     Fail: Graph contains '${scenario}' with "${text}"
    
graph ${name} has an edge from '${start_title}' to '${end_title}'
    [Documentation]    *model info*
    ...    :IN: graph.name==${name}
    ...    :OUT: graph.name==${name}
    Variable Should Exist    ${graph}
    ${start_node} =    Graph Contains Vertex With Text    ${graph}    ${start_title}
    ${end_node} =    Graph Contains Vertex With Text    ${graph}    ${end_title}
    
    Should Not Be Equal    ${start_node}    ${None}    Start node with title '${start_title}' not found
    Should Not Be Equal    ${end_node}    ${None}    End node with title '${end_title}' not found
    
    ${result} =    Vertices Are Connected    ${graph}    ${start_node}    ${end_node}
    Run Keyword If    ${result} != True
    ...     Fail    Fail: Edges '${start_title}' and '${end_title}' exist in graph but are not connected!

graph ${name} does not have an edge from '${start_title}' to '${end_title}'
    [Documentation]    *model info*
    ...    :IN: graph.name==${name}
    ...    :OUT: graph.name==${name}
    Variable Should Exist    ${graph}
    ${start_node} =    Graph Contains Vertex With Text    ${graph}    ${start_title}
    ${end_node} =    Graph Contains Vertex With Text    ${graph}    ${end_title}
    
    ${result} =    Vertices Are Connected    ${graph}    ${start_node}    ${end_node}
    Run Keyword If    ${result} == True
    ...     Fail    Fail: Edges '${start_title}' and '${end_title}' exist in graph and are connected, but shouldn't be!

graph ${name} has vertices ${vertices_string}
    [Documentation]    *model info*
    ...    :IN: graph.name==${name}
    ...    :OUT: graph.name==${name}
    Variable Should Exist    ${graph}
    ${result} =    Graph Contains Vertices Starting With   ${graph}    ${vertices_string}
    Run Keyword If    ${result} != True
    ...    Fail    Graph did not contain all vertices ${vertices_string}

vertex '${start_vertex}' is placed above '${end_vertex}'
    [Documentation]    *model info*
    ...    :IN: None
    ...    :OUT: None
    Variable Should Exist    ${graph}
    Variable Should Exist    ${network_visualiser}
    ${node1} =      Get NodeID      ${graph}    ${start_vertex}
    
    Run Keyword If    "${node1}" == "None"
    ...    Fail    Vertex '${start_vertex}' does not exist

    ${node2} =      Get NodeID      ${graph}    ${end_vertex}

    Run Keyword If    "${node2}" == "None"
    ...    Fail    Vertex '${end_vertex}' does not exist

    ${result1} =    Get Vertex Y position   ${network_visualiser}    ${node1}
    ${result2} =    Get Vertex Y position   ${network_visualiser}    ${node2}
    
    Run Keyword If    ${result1} < ${result2}
    ...    Fail    Vertex '${start_vertex}' is below '${end_vertex}'

the algorithm backtracks by ${n} step(s)
    [Documentation]    *model info*
    ...    :IN: trace_info.current_trace >= ${n}
    ...    :OUT: trace_info.current_trace-=${n} | trace_info.all_traces+=1
    Variable Should Exist    ${trace_info}

    ${a} =      Get Length Current Trace        ${trace_info}
    ${b} =      Get Number of Backtracked Traces        ${trace_info}

    ${trace_info} =     Backtrack       ${trace_info}       ${n}

    ${i} =      Get Length Current Trace        ${trace_info}
    ${j} =      Get Number of Backtracked Traces        ${trace_info}

    Run Keyword If      ${a} - ${n} != ${i}
    ...    Fail     Fail: Backtracking did not shorten current trace correctly

    Run Keyword If      ${b} + 1 != ${j}
    ...    Fail     Fail: Backtracking did not add new trace to all traces

test suite ${suite} is exported to json
    [Documentation]     *model info*
    ...     :IN: trace_info.current_trace, trace_info.all_traces>0
    ...     :OUT: new filepath
    Variable Should Exist   ${suite}
    Variable Should Exist   ${trace_info}
    
    ${filepath} =   Export Graph      ${suite}    ${trace_info}
    Set Suite Variable  ${filepath}

the file ${filename} exists
    [Documentation]     *model info*
    ...     :IN: filepath
    ...     :OUT: filepath 
    Variable Should Exist   ${filepath}

    ${result} =     Check File Exists   ${filepath}
    Run Keyword If    ${result} == False
    ...     Fail    Fail: File does not exist

${filename} is imported
    [Documentation]     *model info*
    ...     :IN: filepath
    ...     :OUT: new new_trace_info
    Variable Should Exist   ${filepath}
    
    ${new_trace_info} =     Import Graph   ${filepath}
    Set Suite Variable      ${new_trace_info}

trace info from ${filename} is the same as trace info ${trace}
    [Documentation]     *model info*
    ...     :IN: new_trace_info, trace_info
    ...     :OUT: new flag_cleanup
    Variable Should Exist   ${trace_info}
    Variable Should Exist   ${new_trace_info}

    ${result} =     Compare Trace Info   ${trace_info}      ${new_trace_info}
    Run Keyword If    ${result} == False
    ...     Fail    Fail: Exported and Imported trace info are not the same

${file} has been imported
    [Documentation]     *model info*
    ...     :IN: flag_cleanup
    ...     :OUT: flag_cleanup
    No operation

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
        Run Keyword If    ${result} == True
    ...     Fail    Fail: File exist