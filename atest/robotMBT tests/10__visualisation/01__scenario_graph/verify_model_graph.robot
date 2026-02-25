*** Settings ***
Documentation     This suite takes the graph generated in the first suite in this folder
...               and checks the content's properties.
Library           ../graph_checker.py
Library           Collections
Suite Setup       Import graph data from    ${OUTPUT_DIR}${/}run_model_with_graph.json

*** Test Cases ***
Scenarios are nodes in the graph
    VAR    @{expected_nodes}    start
    ...                         Buying a card
    ...                         Someone writes their name on the card
    ...                         At least 3 people can write their name on the card
    ${node_count}=    Number of graph nodes
    Should be equal    ${node_count}    ${4}
    @{all_nodes}=    List of node titles
    Lists should be equal    ${all_nodes}    ${expected_nodes}    ignore_order=True

Dependent nodes are connected by directed edges
    @{successors}=    All successors to node    Buying a card
    VAR    @{next_node}     Someone writes their name on the card
    Should be equal    ${successors}    ${next_node}
    @{successors}=    All successors to node    Someone writes their name on the card
    Should not contain    ${successors}    Buying a card

The dependency order for nodes is top-down
    ${first_pos}=    Vertical position of node    Buying a card
    ${second_pos}=    Vertical position of node    Someone writes their name on the card
    Should be true    ${second_pos} < ${first_pos}

Repeating scenarios have a self-looping edge
    @{successors}=    All successors to node    Someone writes their name on the card
    Should contain    ${successors}    Someone writes their name on the card
