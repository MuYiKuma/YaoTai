from dataclasses import dataclass

from scenario_generator import generate_scenarios


@dataclass
class StorageInput:
    power_kw: float
    dod: float
    efficiency: float
    sr_execution_rate: float = 0.97


def test_generate_scenarios_from_dict():
    result = generate_scenarios(
        {
            "power_kw": 1000,
            "dod": 0.97,
            "efficiency": 0.91,
            "sr_execution_rate": 0.99,
        }
    )

    assert result["proposal"]["dod"] == 0.97
    assert result["proposal"]["efficiency"] == 0.9
    assert result["proposal"]["dr_capacity"] == 1000
    assert result["proposal"]["cycles"] is None
    assert result["proposal"]["sr_execution_rate"] == 0.99

    assert result["standard"]["dod"] == 0.95
    assert result["standard"]["efficiency"] == 0.88
    assert result["standard"]["dr_capacity"] == 800
    assert result["standard"]["cycles"] == {"summer": None, "non_summer": 1.5}
    assert result["standard"]["sr_execution_rate"] == 0.9

    assert result["conservative"]["dod"] == 0.9
    assert result["conservative"]["efficiency"] == 0.85
    assert result["conservative"]["dr_capacity"] == 600
    assert result["conservative"]["cycles"] == {"summer": 1, "non_summer": 1}
    assert result["conservative"]["sr_execution_rate"] == 0.8


def test_generate_scenarios_from_dataclass():
    result = generate_scenarios(StorageInput(power_kw=500, dod=0.82, efficiency=0.84))

    assert result["proposal"]["dod"] == 0.82
    assert result["proposal"]["efficiency"] == 0.84
    assert result["proposal"]["dr_capacity"] == 500

    assert result["standard"]["dod"] == 0.82
    assert result["standard"]["efficiency"] == 0.84
    assert result["standard"]["dr_capacity"] == 400

    assert result["conservative"]["dod"] == 0.85
    assert result["conservative"]["efficiency"] == 0.85
    assert result["conservative"]["dr_capacity"] == 300
