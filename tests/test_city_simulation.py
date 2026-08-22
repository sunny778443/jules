import pytest
from simulate_city import VirtualCity, run_75_year_life_simulation


def test_virtual_city_experiences():
    city = VirtualCity()
    exp1 = city.get_yearly_experience(10)
    assert exp1["stage"] == "Youth & Education"
    assert "social_bot" in exp1

    exp75 = city.get_yearly_experience(75)
    assert exp75["stage"] == "Elder Reflection"


def test_75_year_simulation_run():
    res = run_75_year_life_simulation()
    assert res["step"] == 76
    assert "inner_thought_stream" in res
    assert res["dominant_emotion"] in ["fear", "anxiety", "anger"]
