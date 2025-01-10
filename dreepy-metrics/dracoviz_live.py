import time  # to simulate a real time data, time loop

import pandas as pd
import requests
import streamlit
import streamlit as st


def convert_move_name(move_name):
    if move_name:
        move_name = move_name.replace("_FAST", "")
        move_name = move_name.replace("_PLUS", "+")
        move_name = move_name.replace("SUPER_POWER", "Superpower")
        move_name = move_name.replace("_", " ")
        return move_name.title()
    else:
        return "None"


def convert_species_name(species_name):
    species_name = (species_name.replace(" ", "-")
                    .replace("(", "")
                    .replace(")", "")
                    .replace("Gastrodon-West", "Gastrodon")
                    .replace("Galarian","Galar")
                    .replace("Alolan","Alola")
                    .replace("Paldean", "Paldea")
                    .replace("Hisuian", "Hisui")
                    )

    if "Shadow" in species_name:
        regular_name = species_name.replace("-Shadow", "")
        species_name = f"Shadow ({regular_name})"

    return species_name


st.title("Dracoviz Live")

url = streamlit.text_input("Enter tournament URL")

st.write("Loading may take a while, please be patient.")

url = url.strip()

if url:
    if "tournaments.dracoviz.com/en/tournament/" not in url and "dracoviz.gg/en/tournament/" not in url:
        st.error("Invalid URL")
    else:
        try:
            tournament_id = url.split("/")[-1]
        except:
            st.error("Invalid URL (2)")

    url = f"https://dracoviz-site.vercel.app/api/session/get/?id={tournament_id}"
    headers = {
        "x_authorization": "Basic R50wRuaO7J",
        "x_locale": "en",
    }

    placeholder = st.empty()
    placeholder2 = st.empty()
    placeholder3 = st.empty()

    player_with_teams = {}

    while True:
        response = requests.get(url, headers=headers)

        data = response.json()

        with placeholder:
            if data["state"] == "NOT_STARTED" or data["state"] != "POKEMON_VISIBLE":
                st.warning("Tournament has not started yet.")
                time.sleep(10)
                continue

        matches = []
        for round_data in data["bracket"]:
            for match in round_data["matches"]:
                participants = match["participants"][0]
                player1 = participants[0]["name"]
                player2 = participants[1]["name"]

                score1 = match["score"][0][0]
                score2 = match["score"][0][1]

                if score1 > score2:
                    winner = player1
                elif score2 > score1:
                    winner = player2
                else:
                    winner = None

                matches.append({"player1": player1, "player2": player2, "winner": winner})

        player_dict = {}

        for match in matches:

            player1 = match["player1"]
            player2 = match["player2"]
            winner = match["winner"]

            if player1 not in player_dict:
                player_dict[player1] = {"wins": 0, "losses": 0, "win_rate": 0, "opponents": []}

            if player2 not in player_dict:
                player_dict[player2] = {"wins": 0, "losses": 0, "win_rate": 0, "opponents": []}

            # don't add "Bye" as an opponent
            if player2 != "Bye":
                player_dict[player1]["opponents"].append(player2)
                player_dict[player2]["opponents"].append(player1)

            if winner == player1:
                player_dict[player1]["wins"] += 1
                player_dict[player2]["losses"] += 1

            if winner == player2:
                player_dict[player2]["wins"] += 1
                player_dict[player1]["losses"] += 1

        # calculate win rate
        for player in player_dict:
            wins = player_dict[player]["wins"]
            losses = player_dict[player]["losses"]
            # avoid division by zero
            if wins + losses == 0:
                win_rate = 0
            else:
                win_rate = wins / (wins + losses) * 100
            player_dict[player]["win_rate"] = win_rate

        # now average the win rates of every player's opponents
        for player in player_dict:
            if player == "Bye":
                continue
            opponents = player_dict[player]["opponents"]

            # opponent's win rate is at least 25%, if not, raise it to 25%

            opponent_win_rates = []

            for opponent in opponents:
                opponent_win_rates.append(max(player_dict[opponent]["win_rate"], 25))

            avg_opponent_win_rate = sum(opponent_win_rates) / len(opponent_win_rates)
            player_dict[player]["avg_opponent_win_rate"] = avg_opponent_win_rate

        # now average the win rate of every player's opponents' opponents
        for player in player_dict:
            if player == "Bye":
                continue
            opponents = player_dict[player]["opponents"]
            opponents_opponents = []
            for opponent in opponents:
                # skip "Bye" as an opponent
                if opponent == "Bye":
                    continue
                opponents_opponents += player_dict[opponent]["opponents"]

            opponents_opponents = list(set(opponents_opponents))

            # at least 25% win rate
            opponent_opponent_win_rates = []
            for opponent in opponents_opponents:
                opponent_opponent_win_rates.append(max(player_dict[opponent]["win_rate"], 25))
            avg_opponent_opponent_win_rate = sum(opponent_opponent_win_rates) / len(
                opponent_opponent_win_rates
            )
            player_dict[player][
                "avg_opponent_opponent_win_rate"
            ] = avg_opponent_opponent_win_rate

        # skip "Bye"
        try:
            player_dict.pop("Bye", None)
        except KeyError:
            pass

        tournament_name = data.get("name")

        # find each player's team
        for player in data.get("players", []):
            if player["name"] in player_with_teams:
                player_dict[player.get("name")]["team"] = player_with_teams[player["name"]]
                continue
            else:
                long_string = ""
                for pokemon in player.get("pokemon", []):
                    try:
                        species = convert_species_name(pokemon.get("speciesName"))
                        fast_move = convert_move_name(pokemon.get("fastMove"))
                        charge_move1 = convert_move_name(pokemon.get("chargedMoves")[0])
                        charge_move2 = convert_move_name(pokemon.get("chargedMoves")[1])
                        cp = pokemon.get("cp")
                        pokemon_string = f"{species}  \r\nCP: {cp}  \r\n- {fast_move}  \r\n- {charge_move1}  \r\n- {charge_move2}  \r\n\r\n"
                        long_string += pokemon_string
                    except TypeError:
                        pass

                pokepaste_url = "https://pokepast.es/create"

                pokepaste_response = requests.post(pokepaste_url,
                                                   data={"paste": long_string, "title": f"{player.get('name')}'s {tournament_name} Team"})

                player_dict[player.get("name")]["team"] = pokepaste_response.url

                player_with_teams[player["name"]] = pokepaste_response.url

        # sort by wins, then by number of games played, then by avg opponent win rate, then by avg opponent opponent win rate
        sorted_players = sorted(
            player_dict.items(),
            key=lambda x: (
                x[1]["wins"],
                x[1]["losses"] + x[1]["wins"],
                x[1]["avg_opponent_win_rate"],
                x[1]["avg_opponent_opponent_win_rate"],
            ),
            reverse=True,
        )

        table = {}

        for position, player in enumerate(sorted_players, start=1):
            try:
                table[position] = {
                    "Player": player[0],
                    "Wins": player[1]["wins"],
                    "Losses": player[1]["losses"],
                    "Opponents' Win Rate": f"{player[1]['avg_opponent_win_rate']:.2f}%",
                    "Opponents' Opponents' Win Rate": f"{player[1]['avg_opponent_opponent_win_rate']:.2f}%",
                    "Team": player[1]['team'],
                }
            except KeyError:
                print(player[0])

        with placeholder2:
            df = pd.DataFrame(table).T
            st.dataframe(data=df, column_config={"Team": st.column_config.LinkColumn(display_text="View Team")})


        usage_counter = {}

        total_teams = 0
        total_pokemon_count = 0

        for player in data.get("players", []):
            if player.get("pokemon"):
                total_teams += 1
                for pokemon in player.get("pokemon"):
                    if pokemon.get("speciesName") not in usage_counter:
                        usage_counter[pokemon.get("speciesName")] = 0
                    usage_counter[pokemon.get("speciesName")] += 1
                    total_pokemon_count += 1

        # combine Gastrodon forms

        if "Gastrodon (East)" in usage_counter and "Gastrodon (West)" in usage_counter:
            usage_counter["Gastrodon"] = usage_counter["Gastrodon (East)"] + usage_counter["Gastrodon (West)"]
            del usage_counter["Gastrodon (East)"]
            del usage_counter["Gastrodon (West)"]

        # sort the usage_counter dictionary by value and then by alphabetical order if the values are the same
        sorted_usage_counter = dict(sorted(usage_counter.items(), key=lambda x: (-x[1], x[0])))

        final_usage_counter = {}

        # add percentage
        for pokemon in sorted_usage_counter:
            final_usage_counter[pokemon] = {
                "Count": sorted_usage_counter[pokemon],
                "Percentage": f"{sorted_usage_counter[pokemon] / total_teams * 100:.2f}%"
            }

        with placeholder3:
            df = pd.DataFrame(final_usage_counter).T
            st.dataframe(data=df)

        time.sleep(10)
