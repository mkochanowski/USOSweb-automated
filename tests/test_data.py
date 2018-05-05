import pytest
from usos.data import DataController, NotAnEntity

@pytest.fixture
def data_controller():
    data = DataController(dispatcher=object)
    return data

# data uploads

def test__data_uploads__single_empty_entity(data_controller):
    data_controller.upload({})
    assert len(data_controller._data) == 0

def test__data_uploads__single_entity(data_controller):
    item = {
        "entity": "testing-entity",
        "items": []
    }
    data_controller.upload(item)
    assert item in data_controller._data
    assert len(data_controller._data) == 1

def test__data_uploads__single_not_an_entity(data_controller):
    with pytest.raises(NotAnEntity):
        data_controller.upload({
            "elements": {
                "first-entity": 1,
                "second-entity": 2,
            },
            "type": "testing-entity"
        })

def test__data_uploads__multiple_entities(data_controller):
    entities = [
        { "entity": "testing-entity-1", "items": [] },
        { "entity": "testing-entity-2", "items": [] },
        { "entity": "testing-entity-3", "items": [] }
    ]
    data_controller.upload_multiple(entities)
    for ent in entities:
        assert ent in data_controller._data
    assert len(data_controller._data) == len(entities)

def test__data_uploads__multiple__one_false_entity(data_controller):
    entities = [
        { "entity": "testing-entity-1", "items": [] },
        { "entity": "testing-entity-2", "elements": 0 },
        { "entity": "testing-entity-3", "items": [] }
    ]
    with pytest.raises(NotAnEntity):
        data_controller.upload_multiple(entities)

def test__data_uploads__multiple_no_items(data_controller):
    entities = []
    data_controller.upload_multiple(entities)
    assert len(data_controller._data) == 0
