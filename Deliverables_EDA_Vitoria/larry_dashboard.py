import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# Load your dataset with correct path and separator
df = pd.read_csv("../data/KingCounty_joinedTable.csv", sep=";")

# Clean missing values
df['waterfront'] = df['waterfront'].fillna(0)
df['view'] = df['view'].fillna(0)
df['yr_renovated'] = df['yr_renovated'].fillna(0)

# Add flag for recently renovated
df['renovated_recently'] = df['yr_renovated'].apply(lambda x: True if x >= 2000 else False)

# App title with description
st.title("🏡 Larry's Waterfront Property Dashboard")
st.markdown("""
This interactive dashboard helps Larry explore **waterfront homes** in King County that meet his unique preferences.

✅ Adjust filters in the sidebar
✅ View matching homes on the map
✅ Review a detailed table of results
""")

# Sidebar filters
st.sidebar.header("🔧 Filters")

# Budget slider
budget = st.sidebar.slider("💰 Max Budget ($)", min_value=100000, max_value=1000000, value=1000000, step=50000)

# Bedrooms slider
min_bedrooms = st.sidebar.slider("🛏️ Min Bedrooms", min_value=1, max_value=6, value=3)

# Lot size slider
min_lot_size = st.sidebar.slider("📐 Min Lot Size (sqft)", min_value=1000, max_value=100000, value=10000, step=5000)

# Checkbox: Recently Renovated
show_renovated = st.sidebar.checkbox("✨ Only Recently Renovated", value=False)

# Filter dataset
filtered_df = df[
    (df['waterfront'] == 1) &
    (df['price'] <= budget) &
    (df['bedrooms'] >= min_bedrooms) &
    (df['condition'] >= 3) &
    (df['view'] >= 2) &
    (df['grade'] >= 7) &
    (df['sqft_lot'] >= min_lot_size)
]

if show_renovated:
    filtered_df = filtered_df[filtered_df['renovated_recently']]

# Summary panel
st.subheader("📊 Summary of Results")
st.markdown(f"""
- **Total Matches:** {len(filtered_df)}
- **Recently Renovated Homes:** {filtered_df['renovated_recently'].sum()}
- **Average Price:** ${filtered_df['price'].mean():,.0f} (if matches exist)
""")

# Function to color markers by price
def price_color(price):
    if price < 500000:
        return 'green'
    elif price < 800000:
        return 'orange'
    else:
        return 'red'

# Map
st.subheader("🗺️ Map of Filtered Houses")

if not filtered_df.empty:
    map_center = [filtered_df['lat'].mean(), filtered_df['long'].mean()]
    m = folium.Map(location=map_center, zoom_start=10)

    # Add price legend
    legend_html = '''
     <div style="position: fixed; 
                 bottom: 50px; left: 50px; width: 150px; height: 100px; 
                 background-color: white; z-index:9999; font-size:14px;
                 border:2px solid grey; border-radius:8px; padding: 10px;">
     <b>Price Legend</b><br>
     <i style="background:green;color:green">....</i> Under $500K<br>
     <i style="background:orange;color:orange">....</i> $500K - $800K<br>
     <i style="background:red;color:red">....</i> Over $800K
     </div>
     '''
    m.get_root().html.add_child(folium.Element(legend_html))

    for _, row in filtered_df.iterrows():
        popup_info = f"""
        <b>Price:</b> ${row['price']:,.0f}<br>
        <b>Bedrooms:</b> {row['bedrooms']}<br>
        <b>Lot Size:</b> {row['sqft_lot']} sqft<br>
        <b>Condition:</b> {row['condition']}<br>
        <b>View:</b> {row['view']}<br>
        <b>Renovated Recently:</b> {'Yes' if row['renovated_recently'] else 'No'}
        """
        folium.CircleMarker(
            location=[row['lat'], row['long']],
            radius=row['sqft_lot'] / 10000,
            popup=popup_info,
            color=price_color(row['price']),
            fill=True,
            fill_opacity=0.6
        ).add_to(m)

    # Display map
    st_data = st_folium(m, width=700, height=500)
else:
    st.warning("⚠️ No houses match the selected filters.")

# Table of results
st.subheader("📄 Filtered Houses Table")
st.dataframe(filtered_df[['id', 'price', 'bedrooms', 'bathrooms', 'sqft_living', 'sqft_lot', 'zipcode', 'yr_built', 'yr_renovated']].sort_values('price'))
