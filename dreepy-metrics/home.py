import pandas as pd
import streamlit as st
from data import get_data, get_events

events = get_events()

st.write("## Pokémon Usage")

st.divider()

selected_events = st.pills("Select events", events, key="events", selection_mode="multi", format_func=lambda x: x,
                           default=["baltimore2025", "dortmund2025", "joinville2025", "louisville2025", "lille2025",
                                    "gdansk2025", "laic2025"])

st.divider()

sidebar, details = st.columns([25, 75], gap="large")

with sidebar:
    pokemon_data, teams, sorted_pokemon_by_name = get_data(selected_events)

    with st.container(height=450, border=True):
        sorted_pokemon_by_total = sorted(pokemon_data.items(), key=lambda x: x[1]["total_pokemon"], reverse=True)
        total_teams = len(teams)

        label_array = []
        captions_array = []
        for pokemon_name, data in sorted_pokemon_by_total:
            percent_string = f"{data['total_pokemon'] / total_teams * 100:.3f}%"
            label_array.append(pokemon_name)
            captions_array.append(percent_string)

        selected_pokemon = st.radio("Pokemon", label_array, captions=captions_array, index=None)

with details:
    if selected_pokemon:
        selected_data = pokemon_data[selected_pokemon]
        current_pokemon_count = selected_data["total_pokemon"]

        # sort fast move counts
        fast_move_raw_data = sorted(selected_data["fast_move_counts"].items(), key=lambda x: x[1], reverse=True)

        fast_move_data = {}
        fast_move_labels = []
        for fast_move, count in fast_move_raw_data:
            percent_string = f"{count / selected_data['total_pokemon'] * 100:.3f}%"
            fast_move_data[fast_move] = {
                "percent": percent_string,
                "usage": count
            }
            fast_move_labels.append(fast_move)

        charge_move_raw_data = sorted(selected_data["charge_move_individual_counts"].items(), key=lambda x: x[1],
                                      reverse=True)

        charge_move_data = {}
        charge_move_labels = []
        for charge_move, count in charge_move_raw_data:
            percent_string = f"{count / selected_data['total_pokemon'] * 100:.3f}%"
            charge_move_data[charge_move] = {
                "percent": percent_string,
                "usage": count
            }
            charge_move_labels.append(charge_move)

        charge_move_pairing_raw_data = sorted(selected_data["charge_move_combined_counts"].items(), key=lambda x: x[1],
                                              reverse=True)

        charge_move_pairing_data = {}
        charge_move_pairing_labels = []
        for charge_move_pairing, count in charge_move_pairing_raw_data:
            percent_string = f"{count / selected_data['total_pokemon'] * 100:.3f}%"
            charge_move_pairing_data[charge_move_pairing] = {
                "percent": percent_string,
                "usage": count
            }
            charge_move_pairing_labels.append(charge_move_pairing)

        common_pairings = {}
        # find most common pokemon paired with selected_pokemon
        complete_pokemon_data = sorted_pokemon_by_name[selected_pokemon]
        for pokemon in complete_pokemon_data:
            team_id = pokemon["team_id"]
            team = teams[pokemon["team_id"]]
            for member in team["team"]:
                if member["name"] == selected_pokemon:
                    continue

                if member["name"] not in common_pairings:
                    common_pairings[member["name"]] = 0

                common_pairings[member["name"]] += 1

        common_pairings_sorted = sorted(common_pairings.items(), key=lambda x: x[1], reverse=True)

        LIMIT = 12
        counter = 0


        common_pairings_dict = {}
        for pokemon, count in common_pairings_sorted:
            if counter >= LIMIT:
                break
            counter += 1

            percent_string = f"{count / selected_data['total_pokemon'] * 100:.3f}%"
            common_pairings_dict[pokemon] = {
                "percent": percent_string,
                "usage": count
            }


        st.write(f"## {selected_pokemon}")
        left, center, right = st.columns(3, gap="large")
        with left:
            with st.container(border=True):
                total_usage = selected_data["total_pokemon"]
                st.metric("Total Usage", total_usage)

                percent = selected_data["shadow_pokemon"] / current_pokemon_count * 100
                if percent != 0:
                    percent_string = f"{percent:.3f}%"
                    st.metric("Shadow Percent", percent_string)

        with center:
            st.write("Fast Moves")
            st.table(pd.DataFrame(fast_move_data, index=["percent", "usage"]).T)

        with right:
            st.write("Charge Moves")
            st.table(pd.DataFrame(charge_move_data, index=["percent", "usage"]).T)

        lower_left, lower_right = st.columns(2, gap="large")
        with lower_left:
            st.write("Charge Move Pairs")
            st.table(pd.DataFrame(charge_move_pairing_data, index=["percent", "usage"]).T)

        with lower_right:
            st.write("Teammates")
            st.table(pd.DataFrame(common_pairings_dict).T)
