*** Settings ***
Suite Setup       Clear prior exports    ${OUTPUT_DIR}${/}run_model_with_graph.json
Library           ../graph_checker.py
