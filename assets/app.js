const searchInput = document.getElementById("search-input");
const cards = Array.from(document.querySelectorAll(".record-card"));
const resultCount = document.getElementById("result-count");

if (searchInput && resultCount) {
  const updateResults = () => {
    const query = searchInput.value.trim().toLowerCase();
    let visible = 0;

    cards.forEach((card) => {
      const haystack = (card.dataset.search || "").toLowerCase();
      const match = !query || haystack.includes(query);
      card.hidden = !match;
      if (match) visible += 1;
    });

    resultCount.textContent = `共 ${visible} 条`;
  };

  searchInput.addEventListener("input", updateResults);
  updateResults();
}
