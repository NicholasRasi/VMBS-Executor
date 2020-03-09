# Cloud Benchmark
A suite of benchmarks for cloud providers

## Usage
```python
# init
virtualenv env
source env/bin/activate
pip install -r requirements.txt
# run
python main.py
```

## Benchmark Tools
### System
- [**sysbench**](https://github.com/akopytov/sysbench): sysbench is a scriptable multi-threaded benchmark tool
    - CPU
    - memory
    - threads
    - fileio

### Hardware Specific
#### CPU
- **CPUBenchmark**: run a simple CPU benchmark

#### IO
- **DDBenchmark**: dd command is used to monitor the writing performance of a disk device on a Linux and Unix-like system

#### Network
- **DownloadBenchmark**: download a sample file

### Application Specific
#### AI
- [**ai-benchmark**](https://pypi.org/project/ai-benchmark/): AI Benchmark Alpha is an open source python library for evaluating AI performance of various hardware platforms, including CPUs, GPUs and TPUs.

#### Web
- [**gunicorn**](gunicorn.org/) web server + [**wrk**](https://github.com/wg/wrk): wrk is a modern HTTP benchmarking tool capable of generating significant load when run on a single multi-core CPU