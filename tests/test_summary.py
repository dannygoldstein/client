import pytest
import wandb
import numpy as np


@pytest.fixture
def api(runner):
    return wandb.Api()


def test_nested_summary(api, mock_server):
    run = api.runs("test/test")[0]
    summary_dict = {"a": {"b": {"c": 0.9}}}
    summary = wandb.old.summary.Summary(run, summary_dict)
    assert summary["a"]["b"]["c"] == 0.9


def test_summary_setitem(api, mock_server):
    run = api.runs("test/test")[0]
    run.summary["acc2"] = run.summary["acc"]
    run.summary["nested"] = {"a": 1, "b": {"c": 2, "d": 3}}
    run.summary.update()


def test_summary_media_setitem(api, mock_server):
    run = api.runs("test/test")[0]
    try:
        run.summary["img"] = wandb.Image(np.random.random((100, 100)))
        run.summary.update()
        raise Exception()
    except Exception as e:
        assert "Cannot bind Media object" in str(e)


@pytest.mark.wandb_args(wandb_init={"project": "test", "name": "test", "id": test})
def test_summary_media_setitem_current_run(api, live_mock_server, test_settings, wandb_init_run):
    run = api.runs("test/test")[0]
    run.summary["img"] = wandb.Image(np.random.random((100, 100)))
    run.summary.update()
