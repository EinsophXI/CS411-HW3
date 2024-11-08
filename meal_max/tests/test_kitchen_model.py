import pytest
from meal_max.models.kitchen_model import Meal, create_meal, clear_meals, delete_meal, get_meal_by_id, get_meal_by_name, get_leaderboard, update_meal_stats
from meal_max.utils.sql_utils import get_db_connection

@pytest.fixture
def sample_meal_data():
    """Provides sample meal data for testing."""
    return {'meal': 'Spaghetti', 'cuisine': 'Italian', 'price': 12.99, 'difficulty': 'LOW'}

@pytest.fixture
def setup_database():
    """Setup: Clears the meals table before each test to ensure a clean state."""
    clear_meals()
    yield
    clear_meals()

def test_create_meal_success(setup_database, sample_meal_data):
    """Test successful creation of a meal."""
    create_meal(**sample_meal_data)
    meal = get_meal_by_name(sample_meal_data['meal'])
    assert meal.meal == sample_meal_data['meal']
    assert meal.cuisine == sample_meal_data['cuisine']
    assert meal.price == sample_meal_data['price']
    assert meal.difficulty == sample_meal_data['difficulty']

def test_create_meal_invalid_price(setup_database):
    """Test that creating a meal with an invalid price raises a ValueError."""
    with pytest.raises(ValueError, match="Price must be a positive number"):
        create_meal("Test Meal", "Cuisine", -5.00, "LOW")

def test_create_meal_duplicate_name(setup_database, sample_meal_data):
    """Test that creating a meal with a duplicate name raises a ValueError."""
    create_meal(**sample_meal_data)
    with pytest.raises(ValueError, match="Meal with name 'Spaghetti' already exists"):
        create_meal(**sample_meal_data)

def test_clear_meals(setup_database, sample_meal_data):
    """Test clearing all meals from the table."""
    create_meal(**sample_meal_data)
    clear_meals()
    with pytest.raises(ValueError, match="Meal with name 'Spaghetti' not found"):
        get_meal_by_name("Spaghetti")

def test_delete_meal(setup_database, sample_meal_data):
    """Test soft-deleting a meal by ID."""
    create_meal(**sample_meal_data)
    meal = get_meal_by_name(sample_meal_data['meal'])
    delete_meal(meal.id)
    with pytest.raises(ValueError, match=f"Meal with ID {meal.id} has been deleted"):
        get_meal_by_id(meal.id)

def test_get_meal_by_id_not_found(setup_database):
    """Test that trying to retrieve a non-existent meal by ID raises a ValueError."""
    with pytest.raises(ValueError, match="Meal with ID 1 not found"):
        get_meal_by_id(1)

def test_get_meal_by_name_not_found(setup_database):
    """Test that trying to retrieve a non-existent meal by name raises a ValueError."""
    with pytest.raises(ValueError, match="Meal with name 'NonExistentMeal' not found"):
        get_meal_by_name("NonExistentMeal")

def test_get_leaderboard(setup_database, sample_meal_data):
    """Test leaderboard retrieval, ensuring meals are sorted by wins by default."""
    create_meal(**sample_meal_data)
    meal = get_meal_by_name(sample_meal_data['meal'])
    update_meal_stats(meal.id, 'win')
    leaderboard = get_leaderboard()
    assert len(leaderboard) == 1
    assert leaderboard[0]['meal'] == sample_meal_data['meal']
    assert leaderboard[0]['wins'] == 1

def test_update_meal_stats_win(setup_database, sample_meal_data):
    """Test updating meal stats with a win result."""
    create_meal(**sample_meal_data)
    meal = get_meal_by_name(sample_meal_data['meal'])
    update_meal_stats(meal.id, 'win')
    updated_meal = get_meal_by_id(meal.id)
    assert updated_meal.id == meal.id
    assert updated_meal.difficulty == meal.difficulty

def test_update_meal_stats_invalid_result(setup_database, sample_meal_data):
    """Test that providing an invalid result in update_meal_stats raises a ValueError."""
    create_meal(**sample_meal_data)
    meal = get_meal_by_name(sample_meal_data['meal'])
    with pytest.raises(ValueError, match="Invalid result: draw. Expected 'win' or 'loss'."):
        update_meal_stats(meal.id, 'draw')
