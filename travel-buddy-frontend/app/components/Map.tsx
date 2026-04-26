"use client";

import { MapContainer, Marker, Popup, TileLayer, useMap } from "react-leaflet";
import { useEffect, useState } from "react";
import "leaflet/dist/leaflet.css";
import L from "leaflet";

delete (L.Icon.Default.prototype as { _getIconUrl?: unknown })._getIconUrl;

L.Icon.Default.mergeOptions({
  iconRetinaUrl:
    "https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon-2x.png",
  iconUrl: "https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon.png",
  shadowUrl: "https://unpkg.com/leaflet@1.7.1/dist/images/marker-shadow.png",
});

type Props = {
  location: string;
};

const presetCoordinates: Record<string, [number, number]> = {
  goa: [15.2993, 74.124],
  jaipur: [26.9124, 75.7873],
  manali: [32.2396, 77.1887],
  delhi: [28.6139, 77.209],
  mumbai: [19.076, 72.8777],
  kolkata: [22.5726, 88.3639],
  chennai: [13.0827, 80.2707],
  bangalore: [12.9716, 77.5946],
  hyderabad: [17.385, 78.4867],
  pune: [18.5204, 73.8567],
};

function ChangeView({ coords }: { coords: [number, number] }) {
  const map = useMap();

  useEffect(() => {
    map.flyTo(coords, 10, { duration: 1.5 });
  }, [coords, map]);

  return null;
}

export default function Map({ location }: Props) {
  const normalizedLocation = location.trim().toLowerCase();
  const presetCoords = presetCoordinates[normalizedLocation] || presetCoordinates.goa;
  const [coords, setCoords] = useState<[number, number]>(presetCoords);

  useEffect(() => {
    const trimmedLocation = location.trim();

    if (!trimmedLocation) {
      return;
    }

    if (presetCoordinates[trimmedLocation.toLowerCase()]) {
      return;
    }

    const controller = new AbortController();

    fetch(
      `https://nominatim.openstreetmap.org/search?format=json&limit=1&q=${encodeURIComponent(trimmedLocation)}`,
      {
        signal: controller.signal,
        headers: {
          Accept: "application/json",
        },
      }
    )
      .then((res) => res.json())
      .then((data) => {
        if (Array.isArray(data) && data.length > 0) {
          const lat = Number.parseFloat(data[0].lat);
          const lon = Number.parseFloat(data[0].lon);

          if (!Number.isNaN(lat) && !Number.isNaN(lon)) {
            setCoords([lat, lon]);
          }
        }
      })
      .catch(() => undefined);

    return () => controller.abort();
  }, [location]);

  return (
    <MapContainer
      key={location || "default-map"}
      center={coords}
      zoom={10}
      style={{ height: "400px", width: "100%", borderRadius: "12px" }}
    >
      <TileLayer
        attribution="&copy; OpenStreetMap"
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      <Marker position={coords}>
        <Popup>{location || "Goa"}</Popup>
      </Marker>
      <ChangeView coords={coords} />
    </MapContainer>
  );
}
