"""
TiDB faq_embeddings アップロードモジュール

Discord メッセージレコードを TiDB Serverless の faq_embeddings テーブルに
チャンネルごとに洗い替え（DELETE → INSERT）する。

必要な環境変数:
    TIDB_HOST     : TiDB クラスターのホスト名
    TIDB_PORT     : ポート番号（デフォルト: 4000）
    TIDB_USER     : ユーザー名
    TIDB_PASSWORD : パスワード
    TIDB_DATABASE : データベース名
    TIDB_SSL_CA   : CA 証明書ファイルパス（省略可・省略時はシステムデフォルト）
"""

import json
import os
import ssl
import uuid
from datetime import datetime, timezone

import pymysql


def _connect() -> pymysql.Connection:
    """環境変数から TiDB に接続する。"""
    host = os.environ["TIDB_HOST"]
    port = int(os.environ.get("TIDB_PORT", "4000"))
    user = os.environ["TIDB_USER"]
    password = os.environ["TIDB_PASSWORD"]
    database = os.environ["TIDB_DATABASE"]
    ssl_ca = os.environ.get("TIDB_SSL_CA", "").strip()

    ssl_args: dict = {}
    if ssl_ca:
        ssl_ctx = ssl.create_default_context(cafile=ssl_ca)
        ssl_args["ssl"] = ssl_ctx

    return pymysql.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database,
        charset="utf8mb4",
        **ssl_args,
    )


def upsert_discord_faq(channel_id: str, records: list[dict]) -> int:
    """
    channel_id に紐づく discord レコードを洗い替えし、挿入件数を返す。

    既存の discord レコード（同 channel_id）を削除してから
    records を一括 INSERT する。records が空の場合は削除のみ行う。

    Args:
        channel_id: Discord チャンネル ID（削除対象の絞り込みに使用）
        records   : to_faq_records() が返した dict のリスト

    Returns:
        挿入したレコード数
    """
    conn = _connect()
    try:
        with conn.cursor() as cur:
            # 既存レコードを削除
            cur.execute(
                "DELETE FROM faq_embeddings"
                " WHERE content_type = 'discord'"
                " AND JSON_EXTRACT(metadata, '$.channel_id') = %s",
                (channel_id,),
            )

            if not records:
                conn.commit()
                return 0

            # 一括 INSERT
            now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
            rows = [
                (
                    str(uuid.uuid4()),
                    rec["content"],
                    "discord",
                    json.dumps(
                        {
                            "message_id": rec["message_id"],
                            "channel_id": rec["channel_id"],
                            "channel_name": rec["channel_name"],
                            "author": rec["author"],
                            "author_id": rec["author_id"],
                            "timestamp": rec["timestamp"],
                        },
                        ensure_ascii=False,
                    ),
                    now,
                )
                for rec in records
            ]
            cur.executemany(
                "INSERT INTO faq_embeddings"
                " (id, content, content_type, metadata, created_at)"
                " VALUES (%s, %s, %s, %s, %s)",
                rows,
            )
            conn.commit()
            return len(rows)
    finally:
        conn.close()
