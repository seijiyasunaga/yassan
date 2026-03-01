"""notifier.py のユニットテスト"""

import datetime
import json
import os
import tempfile
import unittest
from io import StringIO
from unittest.mock import patch

from notifier import format_event, get_today_events, load_schedule, notify


class TestLoadSchedule(unittest.TestCase):
    def test_load_valid_schedule(self):
        data = {"events": [{"date": "2026-03-01", "title": "test"}]}
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as f:
            json.dump(data, f)
            tmp_path = f.name
        try:
            result = load_schedule(tmp_path)
            self.assertEqual(result, data)
        finally:
            os.unlink(tmp_path)

    def test_file_not_found(self):
        with self.assertRaises(SystemExit):
            load_schedule("/nonexistent/schedule.json")


class TestGetTodayEvents(unittest.TestCase):
    def setUp(self):
        self.schedule = {
            "events": [
                {"date": "2026-03-01", "title": "今日のイベント"},
                {"date": "2026-03-02", "title": "明日のイベント"},
                {"date": "2026-02-28", "title": "昨日のイベント"},
            ]
        }

    def test_returns_today_only(self):
        today = datetime.date.today().isoformat()
        schedule = {
            "events": [
                {"date": today, "title": "今日のイベント"},
                {"date": "2099-12-31", "title": "未来のイベント"},
            ]
        }
        events = get_today_events(schedule)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["title"], "今日のイベント")

    def test_no_events_today(self):
        schedule = {"events": [{"date": "2099-01-01", "title": "未来のイベント"}]}
        today = datetime.date.today().isoformat()
        events = [e for e in get_today_events(schedule) if e["date"] == today]
        self.assertEqual(len(events), 0)

    def test_empty_schedule(self):
        events = get_today_events({"events": []})
        self.assertEqual(events, [])


class TestFormatEvent(unittest.TestCase):
    def test_full_event(self):
        event = {
            "time": "10:00",
            "title": "会議",
            "location": "会議室B",
            "description": "議題あり",
        }
        result = format_event(event)
        self.assertIn("[10:00] 会議", result)
        self.assertIn("会議室B", result)
        self.assertIn("議題あり", result)

    def test_minimal_event(self):
        event = {"title": "シンプルな予定"}
        result = format_event(event)
        self.assertIn("終日", result)
        self.assertIn("シンプルな予定", result)

    def test_no_location_or_description(self):
        event = {"time": "09:00", "title": "予定"}
        result = format_event(event)
        self.assertNotIn("場所:", result)
        self.assertNotIn("備考:", result)


class TestNotify(unittest.TestCase):
    def test_output_with_events(self):
        events = [{"time": "09:00", "title": "朝会", "location": "", "description": ""}]
        date = datetime.date(2026, 3, 1)
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            notify(events, date)
            output = mock_stdout.getvalue()
        self.assertIn("2026年03月01日", output)
        self.assertIn("朝会", output)

    def test_output_no_events(self):
        date = datetime.date(2026, 3, 1)
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            notify([], date)
            output = mock_stdout.getvalue()
        self.assertIn("予定はありません", output)

    def test_weekday_display(self):
        # 2026-03-02 は月曜日
        date = datetime.date(2026, 3, 2)
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            notify([], date)
            output = mock_stdout.getvalue()
        self.assertIn("月", output)


if __name__ == "__main__":
    unittest.main()
