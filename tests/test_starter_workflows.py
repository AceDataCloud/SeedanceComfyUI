"""Importable starter graphs: separate paid submit from same-ID native media."""
import json
import unittest
from pathlib import Path

from test_package import Client, client_module, nodes

ROOT = Path(__file__).resolve().parents[1]


class StarterWorkflowTests(unittest.TestCase):
    def read(self, name):
        return json.loads((ROOT / "examples" / name).read_text())

    def widget_values(self, item, cls):
        required = cls.INPUT_TYPES()["required"]
        names = [key for key, schema in required.items()
                 if not (schema[1] if len(schema) > 1 else {}).get("forceInput")]
        self.assertEqual(len(names), len(item["widgets_values"]))
        return dict(zip(names, item["widgets_values"]))

    def test_submit_template_prepares_real_contract_but_has_no_polling_or_key(self):
        graph = self.read("02-submit-once.json")
        self.assertNotIn("Bearer ", json.dumps(graph))
        custom = [item for item in graph["nodes"] if item["type"] in nodes.NODE_CLASS_MAPPINGS]
        self.assertEqual(len(custom), 1)
        item = custom[0]
        cls = nodes.NODE_CLASS_MAPPINGS[item["type"]]
        self.assertEqual(cls.SPEC["operation"], "generate")
        values = self.widget_values(item, cls)
        parameters = json.loads(values.pop("parameters_json"))
        parameters.update({key: value for key, value in values.items()
                           if value != "" and value != nodes.SENTINEL})
        method, path, body, *_ = Client("offline-test-key").prepare(cls.TOOL, parameters)
        self.assertEqual(method, "POST")
        self.assertFalse(path.endswith("/tasks"))
        self.assertIn("model", body)
        # Only inspect/validate the transport payload. No invoke or network call.

    def test_retrieve_template_only_queries_same_id_and_connects_native_media(self):
        graph = self.read("03-retrieve-native-media.json")
        items = {item["id"]: item for item in graph["nodes"]}
        custom = [item for item in graph["nodes"] if item["type"] in nodes.NODE_CLASS_MAPPINGS]
        task = next(item for item in custom
                    if getattr(nodes.NODE_CLASS_MAPPINGS[item["type"]], "SPEC", {}).get("operation") == "task")
        cls = nodes.NODE_CLASS_MAPPINGS[task["type"]]
        values = self.widget_values(task, cls)
        self.assertEqual(values["task_id"], "PASTE_YOUR_TASK_ID_HERE")
        self.assertEqual(values["wait_seconds"], 240)
        self.assertTrue(all(getattr(nodes.NODE_CLASS_MAPPINGS[item["type"]], "SPEC", {}).get("operation") != "generate"
                            for item in custom))
        media = next(item for item in custom if item is not task)
        self.assertTrue(media["type"].endswith(("LoadImage", "LoadVideo")))
        media_type = nodes.NODE_CLASS_MAPPINGS[media["type"]].RETURN_TYPES[0]
        edges = graph["links"]
        self.assertTrue(any(edge[1:5] == [task["id"], 3, media["id"], 0] and edge[5] == "STRING" for edge in edges))
        self.assertTrue(any(edge[1] == media["id"] and edge[5] == media_type
                            and items[edge[3]]["type"] in ("PreviewImage", "SaveVideo") for edge in edges))
        for edge in edges:
            source, target = items[edge[1]], items[edge[3]]
            self.assertIn(edge[0], source["outputs"][edge[2]]["links"])
            self.assertEqual(target["inputs"][edge[4]]["link"], edge[0])
