import json
import pytest
from src.HistoryManager import HistoryManager

@pytest.fixture
def history_manager():
    return HistoryManager()

def test_save_history_success(history_manager):
    history_manager.history = [{"url": "https://www.python.org", "title": "Python"}]
    
    with open("test_history.json", "w") as f:
        json.dump(history_manager.history, f)
        
    assert history_manager.save_history() is None
    
def test_save_history_failure(history_manager):
    with pytest.raises(Exception):
        history_manager.save_history()
        
def test_save_history_empty(history_manager):
    history_manager.history = []
    
    assert history_manager.save_history() is None
