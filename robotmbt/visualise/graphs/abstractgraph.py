from abc import ABC, abstractmethod
from robotmbt.visualise.models import TraceInfo
import networkx as nx


class AbstractGraph(ABC):
    @abstractmethod
    def update_visualisation(self, info: TraceInfo):
        """
        Update the visualisation with new trace information from another exploration step.
        """
        pass

    @abstractmethod
    def set_final_trace(self, info: TraceInfo):
        """
        Update the graph with information on the final trace.
        """
        pass

    @property
    @abstractmethod
    def networkx(self) -> nx.DiGraph:
        """
        We use networkx to store nodes and edges.
        """
        pass

    @networkx.setter
    @abstractmethod
    def networkx(self, value: nx.DiGraph):
        pass
