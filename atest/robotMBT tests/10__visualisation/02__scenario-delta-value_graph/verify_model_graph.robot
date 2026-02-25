*** Settings ***
Documentation     This suite takes the graph generated in the first suite in this folder
...               and checks how the content's properties for the scenario-delta-value
...               graph are different compared to the scenario graph.
Library           ../graph_checker.py
Library           Collections
Suite Setup       Import graph data from    ${OUTPUT_DIR}${/}run_model_with_graph.json    graph_type=scenario-delta-value

*** Test Cases ***
Repeated scenario with different states become separate nodes
    [Documentation]    In the standard scenario graph, the repeated scenario would show up
    ...                as a self-looping edge. In the scenario-delta-value variant, also
    ...                state changes are taken into account, meaning that the two variants
    ...                will each get their own node.
    ${node_count}=    Number of graph nodes
    Should be true    ${node_count} > ${4}
    @{all_nodes}=    List of node titles
    Should contain    ${all_nodes}     Someone writes their name on the card
    Should contain    ${all_nodes}     Someone writes their name on the card (rep 2)

Full node text contains state info
    [Documentation]    Next to the scenario name, the node text for scenario-delta-value graphs
    ...                also contians information about the model state. 'Buying a card'
    ...                initialises the modeland contains all properties in their initial state.
    ...                'host' and 'names' are properties being tracked by the model.
    ${full_text}=    Full node text of node     Buying a card
    Should contain    ${full_text}   host
    Should contain    ${full_text}   names

Full node text only contains changed information
    [Documentation]    When someone writes their name on the card, then the host or celebrant
    ...                does not change. The node for this scenario should only show the state
    ...                that changed during this scenario.
    ${full_text}=    Full node text of node     Someone writes their name on the card (rep 2)
    Should contain    ${full_text}   names
    Should not contain    ${full_text}   host
