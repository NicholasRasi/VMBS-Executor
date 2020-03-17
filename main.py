import json
import random
import time
import logging
import coloredlogs
import argparse
import requests
import yaml
import datetime
from benchmarks.benchmarks import get_benchmark_class
from benchmarks.server import Server

# setup logger
logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', milliseconds=False, logger=logger)
logger.info("Start cloud benchmark")

# parse arguments
parser = argparse.ArgumentParser()
parser.add_argument('--bin', type=str, required=False)
args = parser.parse_args()

# read bin id from file if not provided as an argument
if args.bin:
    bin_id = args.bin
else:
    f = open("bin_id.txt", "r")
    bin_id = (f.read())

# read configuration file
with open("config.yml", 'r') as file:
    data = file.read()
    config = yaml.load(data, Loader=yaml.FullLoader)

# setup bin url
sending_bin = config["bin_database_url"] + "/" + str(bin_id).strip()
logger.info("Sendind data to: " + sending_bin)

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
        benchmark_results.append({"name": benchmark.name, "setup": benchmark.get_setup(),
                                  "result": result, "completed": True})
    except Exception as e:
        benchmark_results.append({"name": benchmark.name, "setup": benchmark.get_setup(),
                                  "result": str(e), "completed": False})
        logger.error(str(e))
end = time.time()

# build payload
benchmark_result = {"time": str(datetime.datetime.now()),
                    "duration": end - start,
                    "server": Server.get_all(),
                    "benchmarks": benchmark_results}
payload = json.dumps(benchmark_result)
logging.info("Sending payload: " + payload + " to " + sending_bin)

# send data
response = requests.post(sending_bin, payload, headers={'content-type': 'application/json'})
logging.info(response.text)
