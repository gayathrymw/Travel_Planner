const apiKey = '61e68d1bbecfb8f4ee9f86b7431a9db2';

async function getWeather(lat, lon) {
    try {
        const latitude = typeof lat === 'function' ? lat() : lat;
        const longitude = typeof lon === 'function' ? lon() : lon;

        // Current weather
        const weatherUrl = `https://api.openweathermap.org/data/2.5/weather?lat=${latitude}&lon=${longitude}&appid=${apiKey}&units=metric`;
        console.log("Fetching current weather data from:", weatherUrl);

        const response = await fetch(weatherUrl); // HTTP request to the weather API

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json(); // Parse the JSON response
        console.log("Current weather data received:", data);

        const weatherIcon = `http://openweathermap.org/img/wn/${data.weather[0].icon}.png`; 

        const weatherInfo = `
            <img src="${weatherIcon}" alt="${data.weather[0].description}" class="weather-icon">
            <strong>${data.name}</strong><br>
            Date: ${new Date(data.dt * 1000).toLocaleDateString()}<br>  
            ${data.weather[0].description.toUpperCase()} <br>

            Temperature: ${Math.round(data.main.temp)}°C<br>
            Feels Like: ${Math.round(data.main.feels_like)}°C<br>
            Humidity: ${data.main.humidity}%<br>
            Wind Speed: ${data.wind.speed} m/s<br>
        `;

        const weatherElement = document.getElementById('weatherInfo');
        if (weatherElement) {
            weatherElement.innerHTML = weatherInfo; 
        } else {
            console.error('Weather info element not found');
        }

        // Fetch 5-day forecast
        await get5DayForecast(latitude, longitude);
    } 
    
    catch (error) {
        console.error("Error fetching weather data:", error);
        const weatherElement = document.getElementById('weatherInfo');
        if (weatherElement) {
            weatherElement.innerHTML = `
                Unable to fetch weather data. 
                ${error.message}
            `;
        }
    }
}

async function get5DayForecast(lat, lon) {
    try {
        // 5-day forecast API
        const forecastUrl = `https://api.openweathermap.org/data/2.5/forecast?lat=${lat}&lon=${lon}&appid=${apiKey}&units=metric`; 
        console.log("Fetching 5-day forecast from:", forecastUrl);

        const response = await fetch(forecastUrl); 

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        console.log("5-day forecast data received:", data);

        // Group forecast by day
        const dailyForecasts = {};
        data.list.forEach(forecast => {
            const date = new Date(forecast.dt * 1000); // Convert timestamp to date
            const dateKey = date.toLocaleDateString('en-US', { weekday: 'short' });

            if (!dailyForecasts[dateKey]) { // Create a new entry for each day
                dailyForecasts[dateKey] = {
                    temps: [],
                    weather: forecast.weather[0],
                    icon: forecast.weather[0].icon
                };
            }
            dailyForecasts[dateKey].temps.push(forecast.main.temp); // Add temperature to the day
        });

        // Create forecast HTML
        let forecastHTML = '<div class="forecast-container">';
        forecastHTML += '<h4 class="text-center mt-3">5-Day Forecast</h4>';
        forecastHTML += '<div class="row justify-content-center">';

        // Process and display forecast
        Object.entries(dailyForecasts).slice(0, 5).forEach(([day, forecast]) => { 
            const weatherIcon = `http://openweathermap.org/img/wn/${forecast.icon}.png`;
            const maxTemp = Math.round(Math.max(...forecast.temps)); // ... is the spread operator to unpack the array
            const minTemp = Math.round(Math.min(...forecast.temps));

            // Add forecast to the HTML 
            forecastHTML += `
                <div class="col-md-2 text-center mx-2 forecast-day">
                    <p class="mb-1">${day}</p>
                    <img src="${weatherIcon}" alt="${forecast.weather.description}" class="forecast-icon">
                    <p class="mb-0">
                        <span class="text-info">${maxTemp}°</span> / 
                        <span class="text-dark">${minTemp}°</span>
                    </p>
                    <small class="text-capitalize">${forecast.weather.description}</small>
                </div>
            `;
        });

        forecastHTML += '</div></div>'; 

        // Add forecast to the weather info section
        const weatherElement = document.getElementById('weatherInfo');
        if (weatherElement) {
            weatherElement.innerHTML += forecastHTML;
        }
    } 
    
    catch (error) {
        console.error("Error fetching 5-day forecast:", error);
        const weatherElement = document.getElementById('weatherInfo');
        if (weatherElement) {
            weatherElement.innerHTML += `
                <p class="text-danger">Unable to fetch 5-day forecast. 
                ${error.message}</p>
            `;
        }
    }
}

async function init() {
    await customElements.whenDefined('gmp-map');
    const map = document.querySelector('gmp-map');
    const marker = document.querySelector('gmp-advanced-marker');
    const placePicker = document.querySelector('gmpx-place-picker');
    const infowindow = new google.maps.InfoWindow();

    placePicker.addEventListener('gmpx-placechange', () => {
        const place = placePicker.value;

        if (!place.location) {
            window.alert("No details available for input: '" + place.name + "'");
            infowindow.close();
            marker.position = null;
            return;
        }

        if (place.viewport) {
            map.innerMap.fitBounds(place.viewport);
        } else {
            map.center = place.location;
            map.zoom = 17;
        }

        marker.position = place.location;
        const locationTitleElement = document.getElementById('locationTitle');
        if (locationTitleElement) {
            locationTitleElement.textContent = `Location: ${place.displayName}`;
        }

        // Fetch and display weather info for the selected place
        const { lat, lng } = place.location;
        console.log("Latitude and Longitude:", lat, lng);

        getWeather(lat, lng);
    });
}

document.addEventListener('DOMContentLoaded', init);