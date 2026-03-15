async def test_DBが正常な場合は200とステータスokを返す(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


async def test_DB接続失敗時は503とステータスdegradedを返す(client, mock_db_session):
    mock_db_session.execute.side_effect = Exception("DB unreachable")
    response = await client.get("/health")
    assert response.status_code == 503
    assert response.json()["status"] == "degraded"
    mock_db_session.execute.side_effect = None  # リセット


async def test_レスポンスにXRequestIDヘッダーが付与される(client):
    response = await client.get("/health")
    assert "x-request-id" in response.headers
