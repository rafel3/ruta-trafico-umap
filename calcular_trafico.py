import json, os, requests

API_KEY = os.environ["TOMTOM_KEY"]  # la clave va en una variable de entorno
tramos = [
    {"name": "Tramo 1", "origen": (4.6097, -74.0817), "destino": (4.7110, -74.0721)},
]

features = []
for t in tramos:
    (o_lat, o_lon), (d_lat, d_lon) = t["origen"], t["destino"]
    url = (f"https://api.tomtom.com/routing/1/calculateRoute/"
           f"{o_lat},{o_lon}:{d_lat},{d_lon}/json")
    r = requests.get(url, params={"key": API_KEY, "traffic": "true",
                                  "travelMode": "car"}, timeout=15)
    r.raise_for_status()
    resumen = r.json()["routes"][0]["summary"]
    features.append({
        "type": "Feature",
        "properties": {
            "name": t["name"],
            "distancia_km": round(resumen["lengthInMeters"] / 1000, 2),
            "tiempo_min": round(resumen["travelTimeInSeconds"] / 60, 1),
            "retraso_trafico_min": round(resumen.get("trafficDelayInSeconds", 0) / 60, 1),
            "actualizado": __import__("datetime").datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
        },
        "geometry": {"type": "LineString",
                     "coordinates": [[o_lon, o_lat], [d_lon, d_lat]]},
    })

with open("ruta_trafico.geojson", "w", encoding="utf-8") as f:
    json.dump({"type": "FeatureCollection", "features": features}, f,
              ensure_ascii=False, indent=2)