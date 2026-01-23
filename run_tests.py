import os
import sys
import unittest
import robot

if __name__ == '__main__':
    if '-h' in sys.argv or '--help' in sys.argv:
        print("""Usage: python run_tests.py [utest] [atest] [Robot options]
        - When started without arguments, runs all unit and acceptance tests
        - Any additional arguments are used as command line options for Robot Framework
        - Unit tests can also be executed by running their individual files as script (check path settings)""")
        sys.exit(0)
    THIS_DIR = os.path.dirname(os.path.abspath(__file__))
    if len(sys.argv) == 1:
        print("No arguments provided. Running all unit and acceptance tests from", THIS_DIR)

    if 'utest' in sys.argv:
        utest = True
        atest = False if 'atest' not in sys.argv else True
        sys.argv.remove('utest')
    elif 'atest' in sys.argv:
        utest = False
        atest = True
    else:
        utest = True
        atest = True

    if utest:
        utestrun = unittest.main(module=None,
                                 argv=[__file__, 'discover', os.path.join(THIS_DIR, 'utest')],
                                 exit=False)
        if not utestrun.result.wasSuccessful():
            sys.exit(1)

    if atest:
        if 'atest' in sys.argv:
            sys.argv.remove('atest')
        sys.argv.append(os.path.join(THIS_DIR, 'atest'))
        OUTPUT_ROOT = os.path.join(THIS_DIR, 'atest', 'results')
        # Adding the robotframeworkMBT folder to the python path forces the development
        # version to be used instead of the one installed on your system. You will also
        # need to add this path to your IDE options when running from there.
        exit_code: int = robot.run_cli(['--outputdir', OUTPUT_ROOT,
                                        '--pythonpath', THIS_DIR]
                                       + sys.argv[1:], exit=False)
        if utest:
            print(f"Also ran {utestrun.result.testsRun} unit tests")

        sys.exit(exit_code)
