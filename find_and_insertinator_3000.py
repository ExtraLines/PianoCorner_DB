import streamlit as st
import pandas as pd
import uuid
import datetime
import re


TABLE_FIELDS = {
    "songs": {"song_id": "str", "original_name": "str", "english_name": "str", "release_date": "str", "duration": "str", "genre": "str", "youtube_link": "str", "progress": "int8"},
    "artists": {"artist_id": "str", "original_name": "str", "english_name": "str", "type": "str"},
    "sources": {"source_id": "str", "original_title": "str", "english_title": "str", "type": "str", "release_date": "str", "creator": "str"},
    "song_to_artist": {"song_id": "str", "artist_id": "str", "role": "str", "is_primary": "bool"},
    "song_to_source": {"song_id": "str", "source_id": "str", "relation": "str"}
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
date_fields = ["release_date"]


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


def read_csv(table):
    table_path = TABLE_PATHS[table]
    t_fields = TABLE_FIELDS[table]
    return pd.read_csv(table_path, dtype=t_fields)

def to_csv(table, df):
    table_path = TABLE_PATHS[table]
    df.to_csv(table_path, index=False, date_format="%Y-%m-%d")
    
def search_table(table, t_search, s_key):
    name = st.session_state[s_key]
    if not name.strip():
        st.session_state.warning = "Please enter a non-blank name."
        return
    
    t_fields = TABLE_FIELDS[table]
    s_fields = SESSION_FIELDS[table]
    
    df = read_csv(table)
    result = df[df[t_search].str.contains(name, case=False, na=False)]

    if result.empty:
        st.session_state.warning = f"{name} not found in {table}."
        return
    
    match = result.iloc[0]
    
    for i, t_field in enumerate(t_fields.keys()):
        s_field = s_fields[i]
        val = match[t_field]
        if t_field in date_fields:
            val = datetime.datetime.strptime(val, "%Y-%m-%d").date()
        st.session_state[s_field] = val
    
    st.session_state["found_"+table] = True

def table_crud(table, action):
    if action not in ["update", "delete"]:
        st.session_state.error = f"Invalid table action: {action}"
        return False
    
    if table not in TABLE_FIELDS:
        st.session_state.error = f"Invalid table name: {table}"
        return False
    
    t_fields = TABLE_FIELDS[table]
    t_list = list(t_fields.keys())
    s_fields = SESSION_FIELDS[table]
    
    df = read_csv(table)
        
    if table == "song_to_artist" or table == "song_to_source":
        t_id1, t_id2 = t_list[0], t_list[1]
        s_id1, s_id2 = s_fields[0], s_fields[1]
        match = df[(df[t_id1] == st.session_state[s_id1]) & (df[t_id2] == st.session_state[s_id2])]
    else:
        t_id = t_list[0]
        s_id = s_fields[0]
        match = df[df[t_id] == st.session_state[s_id]]
    
    if action == "update":
        row = {}
        for i, t_field in enumerate(t_fields.keys()):
            s_field = s_fields[i]
            row[t_field] = st.session_state[s_field]
        
        if match.empty: # Add
            row_df = pd.DataFrame([row])
            df = pd.concat([df, row_df], ignore_index=True)
        else: # Update
            index = match.index[0]
            df.loc[index] = row
        change = "Added" if match.empty else "Updated"
            
    elif action == "delete":
        if match.empty:
            st.session_state.error = f"ID Entry doesn't exist for deletion in {table}"
            return False
        change = "Deleted"
        df = df.drop(match.index)
        
    st.session_state.success = f"{change} entry in {table}!"
    to_csv(table, df)
    return True

def verify_row_non_blank(table):
    fields = SESSION_FIELDS[table]
    for field in fields:
        entry = st.session_state[field]
        if entry is None or (isinstance(entry, str) and not entry.strip()):
            st.session_state.error = f"Cannot have empty field for {field}"
            return False
    return True

def valid_duration(duration):
    return re.match(r"^\d+:[0-5]\d$", duration)
        
def submit_row(table):
    if table not in TABLE_FIELDS:
        st.session_state.warning = f"Invalid table name: {table}"
        return

    s_fields = SESSION_FIELDS[table]
    id_field = s_fields[0]
    if st.session_state[id_field] == "":
        st.session_state[id_field] = str(uuid.uuid4())
        
    if not verify_row_non_blank(table):
        return
    if "songs_duration" in s_fields and not valid_duration(st.session_state.songs_duration):
        st.session_state.error(f"Please enter time in MM:SS format (e.g., 0:45, 12:05) {st.session_state.songs_duration}.")
        return
    table_crud(table, "update")
        
def submit_join(table):
    if table not in TABLE_FIELDS:
        st.session_state.warning = f"Invalid table name: {table}"
        return
    if not verify_row_non_blank(table):
        return
    table_crud(table, "update")
    
def post_message():
    if "success" in st.session_state:
        st.success(st.session_state.success)
        del st.session_state.success
    if "warning" in st.session_state:
        st.warning(st.session_state.warning)
        del st.session_state.warning
    if "error" in st.session_state:
        st.error(st.session_state.error)
        del st.session_state.error



st.title(":blue[Piano Corner Find and Insertinator 3000]")

# Songs
st.header("Songs")

with st.form("songs_search"):
    c1, c2 = st.columns([4, 1])
    english_name = c1.text_input("Search Song by English Name", key="songs_search_name")
    c2.write(" ")
    submit = c2.form_submit_button("Search Name", on_click=search_table, args=("songs", "english_name", "songs_search_name"))
    if submit:
        post_message()
    

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
        
        submit = st.form_submit_button("Add/Update Song", on_click=submit_row, args=("songs",))
        if submit:
            post_message()


# Artists
st.header("Artists")

with st.form("artists_search"):
    c1, c2 = st.columns([4, 1])
    english_name = c1.text_input("Search Artist by English Name", key="artists_search_name")
    c2.write(" ")
    submit = c2.form_submit_button("Search Name", on_click=search_table, args=("artists", "english_name", "artists_search_name"))
    if submit:
        post_message()


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
        
        submit = st.form_submit_button("Add/Update Artist", on_click=submit_row, args=("artists",))
        if submit:
            post_message()


# Sources
st.header("Sources")

with st.form("sources_search"):
    c1, c2 = st.columns([4, 1])
    english_title = c1.text_input("Search Source by English Title", key="sources_search_title")
    c2.write(" ")
    submit = c2.form_submit_button("Search Title", on_click=search_table, args=("sources", "english_title", "sources_search_title"))
    if submit:
        post_message()


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
        
        submit = st.form_submit_button("Add/Update Source", on_click=submit_row, args=("sources",))
        if submit:
            post_message()


if "found_songs" in st.session_state or "found_artists" in st.session_state:
    if st.session_state.songs_song_id != "" and st.session_state.artists_artist_id != "":
        df = pd.read_csv(TABLE_PATHS["song_to_artist"])
        result = df[(df["song_id"] == st.session_state.songs_song_id) & (df["artist_id"] == st.session_state.artists_artist_id)]
        if not result.empty:
            match = result.iloc[0]
            st.session_state.s2a_role = match["role"]
            st.session_state.s2a_is_primary = bool(match["is_primary"])
    
if "found_songs" in st.session_state or "found_sources" in st.session_state:
    if st.session_state.songs_song_id != "" and st.session_state.sources_source_id != "":
        df = pd.read_csv(TABLE_PATHS["song_to_source"])
        result = df[(df["song_id"] == st.session_state.songs_song_id) & (df["source_id"] == st.session_state.sources_source_id)]
        if not result.empty:
            match = result.iloc[0]
            st.session_state.s2s_relation = match["relation"]
            
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
    
    submit = st.form_submit_button("Add/Update Row", on_click=submit_join, args=("song_to_artist",))
    if submit:
        post_message()
            
            
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
    
    submit = st.form_submit_button("Add/Update Row", on_click=submit_join, args=("song_to_source",))
    if submit:
        post_message()

