import os
import time
import statistics
from benchmarks.wrapper import Wrapper
from math import sin, cos, radians
from ai_benchmark import AIBenchmark
from .python_sysbench import Sysbench


class Benchmark:
    name = None

    def __init__(self, repeat, logger):
        self.repeat = repeat
        self.logger = logger
        self.wrapper = Wrapper(self.logger)
        self.result = []

    def pre(self):
        self.logger.info("Starting " + self.name + " benchmark...")

    def run(self):
        """Abstract method, must be overridden in child class."""
        raise NotImplementedError

    def post(self):
        self.logger.info(self.name + " results: " + str(self.result))


class DDBenchmark(Benchmark):
    """
    dd command is used to monitor the writing performance of a disk device on a Linux and Unix-like system
    https://www.cyberciti.biz/faq/howto-linux-unix-test-disk-performance-with-dd-command/
    """
    name = 'dd'

    def __init__(self, repeat, logger):
        super().__init__(repeat, logger)
        self.bs_count_list = None

    def set_bs_count(self, bs_count_list):
        self.bs_count_list = bs_count_list

    def pre(self):
        self.logger.info(
            "Starting " + self.name + " benchmark with bs_count=" + str(self.bs_count_list))

    def run(self):
        self.pre()
        for bs_count in self.bs_count_list:
            bs = bs_count[0]
            count = bs_count[1]
            for r in range(self.repeat):
                retcode, output = self.wrapper.dd("/dev/zero", "benchmark", bs, count)

                self.result.append({"setup": {"run": r, "repeat": self.repeat, "bs": bs, "count": count},
                                    "retcode": retcode, "output": output})
        os.remove('benchmark')
        self.post()
        return self.result


class DownloadBenchmark(Benchmark):
    """
    Download a sample file
    """
    name = 'download'

    def __init__(self, repeat, logger):
        super().__init__(repeat, logger)
        self.url = 'http://cachefly.cachefly.net/100mb.test'

    def set_url(self, url):
        self.url = url

    def run(self):
        self.pre()
        for r in range(self.repeat):
            retcode, output = self.wrapper.curl("/dev/null", self.url)
            self.result.append({"setup": {"run": r, "repeat": self.repeat, "url": self.url},
                                "retcode": retcode, "output": output})
        self.post()
        return self.result


class CPUBenchmark(Benchmark):
    """
    Run a simple CPU benchmark
    """

    name = 'simple-cpu'

    def run(self):
        self.pre()
        durations = []
        for r in range(self.repeat):
            start = time.time()
            product = 1.0
            for counter in range(1, 1000, 1):
                for dex in list(range(1, 360, 1)):
                    angle = radians(dex)
                    product *= sin(angle) ** 2 + cos(angle) ** 2
            end = time.time()
            durations.append(end - start)
            self.result.append({"setup": {"run": r, "repeat": self.repeat},
                                "result": statistics.mean(durations)})
        self.post()
        return self.result


class AIABenchmark(Benchmark):
    """
    AI Benchmark Alpha is an open source python library for evaluating AI performance of various hardware platforms
    https://pypi.org/project/ai-benchmark/
    """
    name = 'ai-benchmark'

    def __init__(self, repeat, logger, type=None):
        super().__init__(repeat, logger)
        self.type = type

    def run(self):
        self.pre()
        benchmark = AIBenchmark()
        for r in range(self.repeat):
            if self.type == "inference":
                ai_results = benchmark.run_inference()
            elif self.type == "training":
                ai_results = benchmark.run_training()
            elif self.type == "micro":
                ai_results = benchmark.run_micro()
            else:
                ai_results = benchmark.run()
            self.result.append({"setup": {"run": r, "repeat": self.repeat},
                                "result": {"ai_score": ai_results.ai_score,
                                           "inference_score": ai_results.inference_score,
                                           "training_score": ai_results.training_score}})
        self.post()
        return self.result


class SysBenchmark(Benchmark):
    name = 'sys-benchmark'

    def run(self):
        self.pre()
        sysbench = Sysbench(return_full_output=True)
        for r in range(self.repeat):
            output_cpu = sysbench.cpu(2000)
            output_memory = sysbench.memory("1M", "10G")
            output_threads = sysbench.threads(10, 128)
            output_fileio = sysbench.fileio("1GB", "rndrw", 60, 0)

            self.result.append({"setup": {"run": r, "repeat": self.repeat},
                                "result": {"cpu": {"output": output_cpu},
                                           "memory": {"output": output_memory},
                                           "threads": {"output": output_threads},
                                           "fileio": {"output": output_fileio}}})

        self.post()
        return self.result


class WebServerBenchmark(Benchmark):
    name = 'web-benchmark'

    def run(self):
        self.pre()

        for r in range(self.repeat):
            dir_path = os.path.dirname(os.path.realpath(__file__))
            web_server = self.wrapper.gunicorn(12, dir_path + "/webserver/", "main:create_app()", bg=True)
            self.logger.info("Web server started...")
            time.sleep(5)
            self.logger.info("Starting load generator...")
            # run load generator
            retcode, output = self.wrapper.wrk(12, 24, 30, "http://localhost:8000")
            web_server.terminate()
            self.logger.info(output)

            self.result.append({"setup": {"run": r, "repeat": self.repeat},
                                "result": {"retcode": retcode, "output": output}})
        self.post()
        return self.result
