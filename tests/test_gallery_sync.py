import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

spec = importlib.util.spec_from_file_location("sync_gallery", Path(__file__).resolve().parents[1] / "scripts/sync_gallery.py")
sync = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sync)


class PublisherTests(unittest.TestCase):
    def test_github_only_files_are_never_selected(self):
        for path in ["ADAPTATION_REPORT.md", "REUSE.toml", "smoke_test.ipynb", "THIRD_PARTY_NOTICES.md", "VALIDATION.md", ".github/workflows/sync-gallery.yml", "scripts/sync_gallery.py", "tests/test_gallery_sync.py", "requirements-gallery-sync.txt", "course_content/environment/image.txt", "course_content/slides/a.pdf", "course_content/tutorials/tutorial_assets/model.bin", "course_content/tutorials/.ipynb_checkpoints/a.ipynb"]:
            with self.subTest(path=path):
                self.assertFalse(sync.selected(path))
        self.assertTrue(sync.selected("course_content/tutorials/new_lesson.ipynb"))
        self.assertTrue(sync.selected("course_content/html/new_lesson.html"))

    def test_invalid_upload_response_aborts_before_put(self):
        client = sync.GalleryClient("test-token", "test-gallery")
        client.api = Mock(return_value={"Urls": [{"Filename": "index.ipynb", "Url": ""}]})
        with self.assertRaises(sync.SyncError):
            client.upload_urls(["index.ipynb"])

    def test_contributing_replaces_duplicate_course_readme_in_gallery(self):
        self.assertTrue(sync.selected("CONTRIBUTING.md"))
        self.assertFalse(sync.selected("course_content/README.md"))

    def test_expired_oss_url_refreshes_without_sending_credentials(self):
        client = sync.GalleryClient("test-token", "test-gallery")
        client.upload_urls = Mock(return_value={"index.ipynb": "https://oss.example/new"})
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "index.ipynb").write_text("notebook")
            payloads = []
            def upload_result(url, **kwargs):
                body = kwargs["data"]
                self.assertTrue(hasattr(body, "read"))
                payloads.append(body.read())
                return Mock(ok=False, status_code=403) if len(payloads) == 1 else Mock(ok=True)
            with patch.object(sync.requests, "put", side_effect=upload_result) as put, patch.object(sync.time, "sleep"):
                client.upload(root, "index.ipynb", "https://oss.example/expired")
            self.assertEqual(payloads, [b"notebook", b"notebook"])
            client.upload_urls.assert_called_once_with(["index.ipynb"])
            self.assertEqual(put.call_args.args[0], "https://oss.example/new")
            self.assertNotIn("Authorization", put.call_args.kwargs["headers"])
            self.assertNotIn("cookies", put.call_args.kwargs)

    def run_publish(self, change=False, bad_size=False, website=False):
        original = {"Name": "course", "Owner": "VoyagerX", "Role": "admin", "Category": "notebook", "EntryFile": "index.ipynb", "Files": ["old.txt"], "Label": ["course"], "Private": False, "GmtUpdated": "original"}
        name = "index.html" if website else "index.ipynb"
        if website:
            original.update(Category="website", EntryFile=name)
        current = dict(original, GmtUpdated="changed") if change else original
        final = dict(original, Files=[name])
        client = Mock(gid="gid")
        client.gallery.side_effect = [original, current, final]
        client.upload_urls.return_value = {name: "https://oss.example/url"}
        client.api.return_value = {"Files": [{"FileName": name, "Size": 0 if bad_size else 8}]}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / name).write_text("notebook")
            if change or bad_size:
                with self.assertRaises(sync.SyncError):
                    sync.publish(client, root, [name])
                self.assertFalse(any(call.args[0] == "PUT" for call in client.api.call_args_list))
            else:
                sync.publish(client, root, [name])
                writes = [call for call in client.api.call_args_list if call.args[0] == "PUT"]
                self.assertEqual(writes[-1].args[1], "/api/v1/gallery/publish")
                payload = writes[0].kwargs["json"]
                self.assertEqual(json.loads(payload["Files"]), [name])
                self.assertEqual(payload["EntryFile"], name)
                self.assertEqual(payload["Category"], original["Category"])
                self.assertEqual(payload["Private"], 0)
                self.assertEqual(payload["Name"], "course")
                self.assertEqual(json.loads(payload["Label"]), ["course"])

    def test_concurrent_edit_aborts_publication(self):
        self.run_publish(change=True)

    def test_incomplete_draft_aborts_publication(self):
        self.run_publish(bad_size=True)

    def test_success_updates_manifest_then_publishes(self):
        self.run_publish()

    def test_preserves_existing_html_entry(self):
        self.run_publish(website=True)


if __name__ == "__main__":
    unittest.main()
