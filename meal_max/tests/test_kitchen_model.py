from contextlib import contextmanager
import re
import sqlite3

import pytest

from meal_max.models.kitchen_model import (
    Meal,
    create_meal,
    clear_meals,
    delete_meal,
    get_leaderboard,
    get_meal_by_id,
    get_meal_by_name,
    update_meal_stats,
)

######################################################
#
#    Fixtures
#
######################################################

def normalize_whitespace(sql_query: str) -> str:
    return re.sub(r'\s+', ' ', sql_query).strip()

# Mocking the database connection for tests
@pytest.fixture
def mock_cursor(mocker):
    mock_conn = mocker.Mock()
    mock_cursor = mocker.Mock()

    # Mock the connection's cursor
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None  # Default return for queries
    mock_cursor.fetchall.return_value = []
    mock_conn.commit.return_value = None


    # Mock the get_db_connection context manager from sql_utils
    @contextmanager
    def mock_get_db_connection():
        yield mock_conn  # Yield the mocked connection object

    mocker.patch("meal_max.models.kitchen_model.get_db_connection", mock_get_db_connection)

    return mock_cursor  # Return the mock cursor so we can set expectations per test

######################################################
#
#    Add and delete
#
######################################################

def test_create_meal(mock_cursor):
    """Test creating a new meal in the catalog."""
    """Test creating a new meal in the catalog."""

    # Call the function to create a new meal
    create_meal(meal = "Meal Name", cuisine="Cuisine Type", price = 25.0, difficulty="Difficulty Level") 
    expected_query = normalize_whitespace("""
        INSERT INTO meals (meal, cuisine, price, difficulty)
        VALUES (?, ?, ?, ?)
    """)

    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    # Assert that the SQL query was correct
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Extract the arguments used in the SQL call (second element of call_args)
    actual_arguments = mock_cursor.execute.call_args[0][1]

    # Assert that the SQL query was executed with the correct arguments
    expected_arguments = ("Meal Name", "Cuisine Type", 25.0, "Difficulty Level")
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."

def test_create_meal_duplicate(mock_cursor):
    """Test creating a meal with a duplicate artist, title, and year (should raise an error)."""

    # Simulate that the database will raise an IntegrityError due to a duplicate entry
    mock_cursor.execute.side_effect = sqlite3.IntegrityError("UNIQUE constraint failed: meals.name, meals.cuisine, meals.price")

    # Expect the function to raise a ValueError with a specific message when handling the IntegrityError
    with pytest.raises(ValueError, match=" Meal 'Meal Name', cuisine 'Cuisine Type', price 25.0 and difficulty 'Difficulty Level' already exist"):  # change
        create_meal(meal = "Meal Name", cuisine="Cuisine Type", price = 25.0, difficulty="Difficulty Level")

def test_create_meal_invalid_price():
    """Test error when trying to create a meal with an invalid duration (e.g., negative duration)"""

    # Attempt to create a meal with a negative price
    with pytest.raises(ValueError, match="Invalid price: -25.0 \(must be a positive integer\)."):
        create_meal(meal = "Meal Name", cuisine="Cuisine Type", price = -25.0, difficulty="Difficulty Level") 

    # Attempt to create a meal with a non-integer duration
    with pytest.raises(ValueError, match="Invalid price: invalid \(must be a positive integer\)."):
        create_meal(meal = "Meal Name", cuisine="Cuisine Type", price = "twenty-five", difficulty="Difficulty Level")

def test_delete_meal(mock_cursor):
    """Test soft deleting a meal from the catalog by meal ID."""

    # Simulate that the meal exists (id = 1)
    mock_cursor.fetchone.return_value = ([False])

    # Call the delete_meal function
    delete_meal(1)

    # Normalize the SQL for both queries (SELECT and UPDATE)
    expected_select_sql = normalize_whitespace("SELECT deleted FROM meals WHERE id = ?")
    expected_update_sql = normalize_whitespace("UPDATE meals SET deleted = TRUE WHERE id = ?")

    # Access both calls to `execute()` using `call_args_list`
    actual_select_sql = normalize_whitespace(mock_cursor.execute.call_args_list[0][0][0])
    actual_update_sql = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])

    # Ensure the correct SQL queries were executed
    assert actual_select_sql == expected_select_sql, "The SELECT query did not match the expected structure."
    assert actual_update_sql == expected_update_sql, "The UPDATE query did not match the expected structure."

    # Ensure the correct arguments were used in both SQL queries
    expected_select_args = (1,)
    expected_update_args = (1,)

    actual_select_args = mock_cursor.execute.call_args_list[0][0][1]
    actual_update_args = mock_cursor.execute.call_args_list[1][0][1]

    assert actual_select_args == expected_select_args, f"The SELECT query arguments did not match. Expected {expected_select_args}, got {actual_select_args}."
    assert actual_update_args == expected_update_args, f"The UPDATE query arguments did not match. Expected {expected_update_args}, got {actual_update_args}."

def test_delete_meal_already_deleted(mock_cursor):
    """Test error when trying to delete a meal that's already marked as deleted."""

    # Simulate that the song exists but is already marked as deleted
    mock_cursor.fetchone.return_value = ([True])

    # Expect a ValueError when attempting to delete a song that's already been deleted
    with pytest.raises(ValueError, match= "Meal has already been deleted"):
        delete_meal("Meal Name")

def test_clear_catalog(mock_cursor, mocker):
    """Test clearing the entire meal catalog (removes all meals)."""

    # Mock the file reading
    mocker.patch.dict('os.environ', {'SQL_CREATE_TABLE_PATH': 'sql/create_meal_table.sql'})
    mocker.patch.dict('os.environ', {'SQL_CREATE_TABLE_PATH': 'sql/create_meal_table.sql'})
    mock_open = mocker.patch('builtins.open', mocker.mock_open(read_data="The body of the create statement"))

    # Call the clear_database function
    clear_meals()

    # Ensure the file was opened using the environment variable's path
    mock_open.assert_called_once_with('sql/create_meal_table.sql', 'r')
    mock_open.assert_called_once_with('sql/create_meal_table.sql', 'r')

    # Verify that the correct SQL script was executed
    mock_cursor.executescript.assert_called_once()


######################################################
#
#    Get Meal
#
######################################################
    
    # meal (str): The meal name.
        #cuisine (str): The cuisine.
        #price (int): The price of the meal.
        #difficulty (str): meal type.

#get_meal_by_id 2
#get_meal_by_name "Steak"
#get_random_meal
#get_all_meals

def test_get_meal_by_id(mock_cursor):
    # Simulate that the meal exists (id = 1)
    mock_cursor.fetchone.return_value = (1, "Meal Name", "Cuisine Type", 25.0, "Difficulty level")

    # Call the function and check the result
    result = get_meal_by_id(1)

    # Expected result based on the simulated fetchone return value
    expected_result = Meal("Meal Name", "Cuisine Type", 25.0, "Difficulty Level")

    # Ensure the result matches the expected output
    assert result == expected_result, f"Expected {expected_result}, got {result}"

    # Ensure the SQL query was executed correctly
    expected_query = normalize_whitespace("SELECT id, meal, cuisine, price, difficult, deleted FROM meals WHERE id = ?")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    # Assert that the SQL query was correct
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Extract the arguments used in the SQL call
    actual_arguments = mock_cursor.execute.call_args[0][1]

    # Assert that the SQL query was executed with the correct arguments
    expected_arguments = (1,)
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."

def test_get_meal_by_id_bad_id(mock_cursor):
    # Simulate that no meal exists for the given ID
    mock_cursor.fetchone.return_value = None

    # Expect a ValueError when the song is not found
    with pytest.raises(ValueError, match="Meal with ID 999 not found"):
        get_meal_by_id(999)

def test_get_meal_by_name(mock_cursor):
    mock_cursor.fetchone.return_value = (1, "Meal Name", "Cuisine", 25.0, "Difficulty Level", 180, False)

    # Call the function and check the result
    result = get_meal_by_name("Meal Name", "Cuisine Type", 25.0, "Difficulty Level")

    # Expected result based on the simulated fetchone return value
    expected_result = Meal("Meal Name", "Cuisine Type", 25.0, "Difficulty Level")

    # Ensure the result matches the expected output
    assert result == expected_result, f"Expected {expected_result}, got {result}"

    # Ensure the SQL query was executed correctly
    expected_query = normalize_whitespace("SELECT id, meal, cuisine, price, difficulty,  deleted FROM meals WHERE meal name = ? AND cuisine = ? AND price = ?")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    # Assert that the SQL query was correct
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Extract the arguments used in the SQL call
    actual_arguments = mock_cursor.execute.call_args[0][1]

    # Assert that the SQL query was executed with the correct arguments
    expected_arguments = ("Meal Name", "Cuisine Type", 25.0)
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."

def test_get_leaderboard(mock_cursor, mocker):
    """Test retrieving the leaderboard for meals, sorted by wins or win percentage."""
    
    # Simulate meals data with battles and wins for leaderboard
    mock_cursor.fetchall.return_value = [
        (1, "Pizza", "Italian", 12.99, "LOW", 10, 8, 0.8),
        (2, "Sushi", "Japanese", 15.50, "MED", 12, 10, 0.833),
        (3, "Tacos", "Mexican", 8.75, "HIGH", 15, 12, 0.8)
    ]

    # Test the "wins" sorting
    mocker.patch("meal_max.utils.sql_utils.get_db_connection", return_value=mock_cursor)
    leaderboard = get_leaderboard(sort_by="wins")

    # Expected result after sorting by wins
    expected_leaderboard_wins = [
        {'id': 3, 'meal': 'Tacos', 'cuisine': 'Mexican', 'price': 8.75, 'difficulty': 'HIGH', 'battles': 15, 'wins': 12, 'win_pct': 80.0},
        {'id': 2, 'meal': 'Sushi', 'cuisine': 'Japanese', 'price': 15.5, 'difficulty': 'MED', 'battles': 12, 'wins': 10, 'win_pct': 83.3},
        {'id': 1, 'meal': 'Pizza', 'cuisine': 'Italian', 'price': 12.99, 'difficulty': 'LOW', 'battles': 10, 'wins': 8, 'win_pct': 80.0}
    ]
    
    # Ensure the results match expected
    assert leaderboard == expected_leaderboard_wins, f"Expected {expected_leaderboard_wins}, but got {leaderboard}"

    # Test the "win_pct" sorting
    leaderboard = get_leaderboard(sort_by="win_pct")

    # Expected result after sorting by win percentage
    expected_leaderboard_win_pct = sorted(expected_leaderboard_wins, key=lambda x: x['win_pct'], reverse=True)
    
    # Ensure the results match expected
    assert leaderboard == expected_leaderboard_win_pct, f"Expected {expected_leaderboard_win_pct}, but got {leaderboard}"

    # Ensure the SQL query was constructed correctly
    expected_query = "SELECT id, meal, cuisine, price, difficulty, battles, wins, (wins * 1.0 / battles) AS win_pct FROM meals WHERE deleted = false AND battles > 0 ORDER BY wins DESC"
    actual_query = mock_cursor.execute.call_args[0][0]
    
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

def test_update_meal_stats(mock_cursor, mocker):
    """Test updating meal stats for wins and losses."""

    # Patch the database connection
    mocker.patch("meal_max.utils.sql_utils.get_db_connection", return_value=mock_cursor)

    # Case 1: Meal not found
    mock_cursor.fetchone.return_value = None  # Simulate no record found
    with pytest.raises(ValueError, match="Meal with ID 1 not found"):
        update_meal_stats(1, "win")

    # Case 2: Meal marked as deleted
    mock_cursor.fetchone.return_value = (True,)  # Simulate meal marked as deleted
    with pytest.raises(ValueError, match="Meal with ID 1 has been deleted"):
        update_meal_stats(1, "win")

    # Case 3: Valid meal, update with win
    mock_cursor.fetchone.return_value = (False,)  # Meal exists and is not deleted
    update_meal_stats(1, "win")
    
    # Expected query for updating a win
    expected_win_query = "UPDATE meals SET battles = battles + 1, wins = wins + 1 WHERE id = ?"
    mock_cursor.execute.assert_any_call(expected_win_query, (1,))

    # Case 4: Valid meal, update with loss
    update_meal_stats(1, "loss")
    
    # Expected query for updating a loss
    expected_loss_query = "UPDATE meals SET battles = battles + 1 WHERE id = ?"
    mock_cursor.execute.assert_any_call(expected_loss_query, (1,))

    # Case 5: Invalid result
    with pytest.raises(ValueError, match="Invalid result: draw. Expected 'win' or 'loss'"):
        update_meal_stats(1, "draw")

    # Ensure the SQL query to check deletion status was executed correctly
    expected_check_query = "SELECT deleted FROM meals WHERE id = ?"
    mock_cursor.execute.assert_any_call(expected_check_query, (1,))
