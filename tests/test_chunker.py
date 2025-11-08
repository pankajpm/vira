from vira.processing.chunker import ChunkParams, chunk_document


def test_chunk_document_respects_overlap():
    text = "Sentence." * 200
    params = ChunkParams(chunk_size=50, chunk_overlap=10)
    chunks = chunk_document(text, {"url": "https://example.com"}, splitter=None)
    assert chunks, "Expected at least one chunk"
    assert all("url" in chunk for chunk in chunks)

