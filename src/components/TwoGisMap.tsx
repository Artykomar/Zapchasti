"use client";

import { ExternalLink, MapPin } from "lucide-react";
import { useEffect, useRef, useState } from "react";

type Coordinates = [number, number];

type MapGlMap = {
  destroy: () => void;
};

type MapGlMarker = {
  destroy?: () => void;
};

type MapGlApi = {
  Map: new (
    container: HTMLElement,
    options: {
      center: Coordinates;
      key: string;
      zoom: number;
    }
  ) => MapGlMap;
  Marker: new (
    map: MapGlMap,
    options: {
      coordinates: Coordinates;
      label?: {
        offset: [number, number];
        relativeAnchor: [number, number];
        text: string;
      };
    }
  ) => MapGlMarker;
};

declare global {
  interface Window {
    __zemazapTwoGisMapGl?: Promise<MapGlApi>;
    mapgl?: MapGlApi;
  }
}

type TwoGisMapProps = {
  address: string;
  apiKey: string;
  center: Coordinates;
  mapUrl: string;
  zoom: number;
};

const loadMapGl = () => {
  if (window.mapgl) {
    return Promise.resolve(window.mapgl);
  }

  if (!window.__zemazapTwoGisMapGl) {
    window.__zemazapTwoGisMapGl = new Promise<MapGlApi>((resolve, reject) => {
      const script = document.createElement("script");
      script.async = true;
      script.dataset.twoGisMapgl = "true";
      script.src = "https://mapgl.2gis.com/api/js/v1";
      script.onload = () => {
        if (window.mapgl) {
          resolve(window.mapgl);
          return;
        }
        reject(new Error("2GIS MapGL script loaded without mapgl API."));
      };
      script.onerror = () => reject(new Error("2GIS MapGL script failed to load."));
      document.head.appendChild(script);
    });
  }

  return window.__zemazapTwoGisMapGl;
};

export default function TwoGisMap({ address, apiKey, center, mapUrl, zoom }: TwoGisMapProps) {
  const mapNodeRef = useRef<HTMLDivElement>(null);
  const [status, setStatus] = useState<"fallback" | "loading" | "ready">("fallback");

  useEffect(() => {
    if (!apiKey || !mapNodeRef.current) {
      setStatus("fallback");
      return;
    }

    let cancelled = false;
    let map: MapGlMap | undefined;
    let marker: MapGlMarker | undefined;

    setStatus("loading");

    loadMapGl()
      .then((mapgl) => {
        if (cancelled || !mapNodeRef.current) {
          return;
        }
        map = new mapgl.Map(mapNodeRef.current, {
          center,
          key: apiKey,
          zoom
        });
        marker = new mapgl.Marker(map, {
          coordinates: center,
          label: {
            offset: [0, 24],
            relativeAnchor: [0.5, 0],
            text: address
          }
        });
        setStatus("ready");
      })
      .catch(() => {
        if (!cancelled) {
          setStatus("fallback");
        }
      });

    return () => {
      cancelled = true;
      marker?.destroy?.();
      map?.destroy();
    };
  }, [address, apiKey, center, zoom]);

  return (
    <section className="two-gis-map" aria-label={`2ГИС карта: ${address}`}>
      <div className="two-gis-map__viewport" ref={mapNodeRef}>
        {status !== "ready" ? (
          <div className="two-gis-map__fallback">
            <MapPin size={34} aria-hidden="true" />
            <strong>{address}</strong>
            <span>Временная точка выдачи в Москве</span>
          </div>
        ) : null}
      </div>
      <div className="two-gis-map__bar">
        <div>
          <strong>2ГИС</strong>
          <span>{address}</span>
        </div>
        <a href={mapUrl} target="_blank" rel="noreferrer">
          Открыть в 2ГИС
          <ExternalLink size={16} aria-hidden="true" />
        </a>
      </div>
    </section>
  );
}
