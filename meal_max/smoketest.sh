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
  curl -s -X DELETE "$BASE_URL/clear-meals" | grep -q '"status": "success"'
}

create_meal() {
  meal=$1
  cuisine=$2
  price=$3
  difficulty=$4

  echo "Adding meal ($meal - $cuisine, $price, $difficulty) to the meal table..."
  curl -s -X POST "$BASE_URL/create-meal" \
    -H "Content-Type: application/json" \
    -d "{\"meal\":\"$meal\", \"cuisine\":\"$cuisine\", \"price\":$price, \"difficulty\":\"$difficulty\"}"

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
  curl -s -X DELETE "$BASE_URL/delete-meal/$meal_id"
  if [ $? -eq 0 ]; then
    echo "Meal deleted successfully."
  else
    echo "Failed to delete meal."
    exit 1
  fi
}

get_meal_by_name() {
  meal_name=$1
  meal_name_encoded=$(echo -n "$meal_name" | jq -s -R -r @uri)

  echo "Getting meal by name: $meal_name"
  response=$(curl -s -X GET "$BASE_URL/get-meal-by-name/$meal_name_encoded")
  if [ $? -eq 0 ]; then
    echo "Meal retrieved successfully by name."
    echo "$response"
  else
    echo "Failed to get meal by name."
    echo $response
    exit 1
  fi
}


get_meal_by_id() {
  meal_id=$1

  echo "Getting meal by ID ($meal_id)..."
  response=$(curl -s -X GET "$BASE_URL/get-meal-by-id/$meal_id")
  if [ $? -eq 0 ]; then
    echo "$response"
  else
    echo "Failed to get meal by ID ($meal_id)."
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
  if [ $? -eq 0 ]; then
    echo "Combatants cleared successfully."
  else
    echo "Failed to clear combatants."
    exit 1
  fi
}

battle() {
  echo "Starting battle..."
  response=$(curl -s -X GET "$BASE_URL/battle")
  if [ $? -eq 0 ]; then
    echo "Meals successfully battled, $(echo -n "$response" | jq -r .winner) is the winner"
  else
    echo "Failed to start battle: $(echo -n "$response" | jq -r .error)"
    exit 1
  fi
}

get_combatants() {
  echo "Getting combatants..."
  response=$(curl -s -X GET "$BASE_URL/get-combatants")
  if [ $? -eq 0 ]; then
    echo "Combatants retrieved successfully."
    echo "$response"
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

  if [ $? -eq 0 ]; then
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

# Function to get the meal leaderboard sorted by play count
get_leaderboard() {
  echo "Getting meal leaderboard sorted by win count..."
  response=$(curl -s -X GET "$BASE_URL/leaderboard")
  if [ $? -eq 0 ]; then
    echo "Meal leaderboard retrieved successfully."
    echo "Leaderboard sorted by meal wins:"
    echo "$response"
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

delete_meal_by_id 1
get_meal_by_id 5
get_meal_by_name "Steak"

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
