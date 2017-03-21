import pytest

from mongo_thingy import Model, take_uri_from_env


@pytest.fixture
def setup_env():
    import os
    os.environ["MONGO_URI"] = "mongodb://localhost/test"
    yield
    os.environ.pop("MONGO_URI", None)


def test_take_uri_from_env(setup_env):
    @take_uri_from_env()
    class Foo(Model):
        pass

    assert Foo.database.name == "test"


def test_take_uri_from_env_exit():
    with pytest.raises(SystemExit):
        @take_uri_from_env(exit_if_missing=True)
        class Foo(Model):
            pass
