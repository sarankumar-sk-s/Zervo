import React, { useState, useEffect, useRef } from 'react';

/**
 * LocationPicker Component
 * Interactive Leaflet + MapTiler Map Location Selector for Food Donations
 * 
 * Props:
 * - initialAddress: string (optional)
 * - initialLat: number (optional)
 * - initialLng: number (optional)
 * - onLocationChange: function({ address, latitude, longitude, isConfirmed })
 * - maptilerKey: string (optional, falls back to env or window)
 */
export const LocationPicker = ({
  initialAddress = '',
  initialLat = 11.0168,
  initialLng = 76.9558,
  onLocationChange,
  maptilerKey = ''
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const [searchError, setSearchError] = useState('');
  const [selectedLocation, setSelectedLocation] = useState({
    address: initialAddress,
    latitude: initialLat,
    longitude: initialLng
  });
  const [isConfirmed, setIsConfirmed] = useState(false);
  const [manualMode, setManualMode] = useState(false);

  const mapContainerRef = useRef(null);
  const mapInstanceRef = useRef(null);
  const markerRef = useRef(null);
  const searchTimeoutRef = useRef(null);

  // Determine MapTiler API Key
  const apiKey = maptilerKey || 
    (typeof window !== 'undefined' && (window.VITE_MAPTILER_API_KEY || window.MAPTILER_API_KEY)) ||
    '';

  // ── 1. Initialize Leaflet Map ─────────────────────────────────────────────
  useEffect(() => {
    if (manualMode || !mapContainerRef.current) return;
    if (typeof window === 'undefined' || !window.L) return;

    const L = window.L;

    // Ensure Leaflet default marker icons resolve correctly
    delete L.Icon.Default.prototype._getIconUrl;
    L.Icon.Default.mergeOptions({
      iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
      iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
      shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png'
    });

    const startLat = selectedLocation.latitude || 11.0168;
    const startLng = selectedLocation.longitude || 76.9558;

    if (!mapInstanceRef.current) {
      const map = L.map(mapContainerRef.current, {
        center: [startLat, startLng],
        zoom: 14,
        zoomControl: true,
        scrollWheelZoom: 'center'
      });

      // MapTiler Raster Tile Layer (with OpenStreetMap fallback if key unconfigured/invalid)
      const tileUrl = (apiKey && apiKey !== 'YOUR_MAPTILER_API_KEY')
        ? `https://api.maptiler.com/maps/streets-v2/{z}/{x}/{y}.png?key=${apiKey}`
        : 'https://tile.openstreetmap.org/{z}/{x}/{y}.png';

      const attribution = (apiKey && apiKey !== 'YOUR_MAPTILER_API_KEY')
        ? '&copy; <a href="https://www.maptiler.com/">MapTiler</a> &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        : '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>';

      L.tileLayer(tileUrl, {
        attribution,
        maxZoom: 19,
        tileSize: 512,
        zoomOffset: (apiKey && apiKey !== 'YOUR_MAPTILER_API_KEY') ? -1 : 0
      }).addTo(map);

      // Add Draggable Marker
      const marker = L.marker([startLat, startLng], {
        draggable: true,
        autoPan: true
      }).addTo(map);

      marker.on('dragend', () => {
        const pos = marker.getLatLng();
        handleCoordinatesSelected(pos.lat, pos.lng, true);
      });

      // Map click moves marker
      map.on('click', (e) => {
        marker.setLatLng(e.latlng);
        handleCoordinatesSelected(e.latlng.lat, e.latlng.lng, true);
      });

      mapInstanceRef.current = map;
      markerRef.current = marker;

      // Invalidate size after layout renders
      setTimeout(() => {
        if (mapInstanceRef.current) mapInstanceRef.current.invalidateSize();
      }, 300);
    }

    return () => {
      // Optional cleanup on unmount
    };
  }, [manualMode]);

  // ── 2. Reverse Geocoding via MapTiler ──────────────────────────────────────
  const reverseGeocode = async (lat, lng) => {
    try {
      if (apiKey && apiKey !== 'YOUR_MAPTILER_API_KEY') {
        const url = `https://api.maptiler.com/geocoding/${lng},${lat}.json?key=${apiKey}`;
        const res = await fetch(url);
        if (res.ok) {
          const data = await res.json();
          if (data.features && data.features.length > 0) {
            return data.features[0].place_name || data.features[0].text;
          }
        }
      }

      // Safe fallback: OpenStreetMap Nominatim
      const nomUrl = `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}`;
      const nomRes = await fetch(nomUrl, {
        headers: { 'Accept-Language': 'en' }
      });
      if (nomRes.ok) {
        const nomData = await nomRes.json();
        return nomData.display_name || `${lat.toFixed(5)}, ${lng.toFixed(5)}`;
      }
    } catch (err) {
      console.warn('Reverse geocoding error:', err);
    }
    return `Location (${lat.toFixed(5)}, ${lng.toFixed(5)})`;
  };

  // ── 3. Handle Coordinate Selection ─────────────────────────────────────────
  const handleCoordinatesSelected = async (lat, lng, doReverse = false, customAddress = '') => {
    setIsConfirmed(false);
    let addr = customAddress;
    if (doReverse && !customAddress) {
      addr = await reverseGeocode(lat, lng);
    }

    const updated = {
      address: addr || selectedLocation.address,
      latitude: parseFloat(lat.toFixed(6)),
      longitude: parseFloat(lng.toFixed(6))
    };

    setSelectedLocation(updated);

    if (markerRef.current) {
      markerRef.current.setLatLng([lat, lng]);
    }

    if (onLocationChange) {
      onLocationChange({ ...updated, isConfirmed: false });
    }
  };

  // ── 4. Location Search (MapTiler Geocoding API) ─────────────────────────────
  const searchLocation = async (query) => {
    if (!query || query.trim().length < 2) {
      setSearchResults([]);
      setSearchError('');
      return;
    }

    setIsSearching(true);
    setSearchError('');

    try {
      let results = [];
      if (apiKey && apiKey !== 'YOUR_MAPTILER_API_KEY') {
        const url = `https://api.maptiler.com/geocoding/${encodeURIComponent(query)}.json?key=${apiKey}&limit=5`;
        const res = await fetch(url);
        if (res.ok) {
          const data = await res.json();
          results = (data.features || []).map(f => ({
            name: f.text,
            formatted: f.place_name,
            lng: f.geometry.coordinates[0],
            lat: f.geometry.coordinates[1]
          }));
        } else {
          throw new Error('MapTiler geocode failed');
        }
      } else {
        // Fallback geocoding: Nominatim
        const nomUrl = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}&limit=5`;
        const res = await fetch(nomUrl, { headers: { 'Accept-Language': 'en' } });
        if (res.ok) {
          const data = await res.json();
          results = data.map(item => ({
            name: item.name || item.display_name.split(',')[0],
            formatted: item.display_name,
            lat: parseFloat(item.lat),
            lng: parseFloat(item.lon)
          }));
        }
      }

      if (results.length === 0) {
        setSearchError('No locations found.');
      }
      setSearchResults(results);
    } catch (err) {
      console.warn('Geocoding search failed:', err);
      setSearchError('Unable to search location. Please try again.');
      setSearchResults([]);
    } finally {
      setIsSearching(false);
    }
  };

  const handleSearchInputChange = (e) => {
    const val = e.target.value;
    setSearchQuery(val);
    if (searchTimeoutRef.current) clearTimeout(searchTimeoutRef.current);
    searchTimeoutRef.current = setTimeout(() => {
      searchLocation(val);
    }, 350);
  };

  // ── 5. Select Search Result ────────────────────────────────────────────────
  const handleSelectSearchResult = (item) => {
    setSearchQuery(item.formatted);
    setSearchResults([]);
    setSearchError('');

    handleCoordinatesSelected(item.lat, item.lng, false, item.formatted);

    if (mapInstanceRef.current) {
      mapInstanceRef.current.flyTo([item.lat, item.lng], 16, { animate: true, duration: 1.2 });
    }
  };

  // ── 6. Confirm Location ────────────────────────────────────────────────────
  const handleConfirmLocation = () => {
    if (!selectedLocation.address) {
      alert('Please select or search a location first.');
      return;
    }
    setIsConfirmed(true);
    if (onLocationChange) {
      onLocationChange({
        ...selectedLocation,
        isConfirmed: true
      });
    }
  };

  return (
    <div className="location-picker-wrapper space-y-4">
      {/* Search Box Header */}
      <div className="relative">
        <div className="relative flex items-center">
          <input
            type="text"
            value={searchQuery}
            onChange={handleSearchInputChange}
            placeholder="🔍 Search location, college, restaurant, street, area..."
            className="w-full px-5 py-3.5 pr-10 rounded-xl bg-surface-container-highest border border-outline-variant/30 focus:ring-2 focus:ring-primary focus:bg-surface-container-lowest manrope text-on-surface text-sm transition-all"
          />
          {isSearching && (
            <span className="material-symbols-outlined absolute right-3 animate-spin text-primary text-xl pointer-events-none">
              progress_activity
            </span>
          )}
        </div>

        {/* Autocomplete Dropdown */}
        {searchResults.length > 0 && (
          <div className="absolute top-full left-0 right-0 mt-1 bg-surface-container-lowest rounded-xl shadow-2xl border border-outline-variant/20 z-50 max-h-60 overflow-y-auto">
            {searchResults.map((item, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => handleSelectSearchResult(item)}
                className="w-full text-left px-4 py-3 hover:bg-primary-container/10 border-b border-outline-variant/10 flex items-start gap-2.5 transition-colors cursor-pointer"
              >
                <span className="material-symbols-outlined text-primary text-lg mt-0.5">location_on</span>
                <div>
                  <div className="text-sm font-bold plusJakartaSans text-on-surface">{item.name}</div>
                  <div className="text-xs manrope text-on-surface-variant truncate max-w-md">{item.formatted}</div>
                </div>
              </button>
            ))}
          </div>
        )}

        {/* Search Error Notice */}
        {searchError && (
          <p className="text-xs text-error mt-1.5 font-medium manrope px-1">{searchError}</p>
        )}
      </div>

      {/* Map Container */}
      {!manualMode ? (
        <div className="relative rounded-2xl overflow-hidden border border-outline-variant/30 shadow-md">
          <div
            ref={mapContainerRef}
            id="leaflet-map-canvas"
            style={{ height: '340px', width: '100%', zIndex: 1 }}
            className="w-full"
          />
          <div className="absolute bottom-2 left-2 z-10 bg-surface/90 backdrop-blur-md px-3 py-1.5 rounded-lg border border-outline-variant/20 text-[11px] font-medium text-on-surface shadow-sm">
            💡 Drag marker or click map to adjust location
          </div>
        </div>
      ) : (
        /* Manual Address Fallback */
        <div className="p-4 rounded-xl bg-surface-container-highest border border-outline-variant/20 space-y-2">
          <label className="text-xs font-bold manrope text-on-surface-variant">Manual Address Input:</label>
          <textarea
            rows="2"
            value={selectedLocation.address}
            onChange={(e) => {
              const addr = e.target.value;
              setSelectedLocation(prev => ({ ...prev, address: addr }));
              if (onLocationChange) onLocationChange({ address: addr, latitude: null, longitude: null, isConfirmed: false });
            }}
            placeholder="Enter full pickup street address manually..."
            className="w-full p-3 rounded-lg bg-surface-container-lowest border border-outline-variant/30 text-sm manrope text-on-surface focus:ring-2 focus:ring-primary"
          />
        </div>
      )}

      {/* Selected Location Card & Actions */}
      <div className="p-4 rounded-xl bg-surface-container-highest/60 border border-outline-variant/20 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="space-y-1">
          <div className="flex items-center gap-1.5 text-xs font-bold uppercase tracking-wider text-primary">
            <span className="material-symbols-outlined text-sm">pin_drop</span> Selected Location:
          </div>
          <p className="text-sm font-semibold plusJakartaSans text-on-surface leading-snug">
            {selectedLocation.address || 'No location selected yet. Search above or click the map.'}
          </p>
          {selectedLocation.latitude && selectedLocation.longitude ? (
            <div className="flex items-center gap-3 text-xs text-on-surface-variant font-mono">
              <span>Lat: <strong className="text-on-surface">{selectedLocation.latitude.toFixed(5)}</strong></span>
              <span>Lng: <strong className="text-on-surface">{selectedLocation.longitude.toFixed(5)}</strong></span>
            </div>
          ) : null}
        </div>

        <div className="flex items-center gap-2 flex-shrink-0">
          {/* Toggle Manual Mode Fallback */}
          <button
            type="button"
            onClick={() => setManualMode(!manualMode)}
            className="px-3.5 py-2 text-xs font-bold rounded-lg border border-outline-variant/40 hover:bg-surface-variant/40 transition-colors text-on-surface-variant"
          >
            {manualMode ? '🗺️ Use Map' : '✏️ Manual'}
          </button>

          {/* Confirm Location Button */}
          <button
            type="button"
            onClick={handleConfirmLocation}
            className={`px-5 py-2.5 rounded-full font-bold text-sm plusJakartaSans flex items-center gap-1.5 transition-all duration-200 cursor-pointer shadow-sm ${
              isConfirmed 
                ? 'bg-emerald-600 text-white shadow-emerald-600/20' 
                : 'bg-primary text-on-primary hover:bg-emerald-800'
            }`}
          >
            <span className="material-symbols-outlined text-base">
              {isConfirmed ? 'verified' : 'check'}
            </span>
            <span>{isConfirmed ? '✓ Location Confirmed' : '✓ Confirm Location'}</span>
          </button>
        </div>
      </div>

      {/* Confirmation Banner */}
      {isConfirmed && (
        <div className="p-3 rounded-xl bg-emerald-500/15 border border-primary/30 text-emerald-900 dark:text-emerald-100 flex items-center gap-2 text-xs font-bold manrope animate-fadeIn">
          <span className="material-symbols-outlined text-primary text-base">check_circle</span>
          <span>✓ Location confirmed! Coordinates ({selectedLocation.latitude}, {selectedLocation.longitude}) will be saved for smart matching.</span>
        </div>
      )}
    </div>
  );
};

export default LocationPicker;
