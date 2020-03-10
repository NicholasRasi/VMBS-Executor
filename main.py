import json
import time
import logging
import coloredlogs
import argparse
import requests
from benchmarks.benchmarks import DDBenchmark, DownloadBenchmark, CPUBenchmark, AIABenchmark, SysBenchmark, WebServerBenchmark
from benchmarks.server import Server

coloredlogs.install(level='INFO', milliseconds=False)

logger = logging.getLogger("cloud-benchmark")
logger.info("Start cloud benchmark")

parser = argparse.ArgumentParser()
parser.add_argument('--bin', type=str, required=True)
args = parser.parse_args()


benchmark_results = []
benchmarks = []
start = time.time()

# set up benchmarks
# dd benchmark
dd_benchmark = DDBenchmark(repeat=2, logger=logger)
dd_benchmark.set_bs_count([("512MB", 1), ("512", 1000)])
benchmarks.append(dd_benchmark)
# download benchmark
download_benchmark = DownloadBenchmark(repeat=1, logger=logger)
benchmarks.append(download_benchmark)
# simple CPU
cpu_benchmark = CPUBenchmark(repeat=100, logger=logger)
benchmarks.append(cpu_benchmark)
# ai benchmark
ai_benchmark = AIABenchmark(repeat=1, logger=logger, type="micro")
benchmarks.append(ai_benchmark)
# sysbenchmark
sys_benchmark = SysBenchmark(repeat=1, logger=logger)
benchmarks.append(sys_benchmark)
# web server benchmark
web_benchmark = WebServerBenchmark(repeat=1, logger=logger)
#benchmarks.append(web_benchmark)

for benchmark in benchmarks:
    benchmark_results.append({"name": benchmark.name, "results": benchmark.run()})

end = time.time()

benchmark_result = {"duration": end - start, "server": Server.get_all(), "benchmarks": benchmark_results}
logging.info("Sending payload: " + json.dumps(benchmark_result) + " to " + args.bin)

response = requests.post(args.bin, benchmark_result)
logging.info(response)