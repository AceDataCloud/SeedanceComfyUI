"""Cancellation boundaries: simulated transport, not a real service call."""
import unittest
from unittest.mock import patch

from test_package import Client, client_module, nodes


class CancelledByHost(Exception):
    pass


class CancellationTests(unittest.TestCase):
    def test_cancel_after_pending_lookup_stops_before_second_request(self):
        stopped = False
        def check():
            if stopped:
                raise CancelledByHost()
        def pending(*args, **kwargs):
            nonlocal stopped
            stopped = True
            return {"status": "pending"}
        client = Client("test-key", check_interrupted=check)
        tool = next(name for name, endpoint in client_module.ENDPOINTS.items()
                    if endpoint.get("operation") == "task")
        with patch.object(client, "_request", side_effect=pending) as request:
            with self.assertRaises(CancelledByHost):
                client.invoke(tool, {"task_id": "existing-task", "wait_seconds": 240})
        self.assertEqual(request.call_count, 1)
        self.assertEqual(request.call_args.args[2]["id"], "existing-task")

    def test_cancel_during_readonly_connection_failure_stops_retries(self):
        stopped = False
        def check():
            if stopped:
                raise CancelledByHost()
        def fail(*args, **kwargs):
            nonlocal stopped
            stopped = True
            raise client_module.requests.Timeout()
        client = Client("test-key", check_interrupted=check)
        with patch.object(client_module.requests, "request", side_effect=fail) as request:
            with self.assertRaises(CancelledByHost):
                client._request("POST", client_module.TASK_PATH, {"id": "existing-task"}, read_only=True)
        self.assertEqual(request.call_count, 1)

    def test_cancel_during_poll_delay_is_observed_without_full_sleep(self):
        stopped = False
        def check():
            if stopped:
                raise CancelledByHost()
        def sleep(seconds):
            nonlocal stopped
            stopped = True
            self.assertLessEqual(seconds, 0.1)
        client = Client("test-key", check_interrupted=check)
        with patch.object(client_module.time, "sleep", side_effect=sleep) as pause:
            with self.assertRaises(CancelledByHost):
                client._pause(5)
        self.assertEqual(pause.call_count, 1)

    def test_node_wires_comfy_cancellation_to_client(self):
        node_type = next(cls for cls in nodes.NODE_CLASS_MAPPINGS.values()
                         if getattr(cls, "SPEC", {}).get("operation") == "task")
        client_name = next(name for name in vars(nodes) if name.startswith("AceData") and name.endswith("Client"))
        pending = {"status": "pending", "task_id": "existing-task", "media_urls": []}
        with patch.object(nodes, "_credential", return_value="test-key"):
            with patch.object(nodes, client_name) as factory:
                factory.return_value.invoke.return_value = pending
                node_type().run("{}", task_id="existing-task")
        self.assertIs(factory.call_args.kwargs["check_interrupted"], nodes._check_comfy_interruption)

    def test_paid_accepted_task_id_survives_late_local_cancel(self):
        stopped = False
        def check():
            if stopped:
                raise CancelledByHost()
        class Response:
            status_code = 200
            headers = {}
            def __enter__(self): return self
            def __exit__(self, *args): return False
            def json(self): return {"task_id": "accepted-task"}
        def accepted(*args, **kwargs):
            nonlocal stopped
            stopped = True
            return Response()
        client = Client("test-key", check_interrupted=check)
        with patch.object(client_module.requests, "request", side_effect=accepted) as request:
            result = client._request("POST", "/paid-submit", {"prompt": "test"}, read_only=False)
        self.assertEqual(result["task_id"], "accepted-task")
        self.assertEqual(request.call_count, 1)
