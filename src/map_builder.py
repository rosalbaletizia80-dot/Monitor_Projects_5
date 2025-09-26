import folium
from folium.plugins import MarkerCluster

def build_map(df, out_path):
    m = folium.Map(location=[20, -20], zoom_start=2, tiles="OpenStreetMap")
    cluster = MarkerCluster(name="Proyectos").add_to(m)
    for _, row in df.iterrows():
        html = (
            "<b>{nombre}</b><br>"
            "<b>Sector:</b> {sector}<br>"
            "<b>Región:</b> {region}<br>"
            "<b>Ubicación:</b> {ubicacion}<br>"
            "<b>Fecha:</b> {published}<br>"
            '<a href="{link}" target="_blank">Fuente</a>'
        ).format(
            nombre=row.get("nombre",""),
            sector=row.get("sector",""),
            region=row.get("region",""),
            ubicacion=row.get("ubicacion",""),
            published=row.get("published",""),
            link=row.get("link","")
        )
        folium.Marker(
            [row["lat"], row["lon"]],
            tooltip=f'{row.get("nombre","")} — {row.get("ubicacion","")}',
            popup=folium.Popup(html, max_width=450)
        ).add_to(cluster)
    folium.LayerControl(collapsed=False).add_to(m)
    m.save(out_path)
