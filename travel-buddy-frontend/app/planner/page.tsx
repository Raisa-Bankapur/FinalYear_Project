"use client";

import Image from "next/image";
import Link from "next/link";
import dynamic from "next/dynamic";
import {
  startTransition,
  useEffect,
  useMemo,
  useState,
} from "react";
import AuthGuard from "../components/AuthGuard";

const Map = dynamic(() => import("../components/Map"), {
  ssr: false,
});

type Hotel = {
  name: string;
  price: string;
  rating?: number;
  tag?: string;
};

type FamousPlace = {
  name: string;
  description: string;
  image: string;
  best_time?: string;
  visit_time?: string;
};

type DayPlan = {
  date: string;
  activities: string[];
  hotels: Hotel[];
  restaurants: string[];
  famous_places?: FamousPlace[];
  transport?: string[];
  meal_highlight?: string;
};

type TransportOption = {
  mode: string;
  duration: string;
  price: string;
  note: string;
};

type TransportSegment = {
  from: string;
  to: string;
  options: TransportOption[];
};

type DestinationSegment = {
  destination: string;
  overview: string;
  hero_image?: string;
  quick_facts?: string[];
  days: DayPlan[];
  famous_places?: FamousPlace[];
  transport?: string[];
};

type PlannerResponse = {
  summary: string;
  trip_title: string;
  budget_label: string;
  total_days: number;
  itinerary: string;
  segments: DestinationSegment[];
  transport_segments: TransportSegment[];
};

type SavedTrip = {
  id: string;
  savedAt: string;
  data: PlannerResponse;
};

const STORAGE_KEY = "travelBuddySavedTrips";

const fallbackPlaces = (destination: string): FamousPlace[] => [
  {
    name: `${destination} Main Attraction`,
    description: `A popular place to visit in ${destination}.`,
    image: `https://source.unsplash.com/featured/900x700/?${encodeURIComponent(
      `${destination} landmark`
    )}`,
    best_time: "Morning",
    visit_time: "1-2 hours",
  },
];

function buildFallbackPlan(
  destinations: string[],
  days: number,
  budget: string
): PlannerResponse {
  const safeDestinations = destinations.length ? destinations : ["Goa"];

  const segments = safeDestinations.map((destination) => ({
    destination,
    overview: `${destination} highlights with food, stay, and sightseeing ideas.`,
    hero_image: `https://source.unsplash.com/featured/900x700/?${encodeURIComponent(
      `${destination} travel`
    )}`,
    quick_facts: [
      `${days} day plan`,
      `${budget} budget`,
      "Attractions, hotels, and transport",
    ],
    famous_places: fallbackPlaces(destination),
    transport: [
      `Use local cabs and public transport inside ${destination}.`,
      "Keep one flexible slot for traffic or weather delays.",
    ],
    days: Array.from({ length: days }, (_, index) => ({
      date: `Day ${index + 1}`,
      activities: [
        `Explore famous landmarks in ${destination}`,
        "Keep the evening for food and photography",
      ],
      hotels: [
        {
          name: `${destination} Comfort Stay`,
          price: "Rs. 3,500/night",
          rating: 4.2,
          tag: "Comfort",
        },
      ],
      restaurants: [`${destination} Spice House`, `${destination} Market Cafe`],
      famous_places: fallbackPlaces(destination),
      transport: [`Use app cabs or local buses to cover major spots in ${destination}.`],
      meal_highlight: `${destination} Spice House`,
    })),
  }));

  return {
    summary: `Fallback plan for ${safeDestinations.join(", ")}.`,
    trip_title: `${safeDestinations.join(" - ")} Escape`,
    budget_label: budget,
    total_days: days,
    itinerary: segments
      .flatMap((segment) => [
        segment.destination,
        ...segment.days.map((day) => `${day.date}: ${day.activities[0]}`),
      ])
      .join("\n"),
    segments,
    transport_segments: safeDestinations.slice(0, -1).map((destination, index) => ({
      from: destination,
      to: safeDestinations[index + 1],
      options: [
        {
          mode: "Train",
          duration: "5-10 hrs",
          price: "Rs. 1,200",
          note: "Budget-friendly choice between destinations.",
        },
      ],
    })),
  };
}

function downloadBlob(filename: string, content: string, type: string) {
  const blob = new Blob([content], { type });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  anchor.click();
  URL.revokeObjectURL(url);
}

function formatSavedAt(value: string) {
  return new Date(value).toLocaleString();
}

type PlannerImageProps = {
  src?: string;
  alt: string;
  className: string;
  width: number;
  height: number;
};

function PlannerImage({
  src,
  alt,
  className,
  width,
  height,
}: PlannerImageProps) {
  const [currentSrc, setCurrentSrc] = useState(src || "/travel-placeholder.svg");

  return (
    <Image
      src={currentSrc}
      alt={alt}
      className={className}
      width={width}
      height={height}
      unoptimized
      onError={() => setCurrentSrc("/travel-placeholder.svg")}
    />
  );
}

export default function PlannerPage() {
  const [destinations, setDestinations] = useState<string[]>(["Goa"]);
  const [days, setDays] = useState("3");
  const [budget, setBudget] = useState("medium");
  const [itinerary, setItinerary] = useState<PlannerResponse | null>(null);
  const [savedTrips, setSavedTrips] = useState<SavedTrip[]>([]);
  const [selectedHotel, setSelectedHotel] = useState<Hotel | null>(null);
  const [activeDestination, setActiveDestination] = useState("");
  const [loading, setLoading] = useState(false);
  const [statusMessage, setStatusMessage] = useState("");

  useEffect(() => {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return;

    try {
      const parsed = JSON.parse(raw) as SavedTrip[];
      setSavedTrips(parsed);
    } catch {
      localStorage.removeItem(STORAGE_KEY);
    }
  }, []);

  const cleanDestinations = useMemo(
    () => destinations.map((item) => item.trim()).filter(Boolean),
    [destinations]
  );

  const featuredDestination =
    activeDestination || cleanDestinations[0] || itinerary?.segments[0]?.destination || "Goa";

  const persistSavedTrips = (nextTrips: SavedTrip[]) => {
    setSavedTrips(nextTrips);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(nextTrips));
  };

  const generatePlan = async () => {
    const tripDays = Math.max(Number.parseInt(days, 10) || 3, 1);
    const requestDestinations = cleanDestinations.length ? cleanDestinations : ["Goa"];

    setLoading(true);
    setStatusMessage("");
    setSelectedHotel(null);

    try {
      const response = await fetch("http://127.0.0.1:5000/generate_itinerary", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          destinations: requestDestinations,
          days: tripDays,
          budget,
        }),
      });

      if (!response.ok) {
        throw new Error("Planner service unavailable");
      }

      const data = (await response.json()) as PlannerResponse;
      startTransition(() => {
        setItinerary(data);
        setActiveDestination(data.segments[0]?.destination || requestDestinations[0]);
        setStatusMessage("Full itinerary generated successfully.");
      });
    } catch {
      const fallback = buildFallbackPlan(requestDestinations, tripDays, budget);
      startTransition(() => {
        setItinerary(fallback);
        setActiveDestination(fallback.segments[0]?.destination || requestDestinations[0]);
        setStatusMessage(
          "Backend was unavailable, so a local fallback itinerary is being shown."
        );
      });
    } finally {
      setLoading(false);
    }
  };

  const saveItinerary = () => {
    if (!itinerary) return;

    const newTrip: SavedTrip = {
      id: `${Date.now()}`,
      savedAt: new Date().toISOString(),
      data: itinerary,
    };

    const nextTrips = [newTrip, ...savedTrips].slice(0, 6);
    persistSavedTrips(nextTrips);
    setStatusMessage("Itinerary saved on this device.");
  };

  const loadSavedTrip = (trip: SavedTrip) => {
    setItinerary(trip.data);
    setActiveDestination(trip.data.segments[0]?.destination || "");
    setStatusMessage(`Loaded saved itinerary from ${formatSavedAt(trip.savedAt)}.`);
  };

  const downloadJson = () => {
    if (!itinerary) return;
    const slug = itinerary.trip_title.toLowerCase().replace(/[^a-z0-9]+/g, "-");
    downloadBlob(
      `${slug || "travel-buddy-itinerary"}.json`,
      JSON.stringify(itinerary, null, 2),
      "application/json"
    );
  };

  const downloadText = () => {
    if (!itinerary) return;
    const slug = itinerary.trip_title.toLowerCase().replace(/[^a-z0-9]+/g, "-");
    downloadBlob(
      `${slug || "travel-buddy-itinerary"}.txt`,
      itinerary.itinerary,
      "text/plain;charset=utf-8"
    );
  };

  return (
    <AuthGuard>
      <main className="app-shell planner-shell">
        <section className="planner-header planner-topbar">
          <div>
            <p className="eyebrow">Travel Buddy planner</p>
            <h1 className="section-title">Plan attractions, stays, food, and transport in one place</h1>
          </div>
          <div className="nav-links">
            <Link href="/">Home</Link>
            <Link href="/profile">Profile</Link>
          </div>
        </section>

        <section className="planner-layout planner-dashboard">
          <aside className="form-card planner-sidebar">
            <div className="sidebar-block">
              <h2>Trip details</h2>
              <p className="inline-note">
                Add one or more destinations and generate a richer itinerary like a travel website.
              </p>
            </div>

            <div className="sidebar-block">
              <label className="field-label">Destinations</label>
              {destinations.map((destination, index) => (
                <div key={index} className="destination-input-row">
                  <input
                    className="input-field"
                    placeholder={`Destination ${index + 1}`}
                    value={destination}
                    onChange={(event) => {
                      const next = [...destinations];
                      next[index] = event.target.value;
                      setDestinations(next);
                    }}
                  />
                  {destinations.length > 1 ? (
                    <button
                      type="button"
                      className="secondary-button compact-button"
                      onClick={() =>
                        setDestinations(destinations.filter((_, itemIndex) => itemIndex !== index))
                      }
                    >
                      Remove
                    </button>
                  ) : null}
                </div>
              ))}

              <button
                type="button"
                className="secondary-button wide-button"
                onClick={() => setDestinations([...destinations, ""])}
              >
                Add destination
              </button>
            </div>

            <div className="sidebar-block">
              <label className="field-label" htmlFor="days">
                Total days per destination
              </label>
              <input
                id="days"
                className="input-field"
                type="number"
                min="1"
                value={days}
                onChange={(event) => setDays(event.target.value)}
              />

              <label className="field-label" htmlFor="budget">
                Budget style
              </label>
              <select
                id="budget"
                className="input-field"
                value={budget}
                onChange={(event) => setBudget(event.target.value)}
              >
                <option value="low">Low / Budget</option>
                <option value="medium">Medium / Comfort</option>
                <option value="high">High / Premium</option>
              </select>
            </div>

            <button className="primary-button" onClick={generatePlan} disabled={loading}>
              {loading ? "Generating itinerary..." : "Generate full itinerary"}
            </button>

            {itinerary ? (
              <div className="sidebar-actions">
                <button className="secondary-button" onClick={saveItinerary}>
                  Save itinerary
                </button>
                <button className="secondary-button" onClick={downloadJson}>
                  Download JSON
                </button>
                <button className="secondary-button" onClick={downloadText}>
                  Download text
                </button>
              </div>
            ) : null}

            {statusMessage ? <p className="inline-note">{statusMessage}</p> : null}

            <div className="saved-trips">
              <div className="saved-trips-header">
                <h3>Saved itineraries</h3>
                <span>{savedTrips.length}</span>
              </div>
              {savedTrips.length ? (
                <div className="saved-trip-list">
                  {savedTrips.map((trip) => (
                    <button
                      key={trip.id}
                      className="saved-trip-card"
                      onClick={() => loadSavedTrip(trip)}
                    >
                      <strong>{trip.data.trip_title}</strong>
                      <span>{formatSavedAt(trip.savedAt)}</span>
                    </button>
                  ))}
                </div>
              ) : (
                <p className="inline-note">Saved trips will appear here.</p>
              )}
            </div>
          </aside>

          <section className="results-panel planner-results">
            <div className="planner-hero">
              <div className="planner-hero-copy">
                <p className="eyebrow">Live trip preview</p>
                <h2>{itinerary?.trip_title || "Your complete trip dashboard"}</h2>
                <p>
                  {itinerary?.summary ||
                    "Generate an itinerary to see places to visit, stay options, food picks, transport, and export actions."}
                </p>
                {itinerary ? (
                  <div className="planner-stat-row">
                    <div className="planner-stat-card">
                      <strong>{itinerary.segments.length}</strong>
                      <span>Destinations</span>
                    </div>
                    <div className="planner-stat-card">
                      <strong>{itinerary.total_days}</strong>
                      <span>Days each</span>
                    </div>
                    <div className="planner-stat-card">
                      <strong>{itinerary.budget_label}</strong>
                      <span>Budget</span>
                    </div>
                  </div>
                ) : null}
              </div>

              <div className="map-frame planner-map-frame">
                <Map key={featuredDestination} location={featuredDestination} />
              </div>
            </div>

            {itinerary ? (
              <>
                <div className="destination-tabs">
                  {itinerary.segments.map((segment) => (
                    <button
                      key={segment.destination}
                      className={`destination-tab${
                        featuredDestination === segment.destination ? " active" : ""
                      }`}
                      onClick={() => setActiveDestination(segment.destination)}
                    >
                      {segment.destination}
                    </button>
                  ))}
                </div>

                <div className="results-grid planner-segment-grid">
                  {itinerary.segments.map((segment, segmentIndex) => (
                    <article key={segment.destination} className="day-card planner-segment-card">
                      <div className="segment-cover">
                        <PlannerImage
                          key={segment.hero_image || segment.destination}
                          src={segment.hero_image}
                          alt={segment.destination}
                          className="segment-cover-image"
                          width={1200}
                          height={260}
                        />
                        <div className="segment-cover-overlay">
                          <span className="segment-pill">
                            Stop {segmentIndex + 1}
                          </span>
                          <h3>{segment.destination}</h3>
                          <p>{segment.overview}</p>
                        </div>
                      </div>

                      <div className="segment-facts">
                        {segment.quick_facts?.map((fact) => (
                          <span key={fact} className="fact-chip">
                            {fact}
                          </span>
                        ))}
                      </div>

                      {segment.famous_places?.length ? (
                        <div className="card-section">
                          <h4>Famous places to visit</h4>
                          <div className="places-grid">
                            {segment.famous_places.map((place) => (
                              <div key={place.name} className="place-card">
                                <PlannerImage
                                  key={place.image || place.name}
                                  src={place.image}
                                  alt={place.name}
                                  className="place-image"
                                  width={900}
                                  height={700}
                                />
                                <div className="place-content">
                                  <strong>{place.name}</strong>
                                  <p>{place.description}</p>
                                  <span>
                                    Best time: {place.best_time || "Anytime"} | Visit:{" "}
                                    {place.visit_time || "1-2 hours"}
                                  </span>
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      ) : null}

                      <div className="card-section">
                        <h4>Daily itinerary</h4>
                        <div className="daily-plan-list">
                          {segment.days.map((day) => (
                            <div key={`${segment.destination}-${day.date}`} className="daily-plan-card">
                              <div className="daily-plan-header">
                                <strong>{day.date}</strong>
                                <span>{day.meal_highlight || "Food stop included"}</span>
                              </div>

                              <div className="card-section compact-section">
                                <h4>Activities</h4>
                                <ul className="bullet-list">
                                  {day.activities.map((activity) => (
                                    <li key={`${day.date}-${activity}`}>{activity}</li>
                                  ))}
                                </ul>
                              </div>

                              <div className="info-columns">
                                <div className="mini-card">
                                  <h4>Hotels</h4>
                                  <ul className="bullet-list">
                                    {day.hotels.map((hotel) => (
                                      <li key={`${day.date}-${hotel.name}`}>
                                        <button
                                          className="list-link"
                                          onClick={() => {
                                            setSelectedHotel(hotel);
                                            setActiveDestination(segment.destination);
                                          }}
                                        >
                                          {hotel.name} - {hotel.price}
                                        </button>
                                      </li>
                                    ))}
                                  </ul>
                                </div>

                                <div className="mini-card">
                                  <h4>Restaurants</h4>
                                  <ul className="bullet-list">
                                    {day.restaurants.map((restaurant) => (
                                      <li key={`${day.date}-${restaurant}`}>{restaurant}</li>
                                    ))}
                                  </ul>
                                </div>
                              </div>

                              {day.famous_places?.length ? (
                                <div className="inline-place-strip">
                                  {day.famous_places.map((place) => (
                                    <div key={`${day.date}-${place.name}`} className="inline-place-card">
                                      <PlannerImage
                                        key={place.image || `${day.date}-${place.name}`}
                                        src={place.image}
                                        alt={place.name}
                                        className=""
                                        width={96}
                                        height={96}
                                      />
                                      <div>
                                        <strong>{place.name}</strong>
                                        <p>{place.description}</p>
                                      </div>
                                    </div>
                                  ))}
                                </div>
                              ) : null}

                              {day.transport?.length ? (
                                <div className="transport-tip-box">
                                  <strong>Local transport</strong>
                                  <ul className="bullet-list">
                                    {day.transport.map((tip) => (
                                      <li key={`${day.date}-${tip}`}>{tip}</li>
                                    ))}
                                  </ul>
                                </div>
                              ) : null}
                            </div>
                          ))}
                        </div>
                      </div>

                      {itinerary.transport_segments[segmentIndex] ? (
                        <div className="card-section">
                          <h4>Transport to next destination</h4>
                          <div className="transport-options-grid">
                            {itinerary.transport_segments[segmentIndex].options.map((option) => (
                              <div
                                key={`${segment.destination}-${option.mode}`}
                                className="transport-option-card"
                              >
                                <strong>{option.mode}</strong>
                                <span>{option.duration}</span>
                                <span>{option.price}</span>
                                <p>{option.note}</p>
                              </div>
                            ))}
                          </div>
                        </div>
                      ) : null}
                    </article>
                  ))}
                </div>
              </>
            ) : (
              <div className="empty-state">
                <h2>Your full itinerary will appear here</h2>
                <p>
                  The planner will show famous places, hotel options, restaurants,
                  local transport, inter-city transport, and download actions.
                </p>
              </div>
            )}
          </section>
        </section>

        {selectedHotel ? (
          <aside className="details-drawer planner-drawer">
            <h2>Stay details</h2>
            <p>
              <strong>Hotel:</strong> {selectedHotel.name}
            </p>
            <p>
              <strong>Price:</strong> {selectedHotel.price}
            </p>
            <p>
              <strong>Rating:</strong> {selectedHotel.rating || 4.0} / 5
            </p>
            <p>
              <strong>Category:</strong> {selectedHotel.tag || "Comfort"}
            </p>
            <p>
              <strong>Destination:</strong> {featuredDestination}
            </p>
            <button className="secondary-button" onClick={() => setSelectedHotel(null)}>
              Close
            </button>
          </aside>
        ) : null}
      </main>
    </AuthGuard>
  );
}
