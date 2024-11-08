import pytest

from meal_max.models.battle_model import BattleModel
from meal_max.models.kitchen_model import Meal

@pytest.fixture()
def battle_model():
  """Fixture to provide a new instance of BattleModel for each test."""
  return BattleModel()

@pytest.fixture
def mock_update_meal_stats(mocker):
  """Mock the update_meal_stats function for testing purposes."""
  return mocker.patch("meal_max.models.battle_model.update_meal_stats")

@pytest.fixture
def sample_meal1():
    return Meal(1, 'Meal 1', 'Cuisine 1', 13.69, 'LOW')

@pytest.fixture
def sample_meal2():
    return Meal(2, 'Meal 2', 'Cuisine 2', 9.42, 'MED')

@pytest.fixture
def sample_meal3():
    return Meal(3, 'Meal 3', 'Cuisine 3', 4.5, 'HIGH')

@pytest.fixture
def sample_combatants(sample_meal1, sample_meal2, sample_meal3):
    return [sample_meal1, sample_meal2, sample_meal3]

def test_prep_combatant(battle_model, sample_meal1):
  """Test adding meal to combatant list."""
  battle_model.prep_combatant(sample_meal1)
  assert len(battle_model.combatants) == 1
  assert battle_model.combatants[0].meal == 'Meal 1'


def test_prep_duplicate_combatant(battle_model, sample_meal1):
  """Test error when prepping a duplicate meal to combatant list by ID."""
  battle_model.prep_combatant(sample_meal1)
  with pytest.raises(ValueError, match="Meal with ID 1 already exists in the combatant list."):
    battle_model.prep_combatants(sample_meal1)

def test_clear_combatants(battle_model, sample_meal1, sample_meal2):
  battle_model.combatants.extend([sample_meal1, sample_meal2])
  assert len(battle_model.combatants) == 2
  battle_model.clear_combatants()
  assert len(battle_model.combatants) == 0

def test_clear_combatants(battle_model, caplog):
    """Test clearing the entire combatant list when it's empty."""
    battle_model.clear_combatants()
    assert len(battle_model.combatants) == 0, "Combatant list should be empty after clearing."
    assert "Clearing an empty combatant list." in caplog.text, "Expected warning message when clearing an empty combatant list."

def test_get_battle_score(battle_model, sample_meal1):
   """Test getting battle score of a meal"""
   battle_model.prep_combatants(sample_meal1)
   
   assert battle_model.get_battle_score(sample_meal1) == ((13.69 * 9) - 3)
   
def test_get_combatants(battle_model, sample_combatants):
    """Test successfully retrieving all meals from the combatant list"""
    battle_model.combatants.extend(sample_combatants)
    
    all_meals = battle_model.get_combatants()
    assert len(all_meals) == 3
    assert all_meals[0].id == 1
    assert all_meals[1].id == 2
    assert all_meals[2].id == 3


def test_battle_not_enough_combatants(battle_model):
    model = battle_model
    with pytest.raises(ValueError, match="Two combatants must be prepped for a battle."):
        model.battle()

def test_battle_success(mocker, battle_model, sample_meal1, sample_meal2):
    mocker.patch("meal_max.models.battle_model.get_random", return_value=0.09)
    mocker.patch("meal_max.models.battle_model.update_meal_stats")
    battle_model.combatants = [sample_meal1, sample_meal2]
    assert battle_model.battle() == sample_meal1.meal
    assert len(battle_model.combatants) == 1
    battle_model.combatants = [sample_meal1, sample_meal2]
    mocker.patch("meal_max.models.battle_model.get_random", return_value=0.11)
    assert battle_model.battle() == sample_meal2.meal
    assert len(battle_model.combatants) == 1
