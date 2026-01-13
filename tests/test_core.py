import pytest
from unittest.mock import MagicMock, patch
import datetime
from bson.objectid import ObjectId

# Import functions from the main app
from bug_tracker import create_bug, update_bug_status

@patch('bug_tracker.get_db_collection')
@patch('bug_tracker.log_audit_event')
def test_create_bug(mock_log, mock_get_collection):
    # Setup mock
    mock_collection = MagicMock()
    mock_collection.insert_one.return_value.inserted_id = ObjectId()
    mock_get_collection.return_value = mock_collection

    # Execute
    bug_id = create_bug("Test Bug", "Test Description", "low", "p2", "test_module")

    # Assert
    assert isinstance(bug_id, str)
    mock_collection.insert_one.assert_called_once()
    mock_log.assert_called_once()

@patch('bug_tracker.get_db_collection')
@patch('bug_tracker.log_audit_event')
def test_update_bug_status(mock_log, mock_get_collection):
    # Setup mock
    mock_collection = MagicMock()
    mock_collection.update_one.return_value.modified_count = 1
    mock_get_collection.return_value = mock_collection

    # Execute
    bug_id = str(ObjectId())
    result = update_bug_status(bug_id, "resolved")

    # Assert
    assert result is True
    mock_collection.update_one.assert_called_once()
    mock_log.assert_called_once()
