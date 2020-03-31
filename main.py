import json
import random
import time
import logging
import coloredlogs
import yaml
import datetime
from benchmarks.benchmarks import get_benchmark_class
from benchmarks.server import Server

CONFIG_FILE = "config_benchmark.yml"

# setup logger
logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', milliseconds=False, logger=logger)
logger.info("Start cloud benchmark")

# read configuration file
with open(CONFIG_FILE, 'r') as file:
    data = file.read()
    config = yaml.load(data, Loader=yaml.FullLoader)

benchmark_results = []
benchmarks_list = []

benchmarks = config["benchmarks"]
logger.info("Running benchmarks: " + ", ".join(benchmarks.keys()))

# set up benchmarks
for benchmark_name in benchmarks.keys():
    benchmark_class = get_benchmark_class(benchmark_name)
    logger.info("Adding " + benchmark_name + " with: " + str(benchmarks[benchmark_name]["setup"]))
    for repeat in range(benchmarks[benchmark_name]["repeat"]):
        for setup in benchmarks[benchmark_name]["setup"]:
            benchmark = benchmark_class(logger=logger)
            benchmark.setup(setup)
            benchmarks_list.append(benchmark)

# randomize benchmark list
random.shuffle(benchmarks_list)
logger.info("Benchmark list: " + ", ".join([benchmark.name for benchmark in benchmarks_list]))

# start running benchmarks
start = time.time()
for benchmark in benchmarks_list:
    try:
        result = benchmark.run()
    except Exception as e:
        logger.error(str(e))
        result = { "retcode": 400, "result": str(e) }
    benchmark_results.append({"name": benchmark.name, "setup": benchmark.get_setup(), "result": result})

end = time.time()

# build payload
benchmark_result = {"time": str(datetime.datetime.now()),
                    "duration": end - start,
                    "server": Server.get_all(),
                    "benchmarks": benchmark_results}

# save to file
logger.info("Benchmark finished, saving to file...")
with open('benchmark_result', 'w') as outfile:
    json.dump(benchmark_result, outfile)
logger.info("Exiting")
