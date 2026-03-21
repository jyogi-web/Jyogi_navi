# Discord ログ エクスポート手順

JYOGIのDiscordメンバーチャンネルから直近3ヶ月分のログをエクスポートする手順です。

## 使用ツール

[DiscordChatExporter](https://github.com/Tyrrrz/DiscordChatExporter) の CLI版を使用します。

### インストール

```bash
# .NET 8 SDK がインストールされている場合
dotnet tool install -g DiscordChatExporter.Cli

# または GitHub Releases から単体バイナリをダウンロード
# https://github.com/Tyrrrz/DiscordChatExporter/releases
```

## 事前準備

### Botトークンの取得

1. [Discord Developer Portal](https://discord.com/developers/applications) にアクセス
2. 対象のBotアプリを選択 → 「Bot」タブ → 「Token」をコピー
3. **絶対にトークンをリポジトリにコミットしないこと**

### トークンの設定

```bash
# .env ファイルに記載（.gitignore 対象）
echo "DISCORD_TOKEN=your_token_here" > scripts/ingest/discord/.env

# または環境変数として設定
export DISCORD_TOKEN="your_token_here"
```

### Channel ID の確認

1. Discord クライアントで「開発者モード」を有効化
   （設定 → 詳細設定 → 開発者モード）
2. 対象チャンネルを右クリック → 「IDをコピー」

**対象チャンネル（JYOGIメンバーチャンネル）:**

| チャンネル名 | Channel ID |
|---|---|
| 雑談 | 1215894284428120170 |
| 何でも質問 | 1215901602456539146 |

## エクスポート手順

### 単一チャンネルのエクスポート

```bash
# 直近3ヶ月分をJSON形式でエクスポート
dce export \
  --token "$DISCORD_TOKEN" \
  --channel <CHANNEL_ID> \
  --format Json \
  --after "$(date -d '3 months ago' '+%Y-%m-%d')" \
  --output scripts/ingest/discord/raw/
```

### 複数チャンネルの一括エクスポート

```bash
# チャンネルIDをスペース区切りで指定
CHANNEL_IDS="CHANNEL_ID_1 CHANNEL_ID_2 CHANNEL_ID_3"
THREE_MONTHS_AGO=$(date -d '3 months ago' '+%Y-%m-%d')

for CHANNEL_ID in $CHANNEL_IDS; do
  dce export \
    --token "$DISCORD_TOKEN" \
    --channel "$CHANNEL_ID" \
    --format Json \
    --after "$THREE_MONTHS_AGO" \
    --output scripts/ingest/discord/raw/
done
```

> **macOS の場合**: `date -d` の代わりに `date -v-3m` を使用してください。

### 出力ファイル

エクスポートされたJSONは `scripts/ingest/discord/raw/` 以下に保存されます。

```
scripts/ingest/discord/
├── raw/                    # エクスポートされたJSONファイル（.gitignore対象）
│   ├── チャンネル名.json
│   └── ...
├── out/                    # normalize.py の出力先（.gitignore対象）
│   ├── チャンネル名.txt
│   └── ...
├── export.md               # このファイル
└── normalize.py            # 正規化スクリプト
```

## 正規化

エクスポート後、`normalize.py` で個人情報・ノイズを除去してDify用フォーマットに変換します。

```bash
# 一括処理
python scripts/ingest/discord/normalize.py \
  --input scripts/ingest/discord/raw/ \
  --output scripts/ingest/discord/out/
```

詳細は [normalize.py](normalize.py) を参照してください。

## 注意事項

- `raw/` および `out/` ディレクトリは `.gitignore` に登録済みです。Discordログを誤ってコミットしないよう注意してください。
- Botトークンは秘密情報です。`.env` ファイルや環境変数で管理し、絶対にリポジトリにコミットしないでください。
- エクスポート対象はJYOGIのメンバーチャンネルのみとし、DM等はエクスポートしないでください。
