import os
import time
import statistics
from benchmarks.wrapper import Wrapper
from math import sin, cos, radians
from ai_benchmark import AIBenchmark
from .python_sysbench import Sysbench


class Benchmark:
    error_code = 400
    succ_code = 0
    name = None

    def __init__(self, logger):
        self.logger = logger
        self.wrapper = Wrapper(self.logger)
        self.result = None

    def pre(self):
        self.logger.info("Starting " + self.name + " benchmark...")

    def setup(self, setup):
        self.setup = setup

    def get_setup(self):
        return self.setup

    def run(self):
        """Abstract method, must be overridden in child class."""
        raise NotImplementedError

    def post(self):
        self.logger.info("Benchmark " + self.name + " finished")


class DDBenchmark(Benchmark):
    """
    dd command is used to monitor the writing performance of a disk device on a Linux and Unix-like system
    https://www.cyberciti.biz/faq/howto-linux-unix-test-disk-performance-with-dd-command/
    """
    name = 'dd'

    def pre(self):
        self.logger.info("Starting " + self.name + " benchmark with bs=" + str(self.setup["bs"]) + ", count=" +
                         str(self.setup["count"]))

    def run(self):
        self.pre()

        try:
            retcode, output = self.wrapper.dd("/dev/zero", "benchmark", self.setup["bs"], self.setup["count"])
            os.remove('benchmark')
        except Exception as e:
            retcode, output = self.error_code, str(e)
        self.result = {"retcode": retcode, "output": output}

        self.post()
        return self.result


class DownloadBenchmark(Benchmark):
    """
    Download a sample file
    """
    name = 'download'

    def run(self):
        self.pre()

        try:
            retcode, output = self.wrapper.curl("/dev/null", self.setup["url"])
        except Exception as e:
            retcode, output = self.error_code, str(e)
        self.result = {"retcode": retcode, "output": output}

        self.post()
        return self.result


class CPUBenchmark(Benchmark):
    """
    Run a simple CPU benchmark
    """

    name = 'simple-cpu'

    def run(self):
        self.pre()

        try:
            durations = []
            start = time.time()
            product = 1.0
            for counter in range(1, 1000, 1):
                for dex in list(range(1, 360, 1)):
                    angle = radians(dex)
                    product *= sin(angle) ** 2 + cos(angle) ** 2
            end = time.time()
            durations.append(end - start)
            retcode, output = self.succ_code, statistics.mean(durations)
        except Exception as e:
            retcode, output = self.error_code, str(e)
        self.result = {"retcode": retcode, "output": output}

        self.post()
        return self.result


class AIABenchmark(Benchmark):
    """
    AI Benchmark Alpha is an open source python library for evaluating AI performance of various hardware platforms
    https://pypi.org/project/ai-benchmark/
    """
    name = 'ai-benchmark'

    def run(self):
        self.pre()

        try:
            benchmark = AIBenchmark()
            if self.setup["type"] == "inference":
                ai_results = benchmark.run_inference()
            elif self.setup["type"] == "training":
                ai_results = benchmark.run_training()
            elif self.setup["type"] == "micro":
                ai_results = benchmark.run_micro()
            else:
                ai_results = benchmark.run()
            self.result = {"retcode": self.succ_code,
                           "output": {"ai_score": ai_results.ai_score,
                                      "inference_score": ai_results.inference_score,
                                      "training_score": ai_results.training_score}}
        except Exception as e:
            self.result = {"retcode": self.error_code, "output": str(e)}

        self.post()
        return self.result


class SysBenchmark(Benchmark):
    name = 'sys-benchmark'

    def run(self):
        self.pre()
        try:
            sysbench = Sysbench(return_full_output=True)

            output_cpu = sysbench.cpu(self.setup["cpu_max_prime"])
            output_memory = sysbench.memory(self.setup["mem_block_size"], self.setup["mem_total_size"])
            output_threads = sysbench.threads(self.setup["threads_max_time"], self.setup["threads_num"])
            output_fileio = sysbench.fileio(self.setup["file_total_size"], self.setup["file_test_mode"],
                                            self.setup["file_max_time"], self.setup["file_max_requests"])
            self.result = {"retcode": self.succ_code,
                           "output": {"cpu": output_cpu,
                                      "memory": output_memory,
                                      "threads": output_threads,
                                      "fileio": output_fileio}}
        except Exception as e:
            self.result = {"retcode": self.error_code, "output": str(e)}

        self.post()
        return self.result


class WebServerBenchmark(Benchmark):
    """
    https://github.com/wg/wrk
    """
    name = 'web-benchmark'

    def run(self):
        self.pre()

        try:
            dir_path = os.path.dirname(os.path.realpath(__file__))
            web_server = self.wrapper.gunicorn(12, dir_path + "/webserver/", "main:create_app()", bg=True)
            self.logger.info("Web server started...")
            time.sleep(12)
            self.logger.info("Starting load generator...")
            # run load generator
            retcode, output = self.wrapper.wrk(self.setup["threads"], self.setup["connections"], self.setup["time"],
                                               "http://localhost:8000")
            web_server.terminate()
            self.logger.info(output)
        except Exception as e:
            retcode = self.error_code
            output = str(e)
        self.result = {"retcode": retcode, "output": output}

        self.post()
        return self.result


class NenchBenchmark(Benchmark):
    """
    https://github.com/n-st/nench
    """
    name = 'nench-benchmark'

    def run(self):
        self.pre()

        try:
            dir_path = os.path.dirname(os.path.realpath(__file__))
            retcode, output = self.wrapper.bash(dir_path + "/nench/nench.sh")
        except Exception as e:
            retcode, output = self.error_code, str(e)
        self.result = {"retcode": retcode, "output": output}

        self.post()
        return self.result


def get_benchmark_class(name):
    return list(filter(lambda bench: bench.name == name, BENCHMARKS))[0]


BENCHMARKS = [DDBenchmark, DownloadBenchmark, CPUBenchmark, AIABenchmark, SysBenchmark, WebServerBenchmark,
              NenchBenchmark]
