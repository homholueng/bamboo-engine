# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import os
import time
from functools import wraps
from contextlib import contextmanager

from prometheus_client import Gauge, Histogram

from .utils.host import get_hostname

HOST_NAME = get_hostname()


def decode_buckets(buckets_list):
    return [float(x) for x in buckets_list.split(",")]


def get_histogram_buckets_from_evn(env_name):
    if env_name in os.environ:
        buckets = decode_buckets(os.environ.get(env_name))
    else:
        if hasattr(Histogram, "DEFAULT_BUCKETS"):  # pragma: no cover
            buckets = Histogram.DEFAULT_BUCKETS
        else:  # pragma: no cover
            # For prometheus-client < 0.3.0 we cannot easily access
            # the default buckets:
            buckets = (
                0.005,
                0.01,
                0.025,
                0.05,
                0.075,
                0.1,
                0.25,
                0.5,
                0.75,
                1.0,
                2.5,
                5.0,
                7.5,
                10.0,
                float("inf"),
            )
    return buckets


def setup_gauge(*gauges):
    def wrapper(func):
        @wraps(func)
        def _wrapper(*args, **kwargs):
            for g in gauges:
                g.labels(hostname=HOST_NAME).inc(1)
            try:
                return func(*args, **kwargs)
            finally:
                for g in gauges:
                    g.labels(hostname=HOST_NAME).dec(1)

        return _wrapper

    return wrapper


def setup_histogram(*histograms):
    def wrapper(func):
        @wraps(func)
        def _wrapper(*args, **kwargs):
            start = time.time()
            try:
                return func(*args, **kwargs)
            finally:
                for h in histograms:
                    h.labels(hostname=HOST_NAME).observe(time.time() - start)

        return _wrapper

    return wrapper


@contextmanager
def observe(histogram, **labels):
    start = time.time()
    yield
    histogram.labels(**labels).observe(time.time() - start)


# engine metrics
ENGINE_RUNNING_PROCESSES = Gauge(
    name="engine_running_processes", documentation="count running state processes", labelnames=["hostname"]
)
ENGINE_RUNNING_SCHEDULES = Gauge(
    name="engine_running_schedules", documentation="count running state schedules", labelnames=["hostname"]
)
ENGINE_PROCESS_RUNNING_TIME = Histogram(
    name="engine_process_running_time",
    documentation="time spent running process",
    buckets=get_histogram_buckets_from_evn("ENGINE_PROCESS_RUNNING_TIME_BUCKETS"),
    labelnames=["hostname"],
)
ENGINE_SCHEDULE_RUNNING_TIME = Histogram(
    name="engine_schedule_running_time",
    documentation="time spent running schedule",
    buckets=get_histogram_buckets_from_evn("ENGINE_SCHEDULE_RUNNING_TIME_BUCKETS"),
    labelnames=["hostname"],
)
ENGINE_NODE_EXECUTE_TIME = Histogram(
    name="engine_node_execute_time",
    documentation="time spent executing node",
    buckets=get_histogram_buckets_from_evn("ENGINE_NODE_EXECUTE_TIME_BUCKETS"),
    labelnames=["type", "hostname"],
)
ENGINE_NODE_SCHEDULE_TIME = Histogram(
    name="engine_node_schedule_time",
    documentation="time spent scheduling node",
    buckets=get_histogram_buckets_from_evn("ENGINE_NODE_SCHEDULE_TIME_BUCKETS"),
    labelnames=["type", "hostname"],
)
ENGINE_EXECUTE_PRE_PROCESS_DURATION = Histogram(
    name="engine_execute_pre_process_duration",
    documentation="time spent node execute pre-processing",
    buckets=get_histogram_buckets_from_evn("ENGINE_NODE_SCHEDULE_TIME_BUCKETS"),
    labelnames=["type", "hostname"],
)
ENGINE_EXECUTE_POST_PROCESS_DURATION = Histogram(
    name="engine_execute_post_process_duration",
    documentation="time spent node execute post-processing",
    buckets=get_histogram_buckets_from_evn("ENGINE_NODE_SCHEDULE_TIME_BUCKETS"),
    labelnames=["type", "hostname"],
)
ENGINE_SCHEDULE_PRE_PROCESS_DURATION = Histogram(
    name="engine_schedule_pre_process_duration",
    documentation="time spent node schedule pre-processing",
    buckets=get_histogram_buckets_from_evn("ENGINE_NODE_SCHEDULE_TIME_BUCKETS"),
    labelnames=["type", "hostname"],
)
ENGINE_SCHEDULE_POST_PROCESS_DURATION = Histogram(
    name="engine_schedule_post_process_duration",
    documentation="time spent node schedule post-processing",
    buckets=get_histogram_buckets_from_evn("ENGINE_NODE_SCHEDULE_TIME_BUCKETS"),
    labelnames=["type", "hostname"],
)
ENGINE_NODE_EXECUTE_PRE_PROCESS_DURATION = Histogram(
    name="engine_node_execute_pre_process_duration",
    documentation="time spent node handler execute pre-processing",
    buckets=get_histogram_buckets_from_evn("ENGINE_NODE_SCHEDULE_TIME_BUCKETS"),
    labelnames=["type", "hostname"],
)
ENGINE_NODE_EXECUTE_POST_PROCESS_DURATION = Histogram(
    name="engine_node_execute_post_process_duration",
    documentation="time spent node handler execute post-processing",
    buckets=get_histogram_buckets_from_evn("ENGINE_NODE_SCHEDULE_TIME_BUCKETS"),
    labelnames=["type", "hostname"],
)
ENGINE_NODE_SCHEDULE_PRE_PROCESS_DURATION = Histogram(
    name="engine_node_schedule_pre_process_duration",
    documentation="time spent node handler schedule pre-processing",
    buckets=get_histogram_buckets_from_evn("ENGINE_NODE_SCHEDULE_TIME_BUCKETS"),
    labelnames=["type", "hostname"],
)
ENGINE_NODE_SCHEDULE_POST_PROCESS_DURATION = Histogram(
    name="engine_node_schedule_post_process_duration",
    documentation="time spent node handler schedule post-processing",
    buckets=get_histogram_buckets_from_evn("ENGINE_NODE_SCHEDULE_TIME_BUCKETS"),
    labelnames=["type", "hostname"],
)

# runtime metrics
ENGINE_RUNTIME_CONTEXT_VALUE_READ_TIME = Histogram(
    name="engine_runtime_context_value_read_time",
    documentation="time spent reading context value",
    labelnames=["hostname"],
)
ENGINE_RUNTIME_CONTEXT_REF_READ_TIME = Histogram(
    name="engine_runtime_context_ref_read_time",
    documentation="time spent reading context value reference",
    labelnames=["hostname"],
)
ENGINE_RUNTIME_CONTEXT_VALUE_UPSERT_TIME = Histogram(
    name="engine_runtime_context_value_upsert_time",
    documentation="time spent upserting context value",
    labelnames=["hostname"],
)

ENGINE_RUNTIME_DATA_INPUTS_READ_TIME = Histogram(
    name="engine_runtime_data_inputs_read_time",
    documentation="time spent reading node data inputs",
    labelnames=["hostname"],
)
ENGINE_RUNTIME_DATA_OUTPUTS_READ_TIME = Histogram(
    name="engine_runtime_data_outputs_read_time",
    documentation="time spent reading node data outputs",
    labelnames=["hostname"],
)
ENGINE_RUNTIME_DATA_READ_TIME = Histogram(
    name="engine_runtime_data_read_time",
    documentation="time spent reading node data inputs and outputs",
    labelnames=["hostname"],
)

ENGINE_RUNTIME_EXEC_DATA_INPUTS_READ_TIME = Histogram(
    name="engine_runtime_exec_data_inputs_read_time",
    documentation="time spent reading node execution data inputs",
    labelnames=["hostname"],
)
ENGINE_RUNTIME_EXEC_DATA_OUTPUTS_READ_TIME = Histogram(
    name="engine_runtime_exec_data_outputs_read_time",
    documentation="time spent reading node execution data outputs",
    labelnames=["hostname"],
)
ENGINE_RUNTIME_EXEC_DATA_READ_TIME = Histogram(
    name="engine_runtime_exec_data_read_time",
    documentation="time spent reading node execution data inputs and outputs",
    labelnames=["hostname"],
)
ENGINE_RUNTIME_EXEC_DATA_INPUTS_WRITE_TIME = Histogram(
    name="engine_runtime_exec_data_inputs_write_time",
    documentation="time spent writing node execution data inputs",
    labelnames=["hostname"],
)
ENGINE_RUNTIME_EXEC_DATA_OUTPUTS_WRITE_TIME = Histogram(
    name="engine_runtime_exec_data_outputs_write_time",
    documentation="time spent writing node execution data outputs",
    labelnames=["hostname"],
)
ENGINE_RUNTIME_EXEC_DATA_WRITE_TIME = Histogram(
    name="engine_runtime_exec_data_write_time",
    documentation="time spent writing node execution data inputs and outputs",
    labelnames=["hostname"],
)
ENGINE_RUNTIME_CALLBACK_DATA_READ_TIME = Histogram(
    name="engine_runtime_callback_data_read_time",
    documentation="time spent reading node callback data",
    labelnames=["hostname"],
)
ENGINE_RUNTIME_SCHEDULE_READ_TIME = Histogram(
    name="engine_runtime_schedule_read_time", documentation="time spent reading schedule", labelnames=["hostname"]
)
ENGINE_RUNTIME_SCHEDULE_WRITE_TIME = Histogram(
    name="engine_runtime_schedule_write_time", documentation="time spent writing schedule", labelnames=["hostname"]
)

ENGINE_RUNTIME_STATE_READ_TIME = Histogram(
    name="engine_runtime_state_read_time", documentation="time spent reading state", labelnames=["hostname"]
)
ENGINE_RUNTIME_STATE_WRITE_TIME = Histogram(
    name="engine_runtime_state_write_time", documentation="time spent writing state", labelnames=["hostname"]
)

ENGINE_RUNTIME_NODE_READ_TIME = Histogram(
    name="engine_runtime_node_read_time", documentation="time spent reading node", labelnames=["hostname"]
)

ENGINE_RUNTIME_PROCESS_READ_TIME = Histogram(
    name="engine_runtime_process_read_time", documentation="time spent reading process", labelnames=["hostname"]
)
ENGINE_RUNTIME_EXECUTE_TASK_CLAIM_DELAY = Histogram(
    name="engine_runtime_execute_task_claim_delay",
    documentation="delay between execute task send and task claim",
    labelnames=["hostname"],
)
ENGINE_RUNTIME_SCHEDULE_TASK_CLAIM_DELAY = Histogram(
    name="engine_runtime_schedule_task_claim_delay",
    documentation="delay between schedule task send and task claim",
    labelnames=["hostname"],
)
