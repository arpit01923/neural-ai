from services.pdf_chat_service import split_text_into_chunks


def test_split_text_into_chunks_returns_multiple_chunks_with_overlap():
    text = "word " * 250

    chunks = split_text_into_chunks(text, chunk_size=40, chunk_overlap=10)

    assert len(chunks) > 1
    assert all(chunk.strip() for chunk in chunks)
    assert chunks[0].startswith("word")
    assert chunks[1].startswith("word")
