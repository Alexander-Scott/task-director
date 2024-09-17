# Task Sharding

[![codecov](https://codecov.io/gh/Alexander-Scott/task-sharding/branch/main/graph/badge.svg?token=FJFLCZFUKA)](https://codecov.io/gh/Alexander-Scott/task-sharding)
[![CI](https://github.com/Alexander-Scott/task-sharding/actions/workflows/ci.yml/badge.svg)](https://github.com/Alexander-Scott/task-director/actions/workflows/ci.yml)

## Overview

The idea behind Task Sharding is to allow one large task to be split up into multiple smaller tasks which are then distributed across available clients. It was originally designed with Bazel in mind, with the compilation of most complex targets being distributed amongst clients and the output shared across clients via a remote cache. It is most effective with complex targets that are very low down in the build graph and have an extreme number of dependencies.

The task-sharding application consists of three parts: server, client and runner, as well as a common language: a schema.

### The schema

A schema is a pre-defined list of tasks which the client knows how to interpret, normally defined in a YAML file.

### The server

The server is what facilitates the communication between clients and is what assigns schema tasks to individual clients. The server does not have knowledge about the content within each tasks, rather it keeps track of which clients are running which tasks.

### The client

A client connects to the server and supplies client information as well as which tasks it needs to see finished.

### The runner

The runner is what executes a task when instructed. Only an abstract runner is provided by default and the idea is that individual projects implement project specific task runners based on requirements.

## Getting started - The bazel example

This section aims to guide a user in setting up the task-sharding application within a bazel context.

### 1) Create a schema

As mentioned above, a schema is a list of tasks and a unique name. They can be anything from simple integers to bazel build targets. 

```yaml
name: bazel
tasks:
  - task: //:test_my_script_1
  - task: //:test_my_script_2
  - task: //:test_my_script_3
```

### 2) Create a Python class that is able interpret schema steps

This new Python class must inherit from TaskRunner and implement two methods: `run` and `abort`. The client will create an instance of this new class and will call `run` with a `task_id` parameter whenever a task in the schema should be started. `abort` is called when the client determines that the current task should be aborted.

```python
from task_sharding_client.task_runner import TaskRunner

class BazelTask(TaskRunner):
    def __init__(self, schema: dict, config: any):
        super().__init__(schema, config)
        self._process = None

    def run(self, task_id: str) -> int:
        target = self._schema["tasks"][int(task_id)]["task"]
        self._process = subprocess.Popen(["bazel", "test", target])
        stdout, stderr = self._process.communicate()
        exit_code = self._process.wait()

        return exit_code

    def abort(self):
        if self._process:
            self._process.terminate()
```

### 4) Create a Python script that starts the client


```python
from bazel_task import BazelTask
from task_sharding_client.connection import Connection
from task_sharding_client.client import Client

if __name__ == "__main__":
    with Connection("server_ip:sever_port", client_id) as connection:
        client = Client(configuration, connection, BazelTask)
        sys.exit(client.run())
```


### 5) Starting the sever

Fortunately a docker-compose file is provided to allow for a one-command setup.

```bash
docker-compose -f server/docker-compose.yaml up -d
```

### 6) Start the client script


