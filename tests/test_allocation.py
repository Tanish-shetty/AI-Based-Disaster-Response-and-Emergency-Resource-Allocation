import pytest
from src.prediction import predict_areas
from src.resource_allocation import allocate_resources, DEFAULT_BUDGET

@pytest.mark.parametrize("factor",[0,1,7])
def test_budget_conservation(data,bundle,factor):
    budget = {r:total*factor for r,total in DEFAULT_BUDGET.items()}
    output = allocate_resources(predict_areas(data,bundle),budget)
    for resource,total in budget.items():
        assert output[resource].sum() == total
        assert output[resource].ge(0).all()
        assert (output[resource] == output[resource].astype(int)).all()

def test_invalid_budget(data,bundle):
    for value in [-1,1.5,True]:
        budget = {**DEFAULT_BUDGET,"rescue_teams":value}
        with pytest.raises(ValueError):
            allocate_resources(predict_areas(data,bundle),budget)

def test_duplicate_areas(data,bundle):
    duplicated = data.copy(); duplicated.loc[1,"area_id"] = duplicated.loc[0,"area_id"]
    with pytest.raises(ValueError):
        allocate_resources(predict_areas(duplicated,bundle))
