 setTimeout(()=>{
        document.querySelectorAll('.popup').forEach(el => {
          el.style.display='none';
        });
      }, 5000);


  function openBookingModal(serviceType = null) {
        const modal = document.getElementById("bookingModal");

        modal.classList.add("active");
        document.body.style.overflow = "hidden";

        if (serviceType) {
          const serviceInput = document.getElementById(
            `service_${serviceType}`,
          );

          if (serviceInput) {
            serviceInput.checked = true;
            loadProviders(serviceType);
          }
        }
      }

      function closeBookingModal() {
        document
          .getElementById("bookingModal")
          .classList.remove("active");

        document.body.style.overflow = "auto";
      }

      document
        .getElementById("bookingModal")
        .addEventListener("click", function (e) {
          if (e.target === this) {
            closeBookingModal();
          }
        });

      function loadProviders(serviceType) {
        const container =
          document.getElementById("providersContainer");

        const allProviders = JSON.parse(
          document.getElementById("available-providers-data").textContent,
        );

        const providers = allProviders.filter(
          (provider) => provider.service_type === serviceType,
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
                onclick="selectProvider(${provider.id})"
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

      function selectProvider(providerId) {
        document.getElementById("provider_id").value = providerId;

        document
          .querySelectorAll(".provider-option")
          .forEach((option) => option.classList.remove("selected"));

        event.currentTarget.classList.add("selected");
      }

      document.addEventListener("change", function (e) {
        if (e.target.name === "service_type") {
          loadProviders(e.target.value);
          document.getElementById("provider_id").value = "";
        }
      });