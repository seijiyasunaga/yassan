#!/usr/bin/env python3
"""今日のスケジュール通知スクリプト"""

import datetime
import json
import os
import sys
from pathlib import Path


def load_schedule(schedule_file: str) -> dict:
    """スケジュールファイルを読み込む"""
    path = Path(schedule_file)
    if not path.exists():
        print(f"エラー: スケジュールファイルが見つかりません: {schedule_file}", file=sys.stderr)
        sys.exit(1)

    with open(path, encoding="utf-8") as f:
        return json.load(f)


def get_today_events(schedule: dict) -> list[dict]:
    """今日のイベントを取得する"""
    today = datetime.date.today().isoformat()
    events = schedule.get("events", [])
    return [e for e in events if e.get("date") == today]


def format_event(event: dict) -> str:
    """イベントを表示用にフォーマットする"""
    time_str = event.get("time", "終日")
    title = event.get("title", "(タイトルなし)")
    location = event.get("location", "")
    description = event.get("description", "")

    lines = [f"  [{time_str}] {title}"]
    if location:
        lines.append(f"           場所: {location}")
    if description:
        lines.append(f"           備考: {description}")
    return "\n".join(lines)


def notify(events: list[dict], date: datetime.date) -> None:
    """スケジュールを通知する"""
    weekdays = ["月", "火", "水", "木", "金", "土", "日"]
    weekday = weekdays[date.weekday()]
    header = f"=== {date.strftime('%Y年%m月%d日')}（{weekday}）のスケジュール ==="

    print(header)
    print()

    if not events:
        print("  本日の予定はありません。")
    else:
        print(f"  {len(events)}件の予定があります:\n")
        for event in sorted(events, key=lambda e: e.get("time", "99:99")):
            print(format_event(event))
    print()


def main() -> None:
    schedule_file = os.environ.get("SCHEDULE_FILE", "schedule.json")
    schedule = load_schedule(schedule_file)
    today = datetime.date.today()
    events = get_today_events(schedule)
    notify(events, today)


if __name__ == "__main__":
    main()
