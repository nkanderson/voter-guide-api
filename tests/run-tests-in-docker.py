#!/usr/bin/env python

"""Script for running tests using docker compose.

May be invoked with debug option in order to leverage VS Code debugging config.
NOTE: breakpoints in tests may not work until resolution of https://github.com/microsoft/debugpy/issues/1098,
but uncaught exceptions should still trigger a break in the debugger.
Ex: `./tests/run-tests-in-docker.py -d`

Adding the build option will ensure image is rebuilt before running tests.
Ex: `./tests/run-tests-in-docker.py -b`
"""

import subprocess, sys, getopt


def main():
    service_name = "api"
    run_opts = ["--rm"]
    cmd = "pytest"

    try:
        opts, _args = getopt.getopt(sys.argv[1:], "db", ["debug", "build"])
    except getopt.GetoptError as err:
        print(err)
        sys.exit(2)

    debug = False
    build = False

    for o, _a in opts:
        if o in ("-d", "--debug"):
            debug = True
        elif o in ("-b", "--build"):
            build = True
        else:
            assert False, "unhandled option, valid options include --debug and --build"

    if debug:
        service_name = "debug_api"
        run_opts.append("--publish 5678:5678")
        cmd = 'sh -c "pip install debugpy -t /tmp && python /tmp/debugpy --log-to log/debug --wait-for-client --listen 0.0.0.0:5678 -m pytest"'

    if build:
        build_cmd = f"docker compose build {service_name}"
        print(f"Running build with command: {build_cmd}")
        subprocess.run(build_cmd, shell=True)

    run_cmd = f"docker compose run {' '.join(run_opts)} {service_name} {cmd}"
    print(f"Running tests with command: {run_cmd}")
    subprocess.run(run_cmd, shell=True)


if __name__ == "__main__":
    main()
