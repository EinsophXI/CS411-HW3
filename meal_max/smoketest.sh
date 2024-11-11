#!/bin/bash

# Define the base URL for the Flask API
BASE_URL="http://localhost:5000/api"

# Flag to control whether to echo JSON output
ECHO_JSON=false

# Parse command-line arguments
while [ "$#" -gt 0 ]; do
  case $1 in
    --echo-json) ECHO_JSON=true ;;
    *) echo "Unknown parameter passed: $1"; exit 1 ;;
  esac
  shift
done

###############################################
#
# Health checks
#
###############################################

# Function to check the health of the service
check_health() {
  echo "Checking health status..."
  curl -s -X GET "$BASE_URL/health" | grep -q '"status": "healthy"'
  if [ $? -eq 0 ]; then
    echo "Service is healthy."
  else
    echo "Health check failed."
    exit 1
  fi
}

# Function to check the database connection
check_db() {
  echo "Checking database connection..."
  curl -s -X GET "$BASE_URL/db-check" | grep -q '"database_status": "healthy"'
  if [ $? -eq 0 ]; then
    echo "Database connection is healthy."
  else
    echo "Database check failed."
    exit 1
  fi
}

##########################################################
#
# Meal Management
#
##########################################################

clear_meal_table() {
  echo "Clearing the meal table..."
  curl -s -X DELETE "$BASE_URL/clear-catalog" | grep -q '"status": "success"'
}

create_meal() {
  meal=$1
  cuisine=$2
  price=$3
  difficulty=$4

  echo "Adding meal ($meal - $cuisine, $price, $difficulty) to the meal table..."
  curl -s -X POST "$BASE_URL/create-meal" -H "Content-Type: application/json" \
    -d "{\"meal\":\"$meal\", \"cuisine\":\"$cuisine\", \"price\":$price, \"difficulty\":\"$difficulty\"}")

  if [ $? -eq 0 ]; then
    echo "Meal added successfully."
  else
    echo "Failed to add meal."
    exit 1
  fi
}

delete_meal_by_id() {
  meal_id=$1

  echo "Deleting meal by ID ($meal_id)..."
  response=$(curl -s -X DELETE "$BASE_URL/delete-meal/$meal_id")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal deleted successfully by ID ($meal_id)."
  else
    echo "Failed to delete meal by ID ($meal_id)."
    exit 1
  fi
}

get_meal_by_name() {
  meal_name=$1
  meal_name_encoded=$(echo -n "$meal_name" | jq -s -R -r @uri)

  echo "Getting meal by name: $meal_name"
  response=$(curl -s -X GET "$BASE_URL/get-meal-by-name/$meal_name_encoded")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal retrieved successfully by name."
    if [ "$ECHO_JSON" = true ]; then
      echo "Meal JSON (by name):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get meal by name."
    echo $response
    exit 1
  fi
}

get_all_meals() {
  echo "Getting all meals in the playlist..."
  response=$(curl -s -X GET "$BASE_URL/get-all-meals-from-meal-table")
  if echo "$re  sponse" | grep -q '"status": "success"'; then
    echo "All meals retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Meals JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get meals."
    exit 1
  fi
}

get_meal_by_id() {
  meal_id=$1

  echo "Getting meal by ID ($meal_id)..."
  response=$(curl -s -X GET "$BASE_URL/get-meal-from-meal-table-by-id/$meal_id")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal retrieved successfully by ID ($meal_id)."
    if [ "$ECHO_JSON" = true ]; then
      echo "Meal JSON (ID $meal_id):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get meal by ID ($meal_id)."
    exit 1
  fi
}

get_random_meal() {
  echo "Getting a random meal from the meal table..."
  response=$(curl -s -X GET "$BASE_URL/get-random-meal")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Random meal retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Random Meal JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get a random meal."
    exit 1
  fi
}


############################################################
#
# Battle
#
############################################################

clear_combatants() {
  echo "Clearing combatants..."
  response=$(curl -s -X POST "$BASE_URL/clear-combatants")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Combatants cleared successfully."
  else
    echo "Failed to clear combatants."
    exit 1
  fi
}

battle() {
  echo "Starting battle..."
  response=$(curl-s -X GET "$BASE_URL/battle")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meals successfully battled, $(echo -n "$response" | jq -r .winner) is the winner"
  else
    echo "Failed to start battle: $(echo -n "$response" | jq -r .error)"
    exit 1
  fi
}

get_combatants() {
  echo "Getting combatants..."
  response=$(curl -s -X GET "$BASE_URL/get-combatants")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Combatants retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Combatants JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get combatants."
    exit 1
  fi
}

prep_combatant() {
  meal=$1
  echo "Prepping combatant: $meal..."
  response=$(curl -s -X POST "$BASE_URL/prep-combatant" \
    -H "Content-Type: application/json" \
    -d "{\"meal\":\"$meal\"}")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "$meal successfully prepped."
  else
    echo "Failed to prep meal: $(echo -n "$response" | jq -r .error)"
    exit 1
  fi
}

######################################################
#
# Leaderboard
#
######################################################

# Function to get the song leaderboard sorted by play count
get_leaderboard() {
  echo "Getting meal leaderboard sorted by play count..."
  response=$(curl -s -X GET "$BASE_URL/meal-leaderboard?sort=play_count")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal leaderboard retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Leaderboard JSON (sorted by play count):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get meal leaderboard."
    exit 1
  fi
}


# Health checks
check_health
check_db

#Create Meals
create_meal "Pasta" "Italian" 20.0 "LOW"
create_meal "Tacos" "Mexican" 22.0 "LOW"
create_meal "Steak" "French" 24.0 "MED"
create_meal "Sushi" "Japanese" 32.0 "HIGH"
create_meal "Dosa" "Indian" 34.0 "HIGH"

delete_meal 1
get_meal_by_id 2
get_meal_by_name "Steak"
get_random_meal
get_all_meals

prep_combatant "Tacos"
prep_combatant "Dosa"
get_combatants
battle
prep_combatant "Steak"
battle
prep_combatant "Sushi"
battle

get_leaderboard

clear_meal_table
clear_combatants

echo "All tests passed successfully!"
