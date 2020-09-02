from concurrent.futures import ThreadPoolExecutor, wait
from opera.error import OperationError

WORKER_PREFIX = 'Worker'


class NodeExecutor(ThreadPoolExecutor):
    def __init__(self, num_workers=None):
        super().__init__(
            max_workers=num_workers,
            thread_name_prefix=WORKER_PREFIX
        )
        self.futures = {}
        self.processed_nodes = set()
        self.num_workers = num_workers

    def can_submit(self, node_id):
        return (len(self.processed_nodes) < self.num_workers
                and node_id not in self.processed_nodes)

    def submit_operation(self, operation, node_id, verbose, workdir):
        self.processed_nodes.add(node_id)
        self.futures[self.submit(operation, verbose, workdir)] = node_id

    def wait_results(self):
        proceed = bool(self.futures)

        results = wait(
            self.futures,
            return_when="FIRST_COMPLETED"
        )
        errors = self.process_results(results)

        if errors:
            # if errors occurred
            # try cancel pending futures
            running = []
            for fut in self.futures.keys():
                if not fut.cancel():
                    running.append(fut)
            # wait for all running operations to complete
            # and halt execution
            results = wait(
                running,
                return_when="ALL_COMPLETED"
            )
            errors.update(self.process_results(results))
            for node_id in errors:
                print("Error processing node {0}: {1}".format(
                    node_id, errors[node_id])
                )
            raise OperationError("Failed")

        return proceed

    def process_results(self, results):
        errors = {}
        for future in results.done:
            node_id = self.futures.pop(future)
            try:
                future.result()
                self.processed_nodes.remove(node_id)
            except Exception as e:
                errors[node_id] = e

        return errors
