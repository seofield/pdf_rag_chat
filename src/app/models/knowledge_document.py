from datetime import datetime
from typing import Optional

from beanie import (
    Document,
    Insert,
    PydanticObjectId,
    Replace,
    Save,
    SaveChanges,
    Update,
    ValidateOnSave,
    before_event,
)
from pydantic import BaseModel, Field

from app.database import beanie_model_register


class BaseDocument(Document):
    created_at: datetime = Field(default_factory=datetime.now, hidden=True)
    modified_at: datetime = Field(default_factory=datetime.now, hidden=True)

    class Settings:
        validate_on_save = True
        use_state_management = True
        state_management_save_previous = True

    @before_event([ValidateOnSave, Update, Insert, Replace, Save, SaveChanges])
    def update_modified_at(self):
        self.modified_at = datetime.now()


@beanie_model_register
class KnowledgeDocument(BaseDocument):
    file_name: str
    file_path: str
    file_size: Optional[int] = None
    file_type: Optional[str] = None
    status: str = Field()
