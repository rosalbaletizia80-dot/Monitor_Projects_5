import pandas as pd
import folium
from folium.plugins import MarkerCluster

COLORS = {
    "Reducción de emisiones": "green",
    "Tratamiento / Agua": "blue",
    "Optimización / Eficiencia": "purple",
    "Hidrógeno / Nuevas Energías": "orange",
    "Oil & Gas / Químicos (mejoras)": "red",
    "General": "gray"
}

def _color(cat):
    return COLORS.get(cat, "gray")

def build_map(df, out_path):
    m = folium.Map(location=[20, -20], zoom_start=2, tiles="OpenStreetMap")
    cluster = MarkerCluster(name="Proyectos").add_to(m)
    for _, row in df.iterrows():
        html = (
            "<b>{nombre}</b><br>"
            "<b>Empresa:</b> {empresa}<br>"
            "<b>Sector:</b> {sector}<br>"
            "<b>Estado:</b> {estado}<br>"
            "<b>Ciudad/Ubicación:</b> {ubicacion}<br>"
            "<b>Fecha:</b> {published}<br>"
            "<b>Medio:</b> {medio} | <b>Fuente:</b> {fuente}<br>"
            "<b>Oportunidad:</b> {opp_cat} (score {opp_score})<br>"
            "<b>Tags:</b> {opp_tags}<br>"
            '<a href="{link}" target="_blank">Abrir noticia</a>'
        ).format(
            nombre=row.get("nombre",""),
            empresa=row.get("empresa",""),
            sector=row.get("sector",""),
            estado=row.get("estado",""),
            ubicacion=row.get("ubicacion",""),
            published=row.get("published",""),
            medio=row.get("medio",""),
            fuente=row.get("fuente",""),
            opp_cat=row.get("oportunidad_categoria",""),
            opp_score=row.get("oportunidad_puntaje",0),
            opp_tags=row.get("oportunidad_tags",""),
            link=row.get("link","")
        )
        if pd.notna(row.get("lat")) and pd.notna(row.get("lon")):
            folium.Marker(
                [row["lat"], row["lon"]],
                tooltip=f'{row.get("nombre","")}',
                popup=folium.Popup(html, max_width=560),
                icon=folium.Icon(color=_color(row.get("oportunidad_categoria","General")))
            ).add_to(cluster)
    folium.LayerControl(collapsed=False).add_to(m)
    m.save(out_path)
