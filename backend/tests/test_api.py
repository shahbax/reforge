"""Full API flow via TestClient (inline jobs => synchronous completion)."""

YT = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"


def test_health(client):
    assert client.get("/health").json() == {"ok": True}


def test_full_analysis_to_export_flow(client):
    me = client.get("/api/v1/me").json()
    assert me["credits"] >= 2

    # 1. Analyze
    r = client.post("/api/v1/analyses", json={"url": YT})
    assert r.status_code == 202, r.text
    pid = r.json()["project_id"]

    a = client.get(f"/api/v1/analyses/{pid}").json()
    assert a["status"] == "AWAITING_CONCEPT_SELECTION"
    assert a["viral_dna"]["hook"]["strength"] >= 0
    assert len(a["concepts"]["concepts"]) >= 5

    # 2. Generate a script from the first concept
    r2 = client.post(
        f"/api/v1/projects/{pid}/script",
        json={"concept_index": 0, "controls": {"platform": "youtube", "duration_seconds": 180}},
    )
    assert r2.status_code == 202, r2.text
    sid = r2.json()["script_id"]

    s = client.get(f"/api/v1/projects/{pid}/script").json()
    assert s["status"] == "COMPLETED"
    assert s["script"]["word_count"] > 0
    assert 0 <= s["originality_report"]["originality_score"] <= 100
    assert s["originality_report"]["disclaimer"]

    # 3. Rewrite (idempotent even with no flags)
    r3 = client.post(f"/api/v1/scripts/{sid}/rewrite", json={"target": "flagged"})
    assert r3.status_code == 202

    # 4. Export
    md = client.get(f"/api/v1/projects/{pid}/export?format=md")
    assert md.status_code == 200
    assert "Originality analysis" in md.text
    assert "not legal" in md.text  # disclaimer present

    # 5. Usage reflects real token accounting
    u = client.get("/api/v1/usage").json()
    assert u["totals"]["input_tokens"] > 0
    assert u["by_stage"]

    # 6. Project appears in history
    listed = client.get("/api/v1/projects").json()["projects"]
    assert any(p["project_id"] == pid for p in listed)


def test_dedupes_same_video(client):
    first = client.post("/api/v1/analyses", json={"url": YT}).json()["project_id"]
    second = client.post("/api/v1/analyses", json={"url": YT}).json()
    assert second["project_id"] == first
    assert second.get("deduped") is True


def test_rejects_unsupported_host(client):
    r = client.post("/api/v1/analyses", json={"url": "https://evil.example.com/x"})
    assert r.status_code == 422
    assert "error" in r.json()


def test_credit_exhaustion_returns_402(client):
    client.post("/api/v1/me/credits/refill", params={"credits": 1})
    r1 = client.post("/api/v1/analyses", json={"url": "https://youtu.be/aaaaaaaaaaa"})
    assert r1.status_code == 202
    r2 = client.post("/api/v1/analyses", json={"url": "https://youtu.be/bbbbbbbbbbb"})
    assert r2.status_code == 402


def test_requires_ownership(client):
    pid = client.post("/api/v1/analyses", json={"url": YT}).json()["project_id"]
    # A different dev user (via X-Dev-User) must not see it.
    r = client.get(f"/api/v1/analyses/{pid}", headers={"X-Dev-User": "someone-else"})
    assert r.status_code == 404
