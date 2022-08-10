from .version import VERSION
from .SuiteReplacer import SuiteReplacer
from .SuiteProcessors import SuiteProcessors

class robotmbt(SuiteReplacer, SuiteProcessors):
    """
    Generic non-domain specific keywords for use by all to enhance the Natural Language experience
    """

__version__ = VERSION
