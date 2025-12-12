import os
import sys
import robot

if __name__ == '__main__':
    if '-h' in sys.argv or '--help' in sys.argv:
        print("""Usage: python run_demo.py [miss|hit|extended]

              When started without arguments, runs the Titanic demo following the `miss` scenario.
              Including `hit`, `miss` or `extended` will run the selected scenario:
              - hit: Reenacts Titanic's fateful maiden voyage
              - miss: Titanic safely reaches New York
              - extended: Titanic goes on repeated voyages
        """)
        sys.exit(0)
    THIS_DIR = os.path.dirname(os.path.abspath(__file__))
    OUTPUT_ROOT = os.path.join(THIS_DIR, 'results')
    SCENARIO_FOLDER = os.path.join(THIS_DIR, 'Titanic_scenarios')
    HIT_MISS_TAG = 'hit' if len(
        sys.argv) == 1 or sys.argv[1].casefold() != 'hit' else 'miss'
    EXTENDED_TAG = 'extended' if len(
        sys.argv) == 1 or sys.argv[1].casefold() != 'extended' else 'dummy'

    # The base folder needs to be added to the python path to resolve the dependencies. You
    # will also need to add this path to your IDE options when running from there.
    robot.run_cli(['--outputdir', OUTPUT_ROOT,
                   '--pythonpath', THIS_DIR,
                   '--exclude', HIT_MISS_TAG,
                   '--exclude', EXTENDED_TAG,
                   '--loglevel', 'DEBUG:INFO',
                   SCENARIO_FOLDER],
                  exit=False)
