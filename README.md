# Jyogi Navi

JYOGIの新入生向け情報案内チャットシステムです。

## ドキュメント

詳細な仕様・設計は [`docs/`](docs/) を参照してください。

| ファイル | 内容 |
|---|---|
| [docs/01_feature-list.md](docs/01_feature-list.md) | 機能一覧 |
| [docs/02_tech-stack.md](docs/02_tech-stack.md) | 技術スタック |
| [docs/03_screen-flow.md](docs/03_screen-flow.md) | 画面フロー |
| [docs/04_permission-design.md](docs/04_permission-design.md) | 権限設計 |
| [docs/05_erd.md](docs/05_erd.md) | ER 図 |
| [docs/06_directory.md](docs/06_directory.md) | ディレクトリ構成 |
| [docs/07_infrastructure.md](docs/07_infrastructure.md) | インフラ構成 |
| [docs/08_logging.md](docs/08_logging.md) | ログ設計 |
| [docs/09_schedule_and_issues.md](docs/09_schedule_and_issues.md) | スケジュールと課題 |

## Discord ログの週次更新

Dify のナレッジベースを最新の状態に保つため、週次でDiscordログを更新してください。

### 手順

1. **ログをエクスポート**（詳細は [scripts/ingest/discord/export.md](scripts/ingest/discord/export.md) を参照）

   ```bash
   # 例: DiscordChatExporter CLI で直近3ヶ月をエクスポート
   dce export --token "$DISCORD_TOKEN" --channel <CHANNEL_ID> \
     --format Json --after "$(date -d '3 months ago' '+%Y-%m-%d')" \
     --output scripts/ingest/discord/raw/
   ```

2. **ログを正規化**（個人情報・ノイズを除去）

   ```bash
   py scripts/ingest/discord/normalize.py \
     --input scripts/ingest/discord/raw/ \
     --output scripts/ingest/discord/out/
   ```

3. **Dify にアップロード**

   `scripts/ingest/discord/out/` 以下の `.txt` ファイルを Dify のナレッジベースにアップロードしてください。

> **注意**: `raw/` および `out/` はリポジトリ管理対象外です（`.gitignore` に登録済み）。Discordログを誤ってコミットしないよう注意してください。
