import os
import sys
import robot

if __name__ == '__main__':
    if '-h' in sys.argv or '--help' in sys.argv:
        print("""Usage: python run_demo.py [miss|hit]
              When started without arguments, runs the Titanic demo following the `miss` scenario.
              Including the scenario to run, `miss` or `hit` will select that scenario to run.
        """)
        sys.exit(0)
    THIS_DIR = os.path.dirname(os.path.abspath(__file__))
    OUTPUT_ROOT = os.path.join(THIS_DIR, 'results')
    SCENARIO_FOLDER = os.path.join(THIS_DIR, 'Titanic_scenarios')
    TAG = 'hit' if len(sys.argv) == 1 or sys.argv[1].casefold() == 'miss' else 'miss'

    # The base folder needs to be added to the python path to resolve the dependencies. You
    # will also need to add this path to your IDE options when running from there.
    robot.run_cli(['--outputdir', OUTPUT_ROOT,
                   '--pythonpath', THIS_DIR,
                   '--exclude', TAG,
                   '--loglevel', 'DEBUG:INFO',
                   SCENARIO_FOLDER],
                   exit=False)
