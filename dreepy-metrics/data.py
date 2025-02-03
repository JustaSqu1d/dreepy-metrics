import requests
import time
import json


def get_data(event_ids):
    teams = {}
    all_pokemon = []
    sorted_pokemon_by_name = {}
    pokemon_data = {}

    for event_id in event_ids:
        with open(f"data/teams/{event_id}.json", "r") as f:
            event_data = json.load(f)

        for team in event_data:
            player_name = team["team"]["player_name"]
            team_id = team["url"].split("/")[-1]
            tournament_id = team["url"].split("/")[-2]

            del team["team"]["player_name"]

            team_array = []

            for member in team["team"]:
                name = member
                shadow = team["team"][member]["shadow"]
                purified = team["team"][member]["purified"]
                fast_move = team["team"][member]["fast_move"]
                charge_move1, charge_move2 = team["team"][member]["charge_move1"], team["team"][member]["charge_move2"]
                charge_move_array = sorted([charge_move1, charge_move2]) # sorted so that the order does not matter

                individual_pokemon_data = {
                    "name": name,
                    "shadow": shadow,
                    "purified": purified,
                    "fast_move": fast_move,
                    "charge_move1": charge_move_array[0],
                    "charge_move2": charge_move_array[1],
                    "team_id": team_id
                }

                team_array.append(individual_pokemon_data)
                all_pokemon.append(individual_pokemon_data)

            teams[team_id] = ({
                "player_name": player_name,
                "team": team_array,
                "team_id": team_id,
                "tournament_id": tournament_id
            })

    for pokemon in all_pokemon:
        if pokemon["name"] not in sorted_pokemon_by_name:
            sorted_pokemon_by_name[pokemon["name"]] = []

        sorted_pokemon_by_name[pokemon["name"]].append(pokemon)


    for pokemon_name in sorted_pokemon_by_name:
        pokemon_array = sorted_pokemon_by_name[pokemon_name]
        total_pokemon = len(pokemon_array)
        shadow_pokemon = len([pokemon for pokemon in pokemon_array if pokemon["shadow"]])
        purified_pokemon = len([pokemon for pokemon in pokemon_array if pokemon["purified"]])

        fast_move_counts = {}
        charge_move_combined_counts = {}
        charge_move_individual_counts = {}
        for pokemon in pokemon_array:
            fast_move = pokemon["fast_move"]
            charge_move_array = pokemon["charge_move1"], pokemon["charge_move2"]

            if fast_move not in fast_move_counts:
                fast_move_counts[fast_move] = 0

            fast_move_counts[fast_move] += 1

            if charge_move_array not in charge_move_combined_counts:
                charge_move_combined_counts[charge_move_array] = 0

            charge_move_combined_counts[charge_move_array] += 1

            for charge_move in charge_move_array:
                if not charge_move:
                    continue

                if charge_move not in charge_move_individual_counts:
                    charge_move_individual_counts[charge_move] = 0

                charge_move_individual_counts[charge_move] += 1

        pokemon_data[pokemon_name] = {
            "total_pokemon": total_pokemon,
            "shadow_pokemon": shadow_pokemon,
            "purified_pokemon": purified_pokemon,
            "fast_move_counts": fast_move_counts,
            "charge_move_combined_counts": charge_move_combined_counts,
            "charge_move_individual_counts": charge_move_individual_counts
        }

    return pokemon_data, teams, sorted_pokemon_by_name


def get_events(show_future=False):
    url = "https://raw.githubusercontent.com/JustaSqu1d/play-pokemon-go-data/refs/heads/master/events/events.json"

    events = requests.get(url).json()

    if not show_future:
        events = [event for event in events if time.time() > events.get(event).get("time")]

    blacklisted_events = ["lima2025", "buenosaires2025", "bogota2025"]

    events = [event for event in events if event not in blacklisted_events]

    return events


def get_active_events():
    return ["baltimore2025", "dortmund2025", "joinville2025", "louisville2025", "lille2025",
            "gdansk2025", "laic2025", "sacramento2025", "stuttgart2025", "perth2025", "toronto2025", 
            "birmingham2025", "riodejaneiro2025", "sanantonio2025"]
