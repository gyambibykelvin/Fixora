setTimeout(() => {
  document.querySelectorAll(".popup").forEach((el) => {
    el.style.display = "none";
  });
}, 5000);

/* service modal function */
function openBookingModal(serviceType = null) {
  const modal = document.getElementById("bookingModal");

  modal.classList.add("active");
  document.body.style.overflow = "hidden";

  if (serviceType) {
    const serviceInput = document.getElementById(`service_${serviceType}`);

    if (serviceInput) {
      serviceInput.checked = true;
      loadProviders(serviceType);
    }
  }
}

function closeBookingModal() {
  document.getElementById("bookingModal").classList.remove("active");

  document.body.style.overflow = "auto";
}

document.getElementById("bookingModal").addEventListener("click", function (e) {
  if (e.target === this) {
    closeBookingModal();
  }
});

function loadProviders(serviceType) {
  const container = document.getElementById("providersContainer");

  if (!serviceType) {
    container.innerHTML =
      '<div style="text-align: center; padding: 20px; color: var(--sub)">Select a service type above to view available providers</div>';
    return;
  }

  const allProviders = JSON.parse(
    document.getElementById("available-providers-data").textContent,
  );

  const selectedDelivery = document.querySelector(
    'input[name="delivery_type"]:checked',
  )?.value;
  const selectedMode =
    selectedDelivery === "home_delivery"
      ? "home"
      : selectedDelivery === "pickup"
        ? "walk_in"
        : null;

  const providers = allProviders.filter(
    (provider) =>
      provider.service_type === serviceType &&
      (!selectedMode ||
        provider.service_mode === selectedMode ||
        provider.service_mode === "both"),
  );

  if (providers.length === 0) {
    container.innerHTML =
      '<div style="text-align: center; padding: 20px; color: var(--sub)">No providers available for this service</div>';

    return;
  }

  container.innerHTML = providers
    .map(
      (provider) => `
              <div
                class="provider-option"
                onclick="selectProvider(${provider.id}, this)"
              >
                <div class="provider-radio"></div>

                <div class="provider-info">
                  <div class="provider-info-name">
                    ${provider.full_name}
                  </div>

                  <div class="provider-info-rating">
                    ⭐ ${provider.rating} rating
                  </div>
                </div>
              </div>
            `,
    )
    .join("");
}

function selectProvider(providerId, element) {
  document.getElementById("provider_id").value = providerId;

  document
    .querySelectorAll(".provider-option")
    .forEach((option) => option.classList.remove("selected"));

  element.classList.add("selected");
  loadAvailableTimes();
}

let availabilityRequest = 0;

async function loadAvailableTimes() {
  const timeSelect = document.getElementById("service_time");
  const providerId = document.getElementById("provider_id").value;
  const date = document.querySelector('input[name="service_date"]').value;
  const requestId = ++availabilityRequest;

  timeSelect.innerHTML = "";
  timeSelect.disabled = true;

  if (!providerId || !date) {
    timeSelect.add(new Option("Select a provider and date first", ""));
    return;
  }

  timeSelect.add(new Option("Loading available times...", ""));
  try {
    const query = new URLSearchParams({ provider_id: providerId, date });
    const response = await fetch(
      `${timeSelect.dataset.availabilityUrl}?${query.toString()}`,
      { headers: { "X-Requested-With": "XMLHttpRequest" } },
    );
    if (!response.ok) throw new Error("Availability could not be loaded");
    const { times } = await response.json();
    if (requestId !== availabilityRequest) return;

    timeSelect.innerHTML = "";
    if (times.length === 0) {
      timeSelect.add(new Option("No available times for this date", ""));
      return;
    }

    timeSelect.add(new Option("Choose an available time", ""));
    times.forEach((time) => timeSelect.add(new Option(time, time)));
    timeSelect.disabled = false;
  } catch (error) {
    if (requestId !== availabilityRequest) return;
    timeSelect.innerHTML = "";
    timeSelect.add(new Option("Could not load available times", ""));
  }
}

document.addEventListener("change", function (e) {
  if (e.target.name === "service_type" || e.target.name === "delivery_type") {
    const selectedService = document.querySelector(
      'input[name="service_type"]:checked',
    )?.value;
    loadProviders(selectedService);
    document.getElementById("provider_id").value = "";
    loadAvailableTimes();
  }
});

const serviceDateInput = document.querySelector('input[name="service_date"]');
serviceDateInput.addEventListener("input", loadAvailableTimes);
serviceDateInput.addEventListener("change", loadAvailableTimes);
