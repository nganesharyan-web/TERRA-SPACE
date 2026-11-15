import re
from pathlib import Path

import folium
import pandas as pd
import plotly.express as px
import streamlit as st
from streamlit_folium import st_folium

BASE = Path(__file__).resolve().parent
DATA = BASE / "data"

st.set_page_config(
    page_title="TERRA-SPACE | Dhofar",
    page_icon="🛰️",
    layout="wide",
)

# ------------------------------
# Theme and helpers
# ------------------------------
st.markdown(
    """
    <style>
    .main {background:#FFFFFF; color:#172B4D;}
    .block-container {padding-top:1.2rem;}
    div[data-testid="stMetric"] {
        background:#F1F5F9; padding:12px; border-radius:10px;
        border:1px solid #CBD5E1;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

def normalise_column_name(name):
    """Convert a column name to lowercase alphanumeric words."""
    return re.sub(r"[^a-z0-9]+", "_", str(name).strip().lower()).strip("_")


def find_column(df, candidates=(), contains=()):
    """Find a column using exact normalised names, then keyword matching."""
    normalised = {normalise_column_name(col): col for col in df.columns}

    for candidate in candidates:
        key = normalise_column_name(candidate)
        if key in normalised:
            return normalised[key]

    for col in df.columns:
        key = normalise_column_name(col)
        if all(word in key for word in contains):
            return col

    return None


@st.cache_data
def load_data():
    files = {
        "earth": DATA / "earth" / "dhofar_ama18_sem_eds.csv",
        "minerals": DATA / "earth" / "dhofar_mineral_detection_summary.csv",
        "mars_chem": DATA / "mars" / "rocknest_apxs_bulk.csv",
        "mars_minerals": DATA / "mars" / "rocknest_chemin_mineralogy.csv",
        "scores": DATA / "earth" / "dhofar_vs_rocknest_preliminary_scores.csv",
    }
    missing = [str(path.relative_to(BASE)) for path in files.values() if not path.is_file()]
    if missing:
        raise FileNotFoundError("Missing dataset file(s): " + ", ".join(missing))

    return {name: pd.read_csv(path) for name, path in files.items()}


try:
    data = load_data()
    earth = data["earth"]
    minerals = data["minerals"]
    mars_chem = data["mars_chem"]
    mars_minerals = data["mars_minerals"]
    scores = data["scores"]
except Exception as exc:
    st.error(f"Could not load project datasets: {exc}")
    st.info(
        "Check that the data folder is beside final.py and contains the "
        "earth/ and mars/ CSV files in the expected subfolders."
    )
    st.stop()


# ------------------------------
# Banner
# ------------------------------
banner_path = BASE / "banner.png"
if banner_path.is_file():
    st.image(str(banner_path), use_container_width=True)
else:
    st.caption("TERRA-SPACE | Dhofar, Oman")

st.caption(
    "DHOFAR, OMAN • EARTH–MARS ANALOGUE RESEARCH • SOIL COMPOSITION & TERRAIN"
)


# ------------------------------
# Map
# ------------------------------
DHOFAR_CENTRE = (17.1, 54.3)

def terrain_map(lat, lon):
    map_object = folium.Map(
        location=[lat, lon],
        zoom_start=8,
        tiles=None,
        control_scale=True,
    )
    folium.TileLayer(
        tiles=(
            "https://server.arcgisonline.com/ArcGIS/rest/services/"
            "World_Imagery/MapServer/tile/{z}/{y}/{x}"
        ),
        attr="Esri, Maxar, Earthstar Geographics",
        name="Satellite imagery (Esri)",
        overlay=False,
    ).add_to(map_object)
    folium.TileLayer(
        "OpenStreetMap", name="OpenStreetMap", overlay=False
    ).add_to(map_object)
    folium.TileLayer(
        "OpenTopoMap", name="Topographic map", overlay=False
    ).add_to(map_object)

    folium.Marker(
        [lat, lon],
        popup="Dhofar / AMADEE-18 analogue region",
        tooltip="Dhofar study region",
        icon=folium.Icon(color="red", icon="info-sign"),
    ).add_to(map_object)

    folium.Circle(
        [lat, lon],
        radius=25000,
        color="#ffd166",
        fill=True,
        fill_opacity=0.08,
        tooltip="Regional study-area context (illustrative boundary)",
    ).add_to(map_object)

    folium.LayerControl().add_to(map_object)
    return map_object


# ------------------------------
# Sidebar
# ------------------------------
st.sidebar.header("Study configuration")
st.sidebar.write("**Earth analogue:** Dhofar, southern Oman")
lat = st.sidebar.number_input(
    "Map centre latitude", value=DHOFAR_CENTRE[0], format="%.4f"
)
lon = st.sidebar.number_input(
    "Map centre longitude", value=DHOFAR_CENTRE[1], format="%.4f"
)
st.sidebar.caption(
    "The marker identifies the broader Dhofar study region, "
    "not an individual AMADEE-18 sample coordinate."
)

# Identify key columns safely rather than assuming display-style headers.
sample_col = find_column(
    earth,
    candidates=("sample_id", "sample id", "sample"),
    contains=("sample",),
)
if sample_col is None:
    sample_col = earth.columns[0]

score_col = find_column(
    scores,
    candidates=(
        "similarity_score",
        "similarity score (%)",
        "similarity_percent",
        "score",
    ),
    contains=("similarity", "score"),
)
if score_col is None:
    # Fallback: identify a numeric column whose name suggests a score.
    numeric_candidates = [
        col for col in scores.columns
        if pd.api.types.is_numeric_dtype(scores[col])
        and ("score" in normalise_column_name(col)
             or "similar" in normalise_column_name(col))
    ]
    if len(numeric_candidates) == 1:
        score_col = numeric_candidates[0]

score_sample_col = find_column(
    scores,
    candidates=("sample_id", "sample id", "sample"),
    contains=("sample",),
)
if score_sample_col is None and len(scores.columns) > 0:
    score_sample_col = scores.columns[0]


# ------------------------------
# Tabs
# ------------------------------
tabs = st.tabs([
    "Overview",
    "Earth analogue: Dhofar",
    "Mars reference: Rocknest",
    "Earth–Mars comparison",
    "Agricultural assessment",
])

with tabs[0]:
    st.title("TERRA-SPACE research dashboard")
    st.write(
        "Assessing whether terrestrial Mars-analogue environments can be "
        "re-evaluated using measured soil properties to inform future "
        "regolith research."
    )
    c1, c2, c3 = st.columns(3)
    c1.metric("Dhofar samples", len(earth))
    c2.metric("Mars reference", "Rocknest")
    c3.metric("Agricultural score", "Not available")

    st.info(
        "The current comparison is an exploratory major-oxide profile "
        "comparison. It is not a validated mineralogical match or a "
        "crop-growth prediction."
    )
    st.subheader("Interactive Earth terrain map")
    st_folium(
        terrain_map(lat, lon),
        use_container_width=True,
        height=550,
        returned_objects=[],
        key="overview_dhofar_map",
    )
    st.caption(
        "Map layers: Esri satellite imagery, OpenStreetMap and OpenTopoMap."
    )


with tabs[1]:
    st.title("Earth analogue — Dhofar, Oman")
    st.write(
        "The dataset contains AMADEE-18 sample SEM–EDS oxide-equivalent "
        "records. These are semiquantitative prepared-powder measurements, "
        "not high-accuracy whole-rock bulk chemistry."
    )

    st.subheader("Study-region map")
    st_folium(
        terrain_map(lat, lon),
        use_container_width=True,
        height=520,
        returned_objects=[],
        key="dhofar_detail_map",
    )

    st.subheader("Sample chemistry")
    sample_options = earth[sample_col].dropna().astype(str).tolist()
    if sample_options:
        selected_sample = st.selectbox(
            "Select an AMADEE-18 sample", sample_options
        )
        selected_row = earth[
            earth[sample_col].astype(str) == selected_sample
        ].iloc[0]

        chemistry_columns = [
            col for col in earth.columns if col != sample_col
        ]
        chemistry_table = pd.DataFrame({
            "Oxide / measurement": chemistry_columns,
            "Reported value (wt% equivalent)": [
                selected_row[col] for col in chemistry_columns
            ],
        })
        st.write(f"**Selected sample:** {selected_sample}")
        st.dataframe(
            chemistry_table, use_container_width=True, hide_index=True
        )
    else:
        st.warning("No sample IDs were found in the Earth dataset.")

    st.subheader("All sample records")
    st.dataframe(earth, use_container_width=True, hide_index=True)

    st.subheader("Reported regional mineral detections")
    st.dataframe(minerals, use_container_width=True, hide_index=True)
    st.warning(
        "Mineral detections shown here are qualitative sample-suite/regional "
        "detections, not quantitative per-sample mineral abundances."
    )


with tabs[2]:
    st.title("Mars reference — Rocknest, Gale Crater")
    st.write(
        "Rocknest is used as the primary reference for Curiosity APXS bulk "
        "chemistry and CheMin crystalline mineralogy."
    )

    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("APXS bulk chemistry")
        st.dataframe(mars_chem, use_container_width=True, hide_index=True)

        oxide_col = find_column(
            mars_chem, candidates=("oxide",), contains=("oxide",)
        )
        value_col = find_column(
            mars_chem, candidates=("value",), contains=("value",)
        )

        if oxide_col and value_col:
            chart_data = mars_chem.copy()
            chart_data[value_col] = pd.to_numeric(
                chart_data[value_col], errors="coerce"
            )
            chart_data = chart_data.dropna(subset=[value_col])
            if not chart_data.empty:
                fig = px.bar(
                    chart_data,
                    x=oxide_col,
                    y=value_col,
                    title="Rocknest APXS oxide composition",
                    template="plotly_dark",
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning(
                "Could not identify the oxide and value columns for the "
                "APXS chart. The raw data table is still shown."
            )

    with col_b:
        st.subheader("CheMin crystalline mineralogy")
        st.dataframe(
            mars_minerals, use_container_width=True, hide_index=True
        )

        mineral_col = find_column(
            mars_minerals,
            candidates=("mineral",),
            contains=("mineral",),
        )
        abundance_col = find_column(
            mars_minerals,
            candidates=(
                "abundance_wt_pct_crystalline",
                "abundance wt pct crystalline",
            ),
            contains=("abundance",),
        )

        if mineral_col and abundance_col:
            mineral_chart_data = mars_minerals.copy()
            mineral_chart_data[abundance_col] = pd.to_numeric(
                mineral_chart_data[abundance_col], errors="coerce"
            )
            mineral_chart_data = mineral_chart_data.dropna(
                subset=[abundance_col]
            )
            if not mineral_chart_data.empty:
                fig2 = px.bar(
                    mineral_chart_data,
                    x=mineral_col,
                    y=abundance_col,
                    title="Rocknest crystalline phases",
                    template="plotly_dark",
                )
                st.plotly_chart(fig2, use_container_width=True)
        else:
            st.warning(
                "Could not identify the mineral abundance columns. "
                "The raw data table is still shown."
            )

    st.caption(
        "CheMin abundances are percentages of the crystalline component, "
        "not whole-soil weight percentages. Rocknest is distinct from the "
        "Phoenix landing-site soil chemistry dataset."
    )


with tabs[3]:
    st.title("Preliminary Earth–Mars comparison")
    st.write(
        "The score compares the relative proportions of seven shared major "
        "oxides after renormalisation."
    )

    st.subheader("Similarity results")
    if score_col is not None:
        score_display = scores.copy()
        score_display[score_col] = pd.to_numeric(
            score_display[score_col], errors="coerce"
        )
        score_display = score_display.dropna(subset=[score_col])
        score_display = score_display.sort_values(
            score_col, ascending=False
        )
        st.dataframe(
            score_display, use_container_width=True, hide_index=True
        )

        if score_sample_col is not None and not score_display.empty:
            fig3 = px.bar(
                score_display.sort_values(score_col, ascending=True),
                x=score_col,
                y=score_sample_col,
                orientation="h",
                title="Exploratory major-oxide profile similarity",
                template="plotly_dark",
                labels={
                    score_col: "Similarity score",
                    score_sample_col: "Dhofar sample",
                },
            )
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.info(
                "The score table is displayed, but a sample-ID column "
                "could not be identified for the chart."
            )
    else:
        st.warning(
            "The score CSV was loaded, but its similarity-score column "
            "could not be identified automatically. The raw table and "
            "its exact headers are shown below so the data is not lost."
        )
        st.write("Detected CSV headers:", scores.columns.tolist())
        st.dataframe(scores, use_container_width=True, hide_index=True)

    st.warning(
        "This is an exploratory Bray–Curtis-style compositional profile "
        "similarity indicator. Dhofar SEM–EDS and Mars APXS differ in "
        "method and sample scale. Do not interpret it as validated "
        "mineralogical similarity or agricultural suitability."
    )


with tabs[4]:
    st.title("Agricultural compatibility assessment")
    st.write(
        "Earth agricultural-land suitability and Martian substrate "
        "compatibility are separate questions. The current AMADEE-18 "
        "dataset does not contain enough measurements to calculate "
        "either score reliably."
    )

    required = pd.DataFrame(
        [
            ["Soil pH", "Missing", "Acidity / alkalinity"],
            ["Electrical conductivity (EC)", "Missing", "Salinity"],
            ["Organic matter / organic carbon", "Missing", "Soil organic content"],
            ["Nitrogen, phosphorus, potassium", "Missing", "Plant nutrient availability"],
            ["Texture (sand / silt / clay)", "Missing", "Physical soil classification"],
            ["Water retention / infiltration", "Missing", "Water availability to roots"],
            ["Perchlorate and soluble salts", "Missing for Dhofar samples", "Potential toxicity / chemical hazards"],
            ["Bulk density / porosity", "Missing", "Rooting and aeration conditions"],
        ],
        columns=["Measurement", "Data status", "Why it matters"],
    )
    st.dataframe(required, use_container_width=True, hide_index=True)
    st.error(
        "Agricultural suitability: INSUFFICIENT DATA — no score calculated."
    )
    st.info(
        "The existing mineral and oxide measurements can support "
        "preliminary geochemical comparison, but they cannot establish "
        "whether the Dhofar samples are agricultural land or can support "
        "crop growth."
    )

    st.subheader("Add future soil-test measurements")
    default_sample = (
        str(sample_options[0]) if "sample_options" in locals()
        and sample_options else ""
    )

    with st.form("soil_test_form"):
        soil_sample_id = st.text_input("Sample ID", value=default_sample)
        soil_ph = st.number_input(
            "pH", min_value=0.0, max_value=14.0, value=7.0, step=0.1
        )
        soil_ec = st.number_input(
            "Electrical conductivity (dS/m)",
            min_value=0.0,
            value=0.0,
            step=0.1,
        )
        soil_organic = st.number_input(
            "Organic matter (%)",
            min_value=0.0,
            value=0.0,
            step=0.1,
        )
        notes = st.text_area("Notes / laboratory source")
        submitted = st.form_submit_button("Add measurement record")

        if submitted:
            if not soil_sample_id.strip():
                st.error("Please enter a sample ID before saving.")
            else:
                output_path = (
                    DATA / "earth" / "user_soil_test_entries.csv"
                )
                output_path.parent.mkdir(parents=True, exist_ok=True)
                new_record = pd.DataFrame(
                    [[soil_sample_id, soil_ph, soil_ec, soil_organic, notes]],
                    columns=[
                        "sample_id",
                        "pH",
                        "EC_dS_m",
                        "organic_matter_pct",
                        "notes_source",
                    ],
                )
                new_record.to_csv(
                    output_path,
                    mode="a",
                    header=not output_path.exists(),
                    index=False,
                )
                st.success(
                    f"Saved the measurement entry to "
                    f"{output_path.name}. This does not automatically "
                    "create a suitability score."
                )


st.divider()
st.caption(
    "TERRA-SPACE | Research prototype. Data provenance and measurement "
    "limitations must accompany all comparisons."
)
