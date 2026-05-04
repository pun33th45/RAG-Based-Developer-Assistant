from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_upload_text_file_indexes_chunks(monkeypatch):
    indexed = {}

    def fake_create_or_update_vector_store(chunks):
        indexed["chunks"] = chunks

    monkeypatch.setattr("app.routes.upload.create_or_update_vector_store", fake_create_or_update_vector_store)

    response = client.post(
        "/upload",
        files={"file": ("notes.txt", b"DevInsight AI indexes project files for RAG answers.", "text/plain")},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "notes.txt"
    assert data["documents"] == 1
    assert data["chunks"] >= 1
    assert len(indexed["chunks"]) == data["chunks"]


def test_upload_rejects_unsupported_file_type():
    response = client.post(
        "/upload",
        files={"file": ("image.exe", b"not a supported source file", "application/octet-stream")},
    )

    assert response.status_code == 400
    assert "Unsupported file type" in response.json()["detail"]
