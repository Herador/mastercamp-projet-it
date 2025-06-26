const stations = [
      "Château Rouge", "Château D'eau", "Château de Vincennes", "Château-Landon",
      "Châtelet Les Halles", "Gare de Lyon", "Nation", "Porte de Clignancourt", "Place d'Italie",
      "Montparnasse-Bienvenue", "Bastille", "Gare du Nord", "République", "Opéra",
      "La Défense", "Saint-Lazare", "Pyrénées", "Jaurès", "Barbès-Rochechouart", "Odéon"
    ];

    const map = L.map('map').setView([48.857, 2.35], 13);
    L.tileLayer('https://{s}.tile.openstreetmap.fr/osmfr/{z}/{x}/{y}.png', {
      attribution: '&copy; OpenStreetMap contributors', maxZoom: 18
    }).addTo(map);

    const departInput = document.getElementById("depart");
    const arriveeInput = document.getElementById("arrivee");
    const suggestionsBox = document.getElementById("suggestions");
    const blueBox = document.getElementById("blue-box");

    let currentField = null;

    function showSuggestions(input, type) {
      const query = input.value.toLowerCase();
      const results = stations.filter(station => station.toLowerCase().includes(query));
      suggestionsBox.innerHTML = "";

      results.forEach(station => {
        const div = document.createElement("div");
        div.className = "suggestion-item";
        div.textContent = station;
        div.onclick = () => {
          input.value = station;
          suggestionsBox.innerHTML = "";
          blueBox.classList.remove("large");
          arriveeInput.style.display = "block";
          departInput.style.display = "block";
        };
        suggestionsBox.appendChild(div);
      });
    }

    departInput.addEventListener("focus", () => {
      currentField = "depart";
      blueBox.classList.add("large");
      arriveeInput.style.display = "none";
      showSuggestions(departInput, "depart");
    });

    arriveeInput.addEventListener("focus", () => {
      currentField = "arrivee";
      blueBox.classList.add("large");
      departInput.style.display = "none";
      showSuggestions(arriveeInput, "arrivee");
    });

    departInput.addEventListener("input", () => {
      if (currentField === "depart") showSuggestions(departInput);
    });

    arriveeInput.addEventListener("input", () => {
      if (currentField === "arrivee") showSuggestions(arriveeInput);
    });

    document.addEventListener("click", (e) => {
      if (!e.target.closest(".form-box")) {
        suggestionsBox.innerHTML = "";
        arriveeInput.style.display = "block";
        departInput.style.display = "block";
        blueBox.classList.remove("large");
      }
    });