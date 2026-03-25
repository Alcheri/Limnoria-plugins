```mermaid
flowchart LR
    %% =========================
    %% Weather Plugin Flow (source-aligned)
    %% =========================

    subgraph CMD[Command Layer]
        C1[weather command\n@wrap getopts user/forecast + text]
        C2{opts.user provided?}
        C3[hostmask = irc.state.nickToHostmask(opts.user)]
        C4[hostmask = msg.prefix]
        C5{location arg provided?}
        C6[location = arg]
        C7[location = self.db[hostmask]]
        C8{location found?}
        C9[irc.error: no saved location]
        C10[Run async pipeline on self._loop]
    end

    subgraph GEO[Geocoding Layer: google_maps(address)]
        G1{registryValue googlemapsAPI set?}
        G2[handle_error missing Google Maps API key]
        G3[fetch_data geocode endpoint\nmaps.googleapis.com/geocode/json]
        G4{data.status == OK?}
        G5[handle_error geocode failed]
        G6[Extract lat/lng/postcode/place_id/formatted_address]
    end

    subgraph WX[Weather Layer: openweather(lat, lon)]
        W1{registryValue openweatherAPI set?}
        W2[handle_error missing OpenWeather API key]
        W3[fetch_data onecall endpoint\napi.openweathermap.org/data/3.0/onecall]
        W4{HTTP+JSON success?}
        W5[handle_error from fetch_data]
        W6[Return weather_data]
    end

    subgraph FMT[Formatting Layer]
        F1{opts.forecast?}
        F2[format_weather_results location + weather_data]
        F3[format_current_conditions current block]
        F4[colour_temperature / colour_uvi / _get_wind_direction]
        F5[dd2dms + format_location]
        F6[Compose current-conditions reply]

        F7[format_forecast_results location + weather_data]
        F8[Iterate daily entries]
        F9[Compose multi-day forecast reply]
    end

    subgraph OUT[Output + Error Layer]
        O1[irc.reply response]
        O2[callbacks.Error raised by handle_error]
        O3[Done]
    end

    %% Command flow
    C1 --> C2
    C2 -->|yes| C3
    C2 -->|no| C4
    C3 --> C5
    C4 --> C5
    C5 -->|yes| C6
    C5 -->|no| C7
    C7 --> C8
    C8 -->|no| C9
    C8 -->|yes| C10
    C6 --> C10
    C9 --> O3

    %% Async pipeline: geocode then weather
    C10 --> G1
    G1 -->|no| G2
    G1 -->|yes| G3
    G3 --> G4
    G4 -->|no| G5
    G4 -->|yes| G6

    G6 --> W1
    W1 -->|no| W2
    W1 -->|yes| W3
    W3 --> W4
    W4 -->|no| W5
    W4 -->|yes| W6

    %% Formatting split
    W6 --> F1
    F1 -->|no| F2
    F2 --> F3
    F3 --> F4
    F4 --> F5
    F5 --> F6
    F6 --> O1

    F1 -->|yes| F7
    F7 --> F8
    F8 --> F9
    F9 --> O1

    %% Error propagation
    G2 --> O2
    G5 --> O2
    W2 --> O2
    W5 --> O2
    O2 --> O3
    O1 --> O3
