       const timeSlots = document.querySelectorAll(".time-slot");

      timeSlots.forEach((slot) => {
        slot.addEventListener("click", () => {
          timeSlots.forEach((item) => item.classList.remove("active"));
          slot.classList.add("active");
        });
      });
 
 // Reveal
        const reveals = document.querySelectorAll(".reveal");

        const observer = new IntersectionObserver(
          (entries) => {
            entries.forEach((entry) => {
              if (entry.isIntersecting) {
                entry.target.classList.add("active");
              }
            });
          },
          {
            threshold: 0.2,
          },
        );

        reveals.forEach((el) => observer.observe(el));