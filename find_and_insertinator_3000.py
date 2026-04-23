import streamlit as st
import pandas as pd
import uuid
import datetime
import re


TABLE_FIELDS = {
    "songs": ["song_id", "original_name", "english_name", "release_date", "duration", "genre", "youtube_link", "progress"],
    "artists": ["artist_id", "original_name", "english_name", "type"],
    "sources": ["source_id", "original_title", "english_title", "type", "release_date", "creator"],
    "song_to_artist": ["song_id", "artist_id", "role", "is_primary"],
    "song_to_source": ["song_id", "source_id", "relation"]
}
SESSION_FIELDS = {
    "songs": ["songs_song_id", "songs_original_name", "songs_english_name", "songs_release_date", "songs_duration", "songs_genre", "songs_youtube_link", "songs_progress"],
    "artists": ["artists_artist_id", "artists_original_name", "artists_english_name", "artists_type"],
    "sources": ["sources_source_id", "sources_original_title", "sources_english_title", "sources_type", "sources_release_date", "sources_creator"],
    "song_to_artist": ["songs_song_id", "artists_artist_id", "s2a_role", "s2a_is_primary"],
    "song_to_source": ["songs_song_id", "sources_source_id", "s2s_relation"]
}
TABLE_PATHS = {
    "songs": "data/Piano Corner - Songs.csv",
    "artists": "data/Piano Corner - Artists.csv",
    "sources": "data/Piano Corner - Sources.csv",
    "song_to_artist": "data/Piano Corner - Song to Artist.csv",
    "song_to_source": "data/Piano Corner - Song to Source.csv"
}


if "init" not in st.session_state:
    st.session_state.init = True
    for table in SESSION_FIELDS:
        for field in table:
            st.session_state[field] = ""
    st.session_state.songs_release_date = datetime.date.today()
    st.session_state.songs_progress = 1
    st.session_state.sources_release_date = datetime.date.today()
    st.session_state.s2a_is_primary = False
    
    
st.markdown("""
    <style>
    html {
        font-size: 0.9rem;
    }

    .block-container {
        padding: 3rem 3rem 3rem 3rem !important;
        max-width: 65% !important;
    }

    .stButton button, .stTextInput input, .stSelectbox div {
        padding: 2px 10px !important;
        min-height: 25px !important;
        line-height: 2 !important;
    }

    [data-testid="stVerticalBlock"] {
        gap: 0.5rem !important;
        padding-top: -5rem !important;
        padding-bottom: 0rem !important;
    }
            
    h1 { font-size: 2.5rem !important; }
    h2 { font-size: 1.8rem !important;
        margin-top: -0.5rem !important;
    }
    h3 { font-size: 1.4rem !important; }
    
    /* Hackiest way to increase toggle size */
    [data-baseweb="checkbox"] [data-testid="stWidgetLabel"] p {
        /* Styles for the label text for checkbox and toggle */
        font-size: 1rem;
        width: 300px;
    }

    [data-baseweb="checkbox"] div {
        /* Styles for the slider container */
        margin-top: 1.5rem;
        height: 1.9rem;
        width: 2.9rem;
    }
    [data-baseweb="checkbox"] div div {
        /* Styles for the slider circle */
        margin-top: 0rem;
        height: 1.6rem;
        width: 1.6rem;
    }
    [data-testid="stCheckbox"] label span {
        /* Styles the checkbox */
        margin-top: 6rem;
        height: 4rem;
        width: 10rem;
    }
    </style>
    """, unsafe_allow_html=True)

    
def table_crud(table, action):
    if action not in ["update", "delete"]:
        st.warning(f"Invalid song action: {action}")
        return False
    
    if table not in TABLE_FIELDS:
        st.warning(f"Invalid table name: {table}")
        return False
    
    table_path = TABLE_PATHS[table]
    t_fields = TABLE_FIELDS[table]
    s_fields = SESSION_FIELDS[table]
    
    df = pd.read_csv(table_path).convert_dtypes()
    if table == "song_to_artist" or table == "song_to_source":
        t_id1, t_id2 = t_fields[0], t_fields[1]
        s_id1, s_id2 = s_fields[0], s_fields[1]
        match = df[(df[t_id1] == st.session_state[s_id1]) & (df[t_id2] == st.session_state[s_id2])]
    else:
        t_id = t_fields[0]
        s_id = s_fields[0]
        match = df[df[t_id] == st.session_state[s_id]]
    print(match)
    
    if action == "update":
        row = {}
        for i in range(len(TABLE_FIELDS[table])):
            t_field = TABLE_FIELDS[table][i]
            s_field = SESSION_FIELDS[table][i]
            row[t_field] = st.session_state[s_field]

        st.session_state.added_new_entry = match.empty
        if match.empty: # Add
            row_df = pd.DataFrame([row])
            df = pd.concat([df, row_df], ignore_index=True)
        else: # Edit
            index = match.index[0]
            
            df.loc[index] = row
            
    elif action == "delete":
        if match.empty:
            st.warning(f"ID Entry doesn't exist for deletion in {table}")
            return False
        
        df = df.drop(match.index)
        
    df.to_csv(table_path, index=False)
    return True

def verify_row_non_blank(table):
    fields = SESSION_FIELDS[table]
    for field in fields:
        entry = st.session_state[field]
        if entry is None or (isinstance(entry, str) and not entry.strip()):
            st.error(f"Cannot have empty field {field}: {entry}")
            return False
    return True

def valid_duration(duration):
    if not re.match(r"^\d+:[0-5]\d$", duration):
        st.error(f"Please enter time in MM:SS format (e.g., 0:45, 12:05) {duration}")
        return False
    return True


# Hoist to top to get around key edit error
if "submit_songs" in st.session_state:
    if st.session_state.songs_song_id == "":
        st.session_state.songs_song_id = str(uuid.uuid4())

    if verify_row_non_blank("songs") and valid_duration(st.session_state.songs_duration):
        if table_crud("songs", "update"):
            change = "Added" if st.session_state.added_new_entry else "Updated"
            st.success(f"{change} {st.session_state.songs_original_name}!")
    del st.session_state.submit_songs

if "submit_artists" in st.session_state:
    if st.session_state.artists_artist_id == "":
        st.session_state.artists_artist_id = str(uuid.uuid4())

    if verify_row_non_blank("artists"):
        if table_crud("artists", "update"):
            change = "Added" if st.session_state.added_new_entry else "Updated"
            st.success(f"{change} {st.session_state.artists_original_name}!")
    del st.session_state.submit_artists
            
if "submit_sources" in st.session_state:
    if st.session_state.sources_source_id == "":
        st.session_state.sources_source_id = str(uuid.uuid4())

    if verify_row_non_blank("sources"):
        if table_crud("sources", "update"):
            change = "Added" if st.session_state.added_new_entry else "Updated"
            st.success(f"{change} {st.session_state.sources_original_title}!")
    del st.session_state.submit_sources    



st.title(":blue[Piano Corner Find and Insertinator 3000]")

# Songs
st.header("Songs")

with st.form("songs_search"):
    c1, c2 = st.columns([4, 1])
    english_name = c1.text_input("Search Song by English Name")
    c2.write(" ")
    submit = c2.form_submit_button("Search Name")
    
    if submit:
        if not english_name.strip():
            st.warning("Please enter a non-blank name.")
        else:   
            df = pd.read_csv(TABLE_PATHS["songs"]).convert_dtypes()
            result = df[df["english_name"].str.contains(english_name, case=False, na=False)]
            if not result.empty:
                match = result.iloc[0]
                for i in range(len(SESSION_FIELDS["songs"])):
                    s_field = SESSION_FIELDS["songs"][i]
                    t_field = TABLE_FIELDS["songs"][i]
                    st.session_state[s_field] = match[t_field]
                    
                st.session_state.songs_release_date = pd.to_datetime(match["release_date"]).date()
                st.session_state.songs_progress = int(match["progress"])
                st.session_state.found_song = True
            else:
                st.warning("No song found with that name.")


with st.expander("Song Fields", expanded=True):
    c1, c2 = st.columns([1, 3])

    clear_song_id = c1.button("Clear Song ID")
    if clear_song_id:
        st.session_state.songs_song_id = ""
        
    delete_song = c2.button("Remove Song ID from table")
    if delete_song:
        if table_crud("songs", "delete"):
            st.success(f"Deleted {st.session_state.songs_song_id}!")
        
    with st.form("songs_add_form", clear_on_submit=False):
        st.text_input("Song ID", key="songs_song_id", disabled=True)
        
        r2c1, r2c2 = st.columns(2)
        r2c1.text_input("Original Name", key="songs_original_name")
        r2c2.text_input("English Name", key="songs_english_name")
        
        r3c1, r3c2, r3c3 = st.columns(3)
        r3c1.date_input("Release Date", key="songs_release_date")
        r3c2.text_input("Duration (MM:SS)", key="songs_duration")
        r3c3.text_input("Genre", key="songs_genre")
        
        r4c1, r4c2 = st.columns(2)
        r4c1.text_input("Youtube Link", key="songs_youtube_link")
        r4c2.number_input("Progress", min_value=1, max_value=5, key="songs_progress")
        
        submit = st.form_submit_button("Add/Update Song")

        if submit:
            st.balloons()
            st.session_state.submit_songs = True
            st.rerun()


# Artists
st.header("Artists")

with st.form("artists_search"):
    c1, c2 = st.columns([4, 1])
    english_name = c1.text_input("Search Artist by English Name")
    c2.write(" ")
    submit = c2.form_submit_button("Search Name")
    
    if submit:
        if not english_name.strip():
            st.warning("Please enter a non-blank name.")
        else:
            df = pd.read_csv(TABLE_PATHS["artists"]).convert_dtypes()
            result = df[df["english_name"].str.contains(english_name, case=False, na=False)]
            if not result.empty:
                match = result.iloc[0]
                for i in range(len(SESSION_FIELDS["artists"])):
                    s_field = SESSION_FIELDS["artists"][i]
                    t_field = TABLE_FIELDS["artists"][i]
                    st.session_state[s_field] = match[t_field] 
                st.session_state.found_artist = True                  
            else:
                st.warning("No artist found with that name.")


with st.expander("Artist Fields", expanded=True):
    c1, c2 = st.columns([1, 3])

    clear_artist_id = c1.button("Clear Artist ID")
    if clear_artist_id:
        st.session_state.artists_artist_id = ""

    delete_artist = c2.button("Remove Artist by ID from table")
    if delete_artist:
        if table_crud("artists", "delete"):
            st.success(f"Deleted {st.session_state.artists_artist_id}!")
        
    with st.form("artists_add_form", clear_on_submit=False):
        st.text_input("Artist ID", key="artists_artist_id", disabled=True)
        
        r2c1, r2c2 = st.columns(2)
        r2c1.text_input("Original Name", key="artists_original_name")
        r2c2.text_input("English Name", key="artists_english_name")
        
        st.text_input("Type", key="artists_type")
        
        submit = st.form_submit_button("Add/Update Artist")

        if submit:
            st.balloons()
            st.session_state.submit_artists = True
            st.rerun()


# Sources
st.header("Sources")

with st.form("sources_search"):
    c1, c2 = st.columns([4, 1])
    english_title = c1.text_input("Search Source by English Title")
    c2.write(" ")
    submit = c2.form_submit_button("Search Title")
    
    if submit:
        if not english_title.strip():
            st.warning("Please enter a non-blank title.")
        else:   
            df = pd.read_csv(TABLE_PATHS["sources"]).convert_dtypes()
            result = df[df["english_title"].str.contains(english_title, case=False, na=False)]
            if not result.empty:
                match = result.iloc[0]
                for i in range(len(SESSION_FIELDS["sources"])):
                    s_field = SESSION_FIELDS["sources"][i]
                    t_field = TABLE_FIELDS["sources"][i]
                    st.session_state[s_field] = match[t_field]
                    
                st.session_state.sources_release_date = pd.to_datetime(match["release_date"]).date()
                st.session_state.found_source = True
            else:
                st.warning("No source found with that title.")


with st.expander("Source Fields", expanded=True):
    c1, c2 = st.columns([1, 3])

    clear_source_id = c1.button("Clear Source ID")
    if clear_source_id:
        st.session_state.sources_source_id = ""
        
    delete_source = c2.button("Remove Source by ID from table")
    if delete_source:
        if table_crud("sources", "delete"):
            st.success(f"Deleted {st.session_state.sources_source_id}!")
        
    with st.form("sources_add_form", clear_on_submit=False):
        st.text_input("Source ID", key="sources_source_id", disabled=True)
        
        r2c1, r2c2 = st.columns(2)
        r2c1.text_input("Original Title", key="sources_original_title")
        r2c2.text_input("English Title", key="sources_english_title")
        
        r3c1, r3c2, r3c3 = st.columns(3)
        r3c1.text_input("Type", key="sources_type")
        r3c2.date_input("Release Date", key="sources_release_date")
        r3c3.text_input("Creator", key="sources_creator")
        
        submit = st.form_submit_button("Add/Update Source")

        if submit:
            st.balloons()
            st.session_state.submit_sources = True
            st.rerun()


if "found_song" in st.session_state or "found_artist" in st.session_state:
    if st.session_state.songs_song_id != "" and st.session_state.artists_artist_id != "":
        df = pd.read_csv(TABLE_PATHS["song_to_artist"]).convert_dtypes()
        result = df[(df["song_id"] == st.session_state.songs_song_id) & (df["artist_id"] == st.session_state.artists_artist_id)]
        if not result.empty:
            match = result.iloc[0]
            st.session_state.s2a_role = match["role"]
            st.session_state.s2a_is_primary = bool(match["is_primary"])
        else:
            st.warning("No entry found with that name.")
    
if "found_song" in st.session_state or "found_source" in st.session_state:
    if st.session_state.songs_song_id != "" and st.session_state.sources_source_id != "":
        df = pd.read_csv(TABLE_PATHS["song_to_source"]).convert_dtypes()
        result = df[(df["song_id"] == st.session_state.songs_song_id) & (df["source_id"] == st.session_state.sources_source_id)]
        if not result.empty:
            match = result.iloc[0]
            st.session_state.s2s_relation = match["relation"]
        else:
            st.warning("No entry found with that name.")
            
if "found_song" in st.session_state:
    del st.session_state.found_song
if "found_artist" in st.session_state:
    del st.session_state.found_artist
if "found_source" in st.session_state:
    del st.session_state.found_source
    

# Song to Artist
st.header("Song to Artist")

delete_source = st.button("Remove entry", key="delete_s2a")
if delete_source:
    table_crud("delete")
    
with st.form("s2a fields", clear_on_submit=False):
    c1, c2 = st.columns(2)
    c1.text_input("Song ID", value=st.session_state.songs_song_id, disabled=True)
    c2.text_input("Artist ID", value=st.session_state.artists_artist_id, disabled=True)
    
    c1, c2 = st.columns([2, 1])
    c1.text_input("Role", key="s2a_role")
    c2.toggle("Is Primary", key="s2a_is_primary")
    
    submit = st.form_submit_button("Add/Update Row")
    if submit:
        if verify_row_non_blank("song_to_artist"):
            if table_crud("song_to_artist", "update"):
                st.success("Updated entry!")
            
            
# Song to Source
st.header("Song to Source")

delete_source = st.button("Remove entry", key="delete_s2s")
if delete_source:
    table_crud("delete")
    
with st.form("s2s fields", clear_on_submit=False):
    c1, c2 = st.columns(2)
    c1.text_input("Song ID", value=st.session_state.songs_song_id, disabled=True)
    c2.text_input("Source ID", value=st.session_state.sources_source_id, disabled=True)
    
    c1, c2 = st.columns([2, 1])
    c1.text_input("Relation", key="s2s_relation")
    
    submit = st.form_submit_button("Add/Update Row")
    if submit:
        if verify_row_non_blank("song_to_source"):
            if table_crud("song_to_source", "update"):
                st.success("Updated entry!")

