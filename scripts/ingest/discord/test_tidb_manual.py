"""
TiDB 手動確認スクリプト

Discord からメッセージを取得して TiDB に保存できるかを確認する。
Dify へのアップロードはスキップするため、Dify 環境変数は不要。

必要な環境変数:
    DISCORD_BOT_TOKEN   : Discord Bot のトークン
    DISCORD_CHANNEL_IDS : カンマ区切りのチャンネルID（例: "111,222"）
    TIDB_HOST, TIDB_USER, TIDB_PASSWORD, TIDB_DATABASE : TiDB 接続情報

使用例:
    # Windows PowerShell
    $env:DISCORD_BOT_TOKEN="..."
    $env:DISCORD_CHANNEL_IDS="..."
    $env:TIDB_HOST="..."
    $env:TIDB_USER="..."
    $env:TIDB_PASSWORD="..."
    $env:TIDB_DATABASE="..."
    uv run discord/test_tidb_manual.py

    # .env ファイルを使う場合
    uv run --env-file .env discord/test_tidb_manual.py
"""

import os
import sys
from datetime import datetime, timedelta, timezone

from fetch import fetch_channel
from normalize import to_faq_records
from upload_tidb import upsert_discord_faq


def _require_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        print(f"ERROR: 環境変数 {name} が設定されていません", file=sys.stderr)
        sys.exit(1)
    return value


def main() -> None:
    discord_token = _require_env("DISCORD_BOT_TOKEN")
    channel_ids_raw = _require_env("DISCORD_CHANNEL_IDS")
    _require_env("TIDB_HOST")
    _require_env("TIDB_USER")
    _require_env("TIDB_PASSWORD")
    _require_env("TIDB_DATABASE")

    channel_ids = [cid.strip() for cid in channel_ids_raw.split(",") if cid.strip()]
    after_dt = datetime.now(timezone.utc) - timedelta(days=90)

    print("=== TiDB 手動確認 ===")
    print(f"対象チャンネル数: {len(channel_ids)}\n")

    for channel_id in channel_ids:
        print(f"[{channel_id}] 取得中...")
        data = fetch_channel(channel_id, discord_token, after_dt)
        channel_name = data["channel"]["name"]
        messages = data["messages"]
        print(f"  取得: {len(messages)} 件")

        records = to_faq_records(channel_id, channel_name, messages)
        print(f"  正規化後: {len(records)} 件")

        if not records:
            print("  スキップ: 有効なメッセージが0件\n")
            continue

        # 先頭3件をプレビュー
        print("  --- レコードプレビュー（先頭3件）---")
        for r in records[:3]:
            print(f"  author   : {r['author']}")
            print(f"  timestamp: {r['timestamp']}")
            print(f"  content  : {r['content'][:60]}{'...' if len(r['content']) > 60 else ''}")
            print()

        count = upsert_discord_faq(channel_id, records)
        print(f"  TiDB 保存完了: {count} 件\n")

    print("=== 完了 ===")
    print("TiDB Cloud コンソールで確認:")
    print("  SELECT id, content, JSON_EXTRACT(metadata,'$.author') AS author,")
    print("         JSON_EXTRACT(metadata,'$.channel_name') AS channel")
    print("  FROM faq_embeddings WHERE content_type='discord' LIMIT 10;")


if __name__ == "__main__":
    main()
