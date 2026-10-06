setTimeout(() => {
  document.querySelectorAll(".popup").forEach((el) => {
    el.style.display = "none";
  });
}, 5000);

/* PANEL SWITCHING */

const titles = {
  overview: "Overview",
  bookings: "Booking Requests",
  availability: "Availability",
  services: "My Services",
  reviews: "Reviews",
  profile: "Profile Settings",
};

function switchPanel(id, element) {
  document.querySelectorAll(".panel").forEach((panel) => {
    panel.classList.remove("active");
  });

  document.querySelectorAll(".side-link").forEach((link) => {
    link.classList.remove("active");
  });

  const panel = document.getElementById("panel-" + id);

  if (panel) {
    panel.classList.add("active");
  }

  if (element) {
    element.classList.add("active");
  }

  document.getElementById("topbar-title").textContent = titles[id];
}

/* BOOKING FILTER */

function filterBookings(status, element) {
  document.querySelectorAll(".filter-tab").forEach((tab) => {
    tab.classList.remove("active");
  });

  element.classList.add("active");

  document.querySelectorAll("#panel-bookings .booking-card").forEach((card) => {
    if (status === "all" || card.dataset.status === status) {
      card.style.display = "flex";
    } else {
      card.style.display = "none";
    }
  });
}

/* BOOKING STATUS TOGGLE */

function toggleStatus(element) {
  const dot = element.querySelector(".status-dot");

  const currentlyAccepting = element.dataset.state !== "off";

  if (currentlyAccepting) {
    element.dataset.state = "off";

    element.style.background = "var(--danger-l)";

    element.style.color = "var(--danger)";

    dot.style.background = "var(--danger)";

    element.innerHTML =
      '<span class="status-dot" style="background:var(--danger)"></span>' +
      " Not Accepting Bookings";
  } else {
    element.dataset.state = "on";

    element.style.background = "var(--success-l)";

    element.style.color = "var(--success)";

    dot.style.background = "var(--success)";

    element.innerHTML =
      '<span class="status-dot" style="background:var(--success)"></span>' +
      " Accepting Bookings";
  }
}

function previewImage(event) {
  const preview = document.getElementById("preview");
  const file = event.target.files[0];
  if (!file || !preview) return;
  if (preview.tagName !== "IMG") {
    const image = document.createElement("img");
    image.id = "preview";
    image.alt = "Profile preview";
    preview.replaceWith(image);
  }
  document.getElementById("preview").src = URL.createObjectURL(file);
}

