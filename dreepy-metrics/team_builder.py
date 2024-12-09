import pandas as pd
import streamlit as st

from data import get_data, get_events

events = get_events()

st.write("## Team Builder")

st.divider()

selected_events = st.pills("Events", events, key="events", selection_mode="multi", format_func=lambda x: x,
                           default=["baltimore2025", "dortmund2025", "joinville2025", "louisville2025", "lille2025",
                                    "gdansk2025", "laic2025", "sacramento2025", "perth2025"])

st.divider()

pokemon_data, teams, sorted_pokemon_by_name = get_data(selected_events)

# select a pokemon
current_team = st.multiselect("Select Pokémon", list(pokemon_data.keys()), max_selections=6)

common_team_count = 0
most_common_teammates = {}
common_teams = []
for team_id in teams:
    team = teams.get(team_id)
    team_array = team.get("team")

    team_string_array = []

    for pokemon in team_array:
        team_string_array.append(pokemon["name"])

    # check if all the pokemon in the current team are in the current_team
    if all(pokemon in team_string_array for pokemon in current_team):
        common_team_count += 1
        common_teams.append(team_id)
        for pokemon in team_array:
            if pokemon["name"] not in current_team:
                if pokemon["name"] not in most_common_teammates:
                    most_common_teammates[pokemon["name"]] = 0
                most_common_teammates[pokemon["name"]] += 1

most_common_teammates = dict(sorted(most_common_teammates.items(), key=lambda item: item[1], reverse=True))

expander = False

# display the most common teammates

if len(current_team) == 0:
    expander = st.expander(f"Database contains {common_team_count} teams.", expanded=True)
elif common_team_count == 1:
    expander = st.expander("1 team with the selected Pokémon", expanded=True)
else:
    expander = st.expander(f"{common_team_count} teams paired with the selected Pokémon:", expanded=True)

if expander:
    if len(current_team) != 6:
        common_pairings_dict = {}
        for pokemon, count in most_common_teammates.items():
            percent_string = f"{count / common_team_count * 100:.3f}%"
            common_pairings_dict[pokemon] = {
                "percent": percent_string,
                "usage": count
            }

        expander.dataframe(pd.DataFrame(common_pairings_dict).T)
    else:
        for team_id in common_teams:
            team = teams.get(team_id)
            player_name = team.get("player_name")
            tournament_id = team.get("tournament_id")
            expander.write(f"[{player_name}'s team](https://rk9.gg/teamlist-go/public/{tournament_id}/{team_id})")
