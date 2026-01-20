# -*- coding: utf-8 -*-

# BSD 3-Clause License
#
# Copyright (c) 2022, J. Foederer
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import copy
import random
from typing import Any

from robot.api import logger

from . import modeller
from .modelspace import ModelSpace
from .suitedata import Suite, Scenario
from .tracestate import TraceState

try:
    from .visualise.visualiser import Visualiser
    from .visualise.models import TraceInfo

    visualisation_deps_present = True
except ImportError:
    Visualiser = None
    TraceInfo = None
    visualisation_deps_present = False


class SuiteProcessors:
    @staticmethod
    def echo(in_suite):
        return in_suite

    def flatten(self, in_suite: Suite) -> Suite:
        """
        Takes a Suite as input and returns a Suite as output. The output Suite does not
        have any sub-suites, only scenarios. The scenarios do not have a setup. Any setup
        keywords are inserted at the front of the scenario as regular steps.
        """
        out_suite = copy.deepcopy(in_suite)
        outer_scenarios = out_suite.scenarios
        for scenario in outer_scenarios:
            if scenario.setup:
                scenario.steps.insert(0, scenario.setup)
                scenario.setup = None
            if scenario.teardown:
                scenario.steps.append(scenario.teardown)
                scenario.teardown = None

        out_suite.scenarios = []
        for suite in in_suite.suites:
            subsuite = self.flatten(suite)
            for scenario in subsuite.scenarios:
                if subsuite.setup:
                    scenario.steps.insert(0, subsuite.setup)
                if subsuite.teardown:
                    scenario.steps.append(subsuite.teardown)
            out_suite.scenarios.extend(subsuite.scenarios)

        out_suite.scenarios.extend(outer_scenarios)
        out_suite.suites = []
        return out_suite

    def process_test_suite(self, in_suite: Suite, *, seed: Any = 'new', graph: str = '',
                           to_json: bool = False, from_json: str = 'false') -> Suite:
        self.out_suite = Suite(in_suite.name)
        self.out_suite.filename = in_suite.filename
        self.out_suite.parent = in_suite.parent
        self._fail_on_step_errors(in_suite)
        self.flat_suite = self.flatten(in_suite)

        if from_json != 'false':
            self._load_graph(graph, in_suite.name, from_json)

        else:
            self._run_test_suite(seed, graph, in_suite.name, to_json)

        self.__write_visualisation()

        return self.out_suite

    def _load_graph(self, graph: str, suite_name: str, from_json: str):
        traceinfo = TraceInfo()
        traceinfo = traceinfo.import_graph(from_json)
        self.visualiser = Visualiser(graph, suite_name, trace_info=traceinfo)

    def _run_test_suite(self, seed: Any, graph: str, suite_name: str, to_json: bool):
        for id, scenario in enumerate(self.flat_suite.scenarios, start=1):
            scenario.src_id = id
        self.scenarios = self.flat_suite.scenarios[:]
        logger.debug("Use these numbers to reference scenarios from traces\n\t" +
                     "\n\t".join([f"{s.src_id}: {s.name}" for s in self.scenarios]))

        self._init_randomiser(seed)
        self.shuffled = [s.src_id for s in self.scenarios]
        random.shuffle(self.shuffled)  # Keep a single shuffle for all TraceStates (non-essential)

        self.visualiser = None
        if graph != '' and visualisation_deps_present:
            try:
                self.visualiser = Visualiser(graph, suite_name, to_json)
            except Exception as e:
                self.visualiser = None
                logger.warn(f'Could not initialise visualiser due to error!\n{e}')

        elif graph != '' and not visualisation_deps_present:
            logger.warn(f'Visualisation {graph} requested, but required dependencies are not installed. '
                        'Refer to the README on how to install these dependencies. ')

        # a short trace without the need for repeating scenarios is preferred
        tracestate = self._try_to_reach_full_coverage(allow_duplicate_scenarios=False)

        if not tracestate.coverage_reached():
            logger.debug("Direct trace not available. Allowing repetition of scenarios")
            tracestate = self._try_to_reach_full_coverage(allow_duplicate_scenarios=True)
            if not tracestate.coverage_reached():
                raise Exception("Unable to compose a consistent suite")

        self.out_suite.scenarios = tracestate.get_trace()

    def _try_to_reach_full_coverage(self, allow_duplicate_scenarios: bool) -> TraceState:
        tracestate = TraceState(self.shuffled)
        while not tracestate.coverage_reached():
            candidate_id = tracestate.next_candidate(retry=allow_duplicate_scenarios)
            self.__update_visualisation(tracestate)
            if candidate_id is None:  # No more candidates remaining for this level
                if not tracestate.can_rewind():
                    break
                tail = modeller.rewind(tracestate)
                logger.debug(f"Having to roll back up to {tail.scenario.name if tail else 'the beginning'}")
                self._report_tracestate_to_user(tracestate)
                self.__update_visualisation(tracestate)
            else:
                candidate = self._select_scenario_variant(candidate_id, tracestate)
                if not candidate:  # No valid variant available in the current state
                    tracestate.reject_scenario(candidate_id)
                    self.__update_visualisation(tracestate)
                    continue
                previous_len = len(tracestate)
                modeller.try_to_fit_in_scenario(candidate, tracestate)
                self.__update_visualisation(tracestate)
                self._report_tracestate_to_user(tracestate)
                if len(tracestate) > previous_len:
                    logger.debug(f"last state:\n{tracestate.model.get_status_text()}")
                    self.DROUGHT_LIMIT = 50
                    if self.__last_candidate_changed_nothing(tracestate):
                        logger.debug("Repeated scenario did not change the model's state. Stop trying.")
                        modeller.rewind(tracestate)
                        self.__update_visualisation(tracestate)
                    elif tracestate.coverage_drought > self.DROUGHT_LIMIT:
                        logger.debug(f"Went too long without new coverage (>{self.DROUGHT_LIMIT}x). "
                                     "Roll back to last coverage increase and try something else.")
                        modeller.rewind(tracestate, drought_recovery=True)
                        self.__update_visualisation(tracestate)
                        self._report_tracestate_to_user(tracestate)
                        logger.debug(f"last state:\n{tracestate.model.get_status_text()}")
        return tracestate

    def __update_visualisation(self, tracestate: TraceState):
        if self.visualiser is not None:
            try:
                self.visualiser.update_trace(tracestate)
            except Exception as e:
                logger.warn(f'Could not update visualisation due to error!\n{e}')

    def __write_visualisation(self):
        if self.visualiser is not None:
            try:
                logger.info(self.visualiser.generate_visualisation(), html=True)
            except Exception as e:
                logger.warn(f'Could not generate visualisation due to error!\n{e}')

    @staticmethod
    def __last_candidate_changed_nothing(tracestate: TraceState) -> bool:
        if len(tracestate) < 2:
            return False
        if tracestate[-1].id != tracestate[-2].id:
            return False
        return tracestate[-1].model == tracestate[-2].model

    def _select_scenario_variant(self, candidate_id: int, tracestate: TraceState) -> Scenario:
        candidate = self._scenario_with_repeat_counter(candidate_id, tracestate)
        candidate = modeller.generate_scenario_variant(candidate, tracestate.model or ModelSpace())
        return candidate

    def _scenario_with_repeat_counter(self, index: int, tracestate: TraceState) -> Scenario:
        """
        Fetches the scenario by index and, if this scenario is already
        used in the trace, adds a repetition counter to its name.
        """
        candidate = next(s for s in self.scenarios if s.src_id == index)
        rep_count = tracestate.count(index)
        if rep_count:
            candidate = candidate.copy()
            candidate.name = f"{candidate.name} (rep {rep_count + 1})"
        return candidate

    @staticmethod
    def _fail_on_step_errors(suite: Suite):
        error_list = suite.steps_with_errors()

        if error_list:
            err_msg = "Steps with errors in their model info found:\n"
            err_msg += '\n'.join([f"{s.keyword} [{s.model_info['error']}] used in {s.parent.name}"
                                  for s in error_list])
            raise Exception(err_msg)

    @staticmethod
    def _report_tracestate_to_user(tracestate: TraceState):
        user_trace = f"[{', '.join(tracestate.id_trace)}]"
        logger.debug(f"Trace: {user_trace} Reject: {list(tracestate.tried)}")

    @staticmethod
    def _report_tracestate_wrapup(tracestate: TraceState):
        logger.info("Trace composed:")
        for progression in tracestate:
            logger.info(progression.scenario.name)
            logger.debug(f"model\n{progression.model.get_status_text()}\n")

    @staticmethod
    def _init_randomiser(seed: Any):
        if isinstance(seed, str):
            seed = seed.strip()

        if str(seed).lower() == 'none':
            logger.info(
                "Using system's random seed for trace generation. This trace cannot be rerun. Use `seed=new` to generate a reusable seed.")
        elif str(seed).lower() == 'new':
            new_seed = SuiteProcessors._generate_seed()
            logger.info(f"seed={new_seed} (use seed to rerun this trace)")
            random.seed(new_seed)
        else:
            logger.info(f"seed={seed} (as provided)")
            random.seed(seed)

    @staticmethod
    def _generate_seed() -> str:
        """Creates a random string of 5 words between 3 and 6 letters long"""
        vowels = ['a', 'e', 'i', 'o', 'u', 'y']
        consonants = ['b', 'c', 'd', 'f', 'g', 'h', 'j', 'k', 'l',
                      'm', 'n', 'p', 'q', 'r', 's', 't', 'v', 'w', 'x', 'z']

        words = []
        for word in range(5):
            prior_choice = random.choice([vowels, consonants])
            last_choice = random.choice([vowels, consonants])
            string = random.choice(prior_choice) + random.choice(last_choice)  # add first two letters
            for letter in range(random.randint(1, 4)):                         # add 1 to 4 more letters
                if prior_choice is last_choice:
                    new_choice = consonants if prior_choice is vowels else vowels
                else:
                    new_choice = random.choice([vowels, consonants])

                prior_choice = last_choice
                last_choice = new_choice
                string += random.choice(new_choice)

            words.append(string)

        seed = '-'.join(words)
        return seed
