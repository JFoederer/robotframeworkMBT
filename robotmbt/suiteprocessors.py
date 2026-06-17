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

from robot.api import logger
from robot.errors import TimeoutExceeded

from . import modeller
from .modelspace import ModelSpace
from .suitedata import Suite, Scenario
from .tracestate import TraceState

try:
    from .visualise.visualiser import Visualiser
except ImportError:
    Visualiser = None


class SuiteProcessor:
    def process_test_suite(self, in_suite: Suite,
                           **kwargs) -> Suite:
        self._handle_target_options(**kwargs)
        self.scenario_count = in_suite.scenario_count()
        # Counts the scenarios committed by the runner. I.e. the scenarios that are scheduled for execution
        # and cannot be touched anymore
        self.commit_count: int = 0
        return Suite('not implemented')

    def next_scenario_request(self):
        """Indicates the wish for (at least) one more scenario and triggers trace genaration when needed."""
        # This basic implementation assumes that the complete target test suite is returned directly
        # by process_test_suite() in an overridden method. No further generation is triggered.
        if self.scenario_count >= self.commit_count + 1:
            self.commit_count += 1

    @property
    def scenarios_committed(self) -> int:
        """
        Each time next_scenario_request() is called, you commit to one more scenario, if there is at
        least one more scenario available. This can be an already pending scenario, or new trace
        generation can be triggered to generate a next scenario (or batch). Committed scenarios are
        assumed to have been executed when determining the achieved targets.
        """
        return self.commit_count

    @property
    def scenarios_pending(self) -> int:
        """
        The number of scenarios that are waiting in the buffer for when more scenarios are requested.

        For practical reasons, trace generation can run ahead of the actual test execution, creating
        a buffer of pending scenarios ahead of time.

        Note that pending scenarios are still subject to change. Only committed scenarios are frozen
        in place.
        """
        return self.scenario_count - self.commit_count

    def are_all_targets_reached(self, committed_only: bool = True) -> bool:
        if not committed_only:
            return True
        if self.coverage_target and self.commit_count < self.scenario_count:
            return False
        if self.scenario_target and self.commit_count < self.scenario_target:
            return False
        return True

    def _handle_target_options(self,
                               coverage_target: str | int | None = 1,
                               scenario_target: str | int | None = None,
                               **kwargs):
        self.coverage_target = 0 if coverage_target is None else int(coverage_target)
        if self.coverage_target not in [0, 1]:
            logger.warn(f"Unsupported coverage target request '{coverage_target}'. Using default coverage target of 1")
            self.coverage_target = 1
        self.scenario_target = 0 if scenario_target is None else int(scenario_target)


class Echo(SuiteProcessor):
    def process_test_suite(self, in_suite: Suite, **kwargs) -> Suite:
        super().process_test_suite(in_suite, **kwargs)
        return in_suite


class Flatten(SuiteProcessor):
    def process_test_suite(self, in_suite: Suite, **kwargs) -> Suite:
        """
        Takes a Suite as input and returns a Suite as output. The output Suite does not
        have any sub-suites, only scenarios. The scenarios do not have a setup. Any setup
        keywords are inserted at the front of the scenario as regular steps.
        """
        super().process_test_suite(in_suite, **kwargs)
        return self.flatten(in_suite)

    @staticmethod
    def flatten(in_suite: Suite) -> Suite:
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
            subsuite = Flatten.flatten(suite)
            for scenario in subsuite.scenarios:
                if subsuite.setup:
                    scenario.steps.insert(0, subsuite.setup)
                if subsuite.teardown:
                    scenario.steps.append(subsuite.teardown)
            out_suite.scenarios.extend(subsuite.scenarios)
        out_suite.scenarios.extend(outer_scenarios)
        out_suite.suites = []
        return out_suite


class ModelBased(SuiteProcessor):
    def process_test_suite(self, in_suite: Suite, *, seed: str | int | bytes | bytearray = 'new',
                           batch_size: str | int = 100,
                           graph: str = '', export_graph_data: str = '', **kwargs) -> Suite:
        # handle options
        super().process_test_suite(in_suite, **kwargs)
        self.batch_size = int(batch_size)
        self._init_randomiser(seed)
        self._visualiser = self._init_visualiser(in_suite.name) if graph or export_graph_data else None

        self.out_suite = Suite(in_suite.name)
        self.out_suite.filename = in_suite.filename
        self.out_suite.parent = in_suite.parent
        self._fail_on_step_errors(in_suite)
        self.flat_suite = Flatten.flatten(in_suite)
        for id, scenario in enumerate(self.flat_suite.scenarios, start=1):
            scenario.src_id = id
        self.scenarios: list[Scenario] = self.flat_suite.scenarios[:]
        logger.debug("Use these numbers to reference scenarios from traces\n\t" +
                     "\n\t".join([f"{s.src_id}: {s.name}" for s in self.scenarios]))

        try:
            # a short trace without the need for repeating scenarios is preferred
            direct_tracestate = self._search_direct_trace()
            if self.are_all_targets_reached(direct_tracestate, committed_only=False):
                # The visualiser assumes that the last trace is the final selected trace, which is not always
                # the case. Re-adding the selected trace to prevent the wrong path from being highlighted.
                self.tracestate = direct_tracestate
                self._update_visualisation(self.tracestate)
            else:
                self.tracestate = TraceState([s.src_id for s in self.scenarios])
                self.tracestate.unreached = direct_tracestate.unreached
                logger.debug("Direct trace not discovered. Now exploring with loops, allowing repetition of scenarios.")
                self._generate_next_batch(self.batch_size)
        finally:  # Draw the graph even when a timeout or user interrupt occurs
            if graph:
                self._write_visualisation(graph)
            if export_graph_data:
                self._export_graph_data(export_graph_data)
        if len(self.tracestate) == 0:
            raise Exception("Unable to compose a consistent suite")
        self._report_tracestate_wrapup()
        return self.out_suite

    def next_scenario_request(self):
        if len(self.tracestate) <= self.out_suite.scenario_count():
            self._generate_next_batch(self.batch_size)
        if len(self.tracestate) > self.out_suite.scenario_count():
            self.out_suite.scenarios.append(self.tracestate[self.out_suite.scenario_count()].scenario)
            self.commit_count += 1
            self.tracestate.rewind_limit += 1

    @property
    def scenarios_committed(self) -> int:
        return self.out_suite.scenario_count()

    @property
    def scenarios_pending(self) -> int:
        return len(self.tracestate) - self.out_suite.scenario_count()

    def are_all_targets_reached(self, tracestate: TraceState | None = None, committed_only: bool = True) -> bool:
        if tracestate is None:
            tracestate = self.tracestate
        if committed_only:
            if self.coverage_target and not tracestate[self.commit_count-1].coverage_reached:
                return False
            if self.scenario_target and self.commit_count < self.scenario_target:
                return False
        else:
            if self.coverage_target and not tracestate.coverage_reached():
                return False
            if self.scenario_target and len(tracestate) < self.scenario_target:
                return False
        return True

    def draw_graph_from_export_file(self, file_path: str, graph_style: str):
        self._visualiser = self._init_visualiser()
        if self._visualiser:
            self._visualiser.load_from_file(file_path)
            logger.info(self._visualiser.generate_visualisation(graph_style), html=True)
        else:
            logger.info(f'Visualisation disabled due to initialisation failure.')

    def _search_direct_trace(self) -> TraceState:
        """
        Try to find a direct trace (without repeated scenarios) by exploring multiple traces
        with different priorities for selecting a scenario. Each attempt a new set of scenarios
        is moved to the front of the list, giving it the best chance of early insertion with the
        least dependencies. Other scenarios are randomised for further exploration. This gives
        a good (but not necessary complete) picture of dependencies between scenarios.

        If no direct trace is found after this first phase, additional attemps are made to
        construct a direct trace based on the longest trace found so far and then based on the
        last trace that resulted in new coverage. If there is still no full trace found, no
        further attemps are made and the last explored trace is returned.

        If visualisation is inactive, then the first discovered full direct trace is returned.
        If visualisation is active, then the first phase is always completed before returning.
        """
        MAX_LOOPCOUNT = 7
        id_list = [s.src_id for s in self.scenarios]
        loopcount = min(MAX_LOOPCOUNT, len(id_list))
        random.shuffle(id_list)  # pre-shuffle to prevent scenario 1 from always getting first prio
        prio_chunks = [id_list[i::loopcount] for i in range(loopcount)]
        tracestates = []
        for prio_ids in prio_chunks:
            prio_order = prio_ids
            other_scenarios = [s for s in id_list if s not in prio_ids]
            random.shuffle(other_scenarios)
            prio_order += other_scenarios
            if self._is_duplicate_prio_order(tracestates, prio_order):
                continue
            tracestates.append(self._one_shot_trace(prio_order))
            if self.are_all_targets_reached(tracestates[-1], committed_only=False) and not self._visualiser:
                return tracestates[-1]
            suggestion = self._create_suggestion_by_experience(tracestates)
            if self._is_duplicate_prio_order(tracestates, suggestion):
                continue
            tracestates.append(self._one_shot_trace(suggestion))
            if self.are_all_targets_reached(tracestates[-1], committed_only=False) and not self._visualiser:
                return tracestates[-1]

        index_longest = self._longest_trace(tracestates)
        if self.are_all_targets_reached(tracestates[index_longest], committed_only=False):
            return tracestates[index_longest]
        logger.debug("Trying to extend most promising traces")
        prio_order = self._create_suggestion_by_experience(tracestates, index_longest)
        if not self._is_duplicate_prio_order(tracestates, prio_order):
            tracestates.append(self._one_shot_trace(prio_order))
            if self.are_all_targets_reached(tracestates[-1], committed_only=False):
                return tracestates[-1]
        last_new = self._last_new_coverage(tracestates)
        while True:  # while still discovering new coverage
            prio_order = self._create_suggestion_by_experience(tracestates, last_new)
            if self._is_duplicate_prio_order(tracestates, prio_order):
                break
            tracestates.append(self._one_shot_trace(prio_order))
            if self.are_all_targets_reached(tracestates[-1], committed_only=False):
                return tracestates[-1]
            last_new = self._last_new_coverage(tracestates)
            if last_new != len(tracestates)-1:
                break  # The new entry did not yield new coverage

        longest = tracestates[self._longest_trace(tracestates)]
        not_in_trace = sorted(longest.not_in_trace)
        longest.unreached = sorted(self._unreached_scenarios(tracestates))
        logger.debug(
            f"Longest trace so far ({len(longest.covered_ids)} scenario{'s' if len(longest.covered_ids) != 1 else ''})"
            f": [{', '.join(longest.id_trace)}]\n"
            f"{len(not_in_trace)} Scenario{'s' if len(not_in_trace) != 1 else ''} not in this trace: "
            f": [{', '.join([str(i) + '*' if i in longest.unreached else str(i) for i in not_in_trace])}] "
            "(Scenarios marked with * are not part of any trace)\n\n")
        return longest

    def _longest_trace(self, tracestate_list: list[TraceState]) -> int:
        """returns the index of the trace that covers the most scenarios"""
        lengths = [len(ts.covered_ids) for ts in tracestate_list]
        return lengths.index(max(lengths))

    def _last_new_coverage(self, tracestate_list: list[TraceState]) -> int:
        """
        From the list of traces, finds the last trace that inserted a scenario that had not
        been reached before. The idea behind this is that maybe this last insertion was most
        difficult to reach and this trace may contain a unique sequence for reaching that
        scenario.
        """
        ids = []
        latest_new = 0
        for index, tracestate in enumerate(tracestate_list):
            for id in [int(float(long_id)) for long_id in tracestate.id_trace]:
                if id not in ids:
                    ids.append(id)
                    latest_new = index
        return latest_new

    @staticmethod
    def _is_duplicate_prio_order(tracestate_list: list[TraceState], candidate_order) -> bool:
        return any(ts.prio_order == candidate_order for ts in tracestate_list)

    @staticmethod
    def _unreached_scenarios(tracestate_list: list[TraceState]) -> list[int]:
        not_in_trace = [set(t.not_in_trace) for t in tracestate_list]
        return list(not_in_trace[0].intersection(*not_in_trace[1:]))

    def _one_shot_trace(self, scenarios: list[int]) -> TraceState:
        """
        Given a list of scenario ids, construct a trace trying all scenarios in order until
        a full trace is created, or until a deadend is reached. No rollbacks are done.
        """
        logger.debug(f"Discovering with prio order {scenarios}")
        tracestate = TraceState(scenarios)
        self._update_visualisation(tracestate)
        candidate_id = tracestate.next_candidate(retry=False, randomise=False)
        while candidate_id is not None:
            candidate = self._select_scenario_variant(candidate_id, tracestate)
            if candidate:  # No valid variant available in the current state
                modeller.try_to_fit_in_scenario(candidate, tracestate)
            else:
                tracestate.reject_scenario(candidate_id)
            self._update_visualisation(tracestate)
            candidate_id = tracestate.next_candidate(retry=False)
        n = len(tracestate.covered_ids)
        logger.debug(f"Discovered trace ({n} scenario{'s' if n != 1 else ''}): [{', '.join(tracestate.id_trace)}]")
        return tracestate

    def _create_suggestion_by_experience(self, tracestate_list, target_index=-1) -> list[int]:
        """
        target_index is the index in tracestate_list to use as prior experience. The next
        suggestion is a prio order created using the following rules:
          - First all never-reached scenarios in randomized order,
          - then all scenarios that are reachable, but are not part of the prior experience,
          - and finally all scenarios (in order) that are part of the prior experience.

        Note that items earlier in the prio order are tried more often to get inserted.
        """
        never_reached = self._unreached_scenarios(tracestate_list)
        random.shuffle(never_reached)
        not_in_target = [id for id in tracestate_list[target_index].not_in_trace if id not in never_reached]
        return never_reached + not_in_target + tracestate_list[target_index].covered_ids

    def _generate_next_batch(self, batchsize):
        tracestate = self.tracestate
        old_len = len(tracestate)
        self._update_visualisation(tracestate)
        while len(tracestate) < old_len + batchsize and not self.are_all_targets_reached(committed_only=False):
            candidate_id = tracestate.next_candidate(retry=True, randomise=True)
            if candidate_id is None:
                logger.debug("No more candidates remaining at this position.")
                if not tracestate.can_rewind():
                    break
                tail = modeller.rewind(tracestate)
                logger.debug(f"Having to roll back up to {tail.scenario.name if tail else 'the beginning'}")
                self._report_tracestate_to_user(tracestate)
                if tracestate.model:
                    logger.debug(f"last state:\n{tracestate.model.get_status_text()}")
            else:
                candidate = self._select_scenario_variant(candidate_id, tracestate)
                if not candidate:  # No valid variant available in the current state
                    tracestate.reject_scenario(candidate_id)
                    self._update_visualisation(tracestate)
                    continue
                previous_len = len(tracestate)
                modeller.try_to_fit_in_scenario(candidate, tracestate)
                self._update_visualisation(tracestate)
                if len(tracestate) > previous_len:
                    self._report_tracestate_to_user(tracestate)
                    logger.debug(f"last state:\n{tracestate.model.get_status_text()}")
                    self.DROUGHT_LIMIT = 50
                    if self.__last_candidate_changed_nothing(tracestate):
                        logger.debug("Repeated scenario did not change the model's state. Stop trying.")
                        modeller.rewind(tracestate)
                    elif self.coverage_target and not self.tracestate.coverage_reached() and tracestate.coverage_drought > self.DROUGHT_LIMIT:
                        logger.debug(f"Went too long without new coverage (>{self.DROUGHT_LIMIT}x). "
                                     "Roll back to last coverage increase and try something else.")
                        modeller.rewind(tracestate, drought_recovery=True)
                        self._report_tracestate_to_user(tracestate)
                        logger.debug(f"last state:\n{tracestate.model.get_status_text()}")
            self._update_visualisation(tracestate)
        self._update_visualisation(tracestate)

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
            candidate.name = f"{candidate.name} (rep {rep_count+1})"
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
        pending = ', '.join([str(i) + '*' if i in tracestate.unreached else str(i) for i in tracestate.not_in_trace])
        logger.debug(f"Trace: [{', '.join(tracestate.id_trace)}] Pending: [{pending}]"
                     f"{' Rejected: ' + str(tracestate.tried) if tracestate.tried else ''}")

    def _report_tracestate_wrapup(self):
        if self.are_all_targets_reached(committed_only=False):
            logger.info("Trace composed:")
        else:
            logger.info("First part of trace composed: (Check scenarios tagged with `mbt trace extension` for continued generation)")
        for progression in self.tracestate:
            logger.info(progression.scenario.name)
            logger.debug(f"model\n{progression.model.get_status_text()}\n")

    @staticmethod
    def _init_randomiser(seed: str | int | bytes | bytearray | None):
        if isinstance(seed, str):
            seed = seed.strip()
        if str(seed).lower() == 'none':
            random.seed()
            logger.info(
                "Using system's random seed for trace generation. This trace cannot be rerun. Use `seed=new` to generate a reusable seed.")
        elif str(seed).lower() == 'new':
            random.seed()
            new_seed = ModelBased._generate_seed()
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

    def _init_visualiser(self, name: str = ''):
        global Visualiser
        if Visualiser is None:
            Visualiser = False
            logger.warn(f'Visualisation requested, but required dependencies are not installed. '
                        'Refer to the README on how to install these dependencies. ')
        return Visualiser(name) if Visualiser else None

    def _update_visualisation(self, tracestate: TraceState):
        if self._visualiser:
            try:
                self._visualiser.update_trace(tracestate)
            except TimeoutExceeded:
                raise
            except Exception as e:
                logger.debug(f'Could not update visualisation due to error!\n{e}')

    def _write_visualisation(self, graph_style: str):
        if self._visualiser:
            try:
                text = self._visualiser.generate_visualisation(graph_style)
                logger.info(text, html=True)
            except TimeoutExceeded:
                raise
            except Exception as e:
                logger.debug(f'Could not generate visualisation due to error!\n{e}')
        else:
            logger.info("Graph skipped due to prior failure")

    def _export_graph_data(self, export_dir):
        if self._visualiser:
            try:
                file_name = self._visualiser.export_to_file(export_dir)
                logger.info(f"Graph data stored in file: {file_name}")
            except TimeoutExceeded:
                raise
            except Exception as e:
                logger.info("Could not export visualisation due to failure.")
                logger.debug(f"Export error:\n{e}")
