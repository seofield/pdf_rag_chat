from unittest.mock import AsyncMock, patch

import pytest
from fastapi import UploadFile

from app.bo.knowledge_document import (
    create_knowledge_document,
    delete_knowledge_document,
    get_knowledge_documents,
)


@pytest.mark.asyncio
async def test_create_knowledge_document():
    with patch(
        "app.tasks.knowledge_document.parse_document.apply_async"
    ) as mock_parse_document, patch(
        "app.models.knowledge_document.KnowledgeDocument.insert", new_callable=AsyncMock
    ) as mock_insert:
        mock_file = AsyncMock(spec=UploadFile)
        mock_file.name = "test.pdf"
        mock_file.size = 1024

        response = await create_knowledge_document(mock_file)

        response = await create_knowledge_document("/path/to/test.pdf", mock_file)
        mock_insert.assert_called_once()

        assert response == {"message": "File uploaded successfully."}


@pytest.mark.asyncio
async def test_get_knowledge_documents():
    with patch(
        "app.models.knowledge_document.KnowledgeDocument.all", return_value=AsyncMock()
    ) as mock_all:
        mock_all.return_value.to_list.return_value = [
            {"file_name": "test.pdf", "status": "uploaded"}
        ]

        response = await get_knowledge_documents()

        mock_all.assert_called_once()

        assert response == [{"file_name": "test.pdf", "status": "uploaded"}]


@pytest.mark.asyncio
async def test_delete_knowledge_document():
    with patch(
        "app.models.knowledge_document.KnowledgeDocument.find", return_value=AsyncMock()
    ) as mock_find:
        mock_find.return_value.delete.return_value = None

        response = await delete_knowledge_document("/path/to/test.pdf")

        mock_find.assert_called_once_with({"file_path": "/path/to/test.pdf"})
        mock_find.return_value.delete.assert_called_once()

        assert response == {"message": "File deleted successfully."}
