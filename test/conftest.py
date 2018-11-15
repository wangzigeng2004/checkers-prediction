import pytest
from app import create_app

@pytest.fixture
def app():
	app = create_app({
		'TESTING': True,
	})

	yield app