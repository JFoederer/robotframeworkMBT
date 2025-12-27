import jsonpickle
from robot.api.deco import keyword  # type:ignore
from robotmbt.visualise.models import TraceInfo, ScenarioInfo, StateInfo
from robotmbt.visualise.visualiser import Visualiser
import os


class ModelGenerator:
    @keyword(name='Generate Trace Information') # type:ignore
    def generate_trace_information(self) -> TraceInfo:
        return TraceInfo()

    @keyword(name='Current Trace Contains') # type:ignore
    def current_trace_contains(self, trace_info: TraceInfo, scenario_name: str, state_str: str) -> TraceInfo:
        '''
        State should be of format
        "name: key=value"
        '''
        scenario = ScenarioInfo(scenario_name)
        s = state_str.split(': ')
        key, item = s[1].split('=')
        state = StateInfo._create_state_with_prop(s[0], [(key, item)])
        trace_info.update_trace(scenario, state, trace_info.previous_length+1)

        return trace_info
    
    @keyword(name='All Traces Contains List') # type:ignore
    def all_traces_contains_list(self, trace_info: TraceInfo) -> TraceInfo:
        trace_info.all_traces.append([])
        return trace_info
    
    @keyword(name='All Traces Contains') # type:ignore
    def all_traces_contains(self, trace_info: TraceInfo, scenario_name: str, state_str: str) -> TraceInfo:
        '''
        State should be of format
        "name: key=value"
        '''
        scenario = ScenarioInfo(scenario_name)
        s = state_str.split(': ')
        key, item = s[1].split('=')
        state = StateInfo._create_state_with_prop(s[0], [(key, item)])
        
        trace_info.all_traces[0].append((scenario, state))

        return trace_info
    
    @keyword(name='Export Graph') # type:ignore
    def export_to_json(self, suite:str, trace_info: TraceInfo) -> str:
        return trace_info.export_graph(suite, True)
    
    @keyword(name='Import JSON File') # type:ignore
    def import_json_file(self, filepath: str) -> TraceInfo:
        with open(filepath, 'r') as f:
            string = f.read()
            decoded_instance = jsonpickle.decode(string)
        visualiser = Visualiser('state', trace_info=decoded_instance)
        return visualiser.trace_info

    @keyword(name='Check File Exists') # type:ignore
    def check_file_exists(self, filepath: str) -> str:
        '''
        Checks if file exists

        Returns string for .resource error message in case values are not equal
        Expected != result
        '''
        return 'file exists' if os.path.exists(filepath) else 'file does not exist'
    
    @keyword(name='Compare Trace Info') # type:ignore
    def compare_trace_info(self, t1: TraceInfo, t2: TraceInfo) -> str:
        '''
        Checks if current trace and all traces of t1 and t2 are equal

        Returns string for .resource error message in case values are not equal
        Expected != result
        '''
        succes = 'imported model equals exported model'
        fail = 'imported models differs from exported model'
        return  succes if repr(t1) == repr(t2) else fail
    
    @keyword(name='Delete File') # type:ignore
    def delete_json_file(self, filepath: str):
        os.remove(filepath)

