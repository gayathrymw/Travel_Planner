async function init() {
  await customElements.whenDefined('gmp-map');

  const map = document.querySelector('gmp-map');
  const marker = document.querySelector('gmp-advanced-marker');
  const placePicker = document.querySelector('gmpx-place-picker');
  const destinationInput = document.querySelector('#destination');
  const infowindow = new google.maps.InfoWindow();

  placePicker.addEventListener('gmpx-placechange', () => {
    const place = placePicker.value;

    if (!place.location) {
      window.alert(
        "No details available for input: '" + place.name + "'"
      );
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

    infowindow.setContent(
      `<strong>${place.displayName}</strong><br>
         <span>${place.formattedAddress}</span>
      `);
    infowindow.open(map.innerMap, marker);

    if (destinationInput) {
      destinationInput.value = place.displayName;
    }
  });
}

document.addEventListener('DOMContentLoaded', init); // Run the init function only when the page is loaded