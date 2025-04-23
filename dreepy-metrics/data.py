import time
import json
import os


def get_data(st, event_ids):
    teams = {}
    all_pokemon = []
    sorted_pokemon_by_name = {}
    pokemon_data = {}

    for event_id in event_ids:
        path = os.path.dirname(__file__)
        try:
            with open(path + f"/data/teams/{event_id}.json", "r") as f:
                event_data = json.load(f)
        except FileNotFoundError:
            st.warning(f"No data for {event_id}, yet!")

        for team in event_data:
            player_name = team["player_name"]
            team_id = team["url"].split("/")[-1]
            tournament_id = team["url"].split("/")[-2]

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
    path = os.path.dirname(__file__)
    with open(path + "/data/events/events.json", "r") as f:
        events = json.load(f)

    if not show_future:
        events = [event for event in events if time.time() > events.get(event).get("time")]

    blacklisted_events = ["lima2025", "buenosaires2025", "bogota2025", "carolina2025"]

    events = [event for event in events if event not in blacklisted_events]

    return events


def get_active_events():
    return ["laic2025", "sacramento2025", "stuttgart2025", "perth2025", "toronto2025", 
            "birmingham2025", "riodejaneiro2025", "sanantonio2025", "merida2025", "euic2025", "vancouver2025", 
            "fortaleza2025", "stockholm2025", "brisbane2025", "atlanta2025", "monterrey2025"]
