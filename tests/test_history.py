import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import core.history as history


def test_diff_last_scan_compares_against_latest_existing_snapshot():
    tmp = tempfile.mkdtemp()
    orig_dir = history.HISTORY_DIR
    history.HISTORY_DIR = tmp
    try:
        target = "https://example.com"
        history.save_snapshot(target, {"metadata": {"timestamp": "t1"}, "result": {"ports": [80]}})
        history.save_snapshot(target, {"metadata": {"timestamp": "t2"}, "result": {"ports": [80, 443]}})
        open(os.path.join(history.history_dir_for(target), "_"), "w").close()  # stray non-json file must be ignored

        files = history.list_history_files(target)
        assert len(files) == 2, f"expected 2 snapshots, found {files}"

        # diff BEFORE saving the current run: must compare against t2 (the latest
        # existing snapshot), not crash on "_" and not compare against t1.
        current = {"metadata": {"timestamp": "t3"}, "result": {"ports": [80, 443, 22]}}
        diff = history.diff_last_scan(target, current)
        assert diff is not None
        assert "22" in str(diff)
    finally:
        history.HISTORY_DIR = orig_dir
        shutil.rmtree(tmp)


def test_different_targets_do_not_share_history():
    tmp = tempfile.mkdtemp()
    orig_dir = history.HISTORY_DIR
    history.HISTORY_DIR = tmp
    try:
        history.save_snapshot("https://a.example", {"metadata": {"timestamp": "t1"}, "result": {}})
        history.save_snapshot("https://b.example", {"metadata": {"timestamp": "t1"}, "result": {}})

        assert len(history.list_history_files("https://a.example")) == 1
        assert len(history.list_history_files("https://b.example")) == 1
        # a target scanned for the first time must never diff against some other target's snapshot
        assert history.diff_last_scan("https://c.example", {"metadata": {"timestamp": "t2"}, "result": {}}) is None
    finally:
        history.HISTORY_DIR = orig_dir
        shutil.rmtree(tmp)


if __name__ == "__main__":
    test_diff_last_scan_compares_against_latest_existing_snapshot()
    test_different_targets_do_not_share_history()
    print("ok")
