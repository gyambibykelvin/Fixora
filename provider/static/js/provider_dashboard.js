/*    PANEL SWITCHING
       */

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

      /* =========================
   BOOKING FILTER
========================= */

      function filterBookings(status, element) {
        document.querySelectorAll(".filter-tab").forEach((tab) => {
          tab.classList.remove("active");
        });

        element.classList.add("active");

        document
          .querySelectorAll("#panel-bookings .booking-card")
          .forEach((card) => {
            if (status === "all" || card.dataset.status === status) {
              card.style.display = "flex";
            } else {
              card.style.display = "none";
            }
          });
      }

      /* =========================
   BOOKING STATUS TOGGLE
========================= */

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

      /* =========================
   DARK MODE
========================= */

      function toggleTheme() {
        const html = document.documentElement;

        const dark = html.getAttribute("data-theme") === "dark";

        if (dark) {
          html.setAttribute("data-theme", "light");

          document.getElementById("themeBtn").textContent = "🌙";
        } else {
          html.setAttribute("data-theme", "dark");

          document.getElementById("themeBtn").textContent = "☀️";
        }
      }