// Function to toggle between Light Mode and Dark Mode
function toggleMode() {
    const body = document.body;
    const button = document.getElementById("modeToggle");
    if (body.classList.contains("dark-mode")) {
        body.classList.remove("dark-mode");
        body.classList.add("light-mode");
        localStorage.setItem("theme", "light-mode");
        button.textContent = "Switch to Dark Mode";
    } else {
        body.classList.remove("light-mode");
        body.classList.add("dark-mode");
        localStorage.setItem("theme", "dark-mode");
        button.textContent = "Switch to Light Mode";
    }
}

// Store response data when the page loads
window.onload = function () {
    const theme = localStorage.getItem("theme") || "dark-mode";
    document.body.classList.add(theme);
    document.getElementById("modeToggle").textContent = theme === "dark-mode" ? "Switch to Light Mode" : "Switch to Dark Mode";

    // Capture response data from HTML (if available)
    window.originalResponse = document.getElementById("response-content").textContent;
    const parsedJsonElement = document.getElementById("parsed-json");
    window.parsedJsonResponse = parsedJsonElement ? parsedJsonElement.textContent : "Invalid JSON";
};

// Function to toggle between Original Response and Parsed JSON tabs
function showTab(tab) {
    const responseContent = document.getElementById("response-content");

    if (tab === "original") {
        responseContent.textContent = window.originalResponse; // Show original response
        document.getElementById("original-tab").classList.add("active");
        document.getElementById("json-tab").classList.remove("active");
    } else {
        responseContent.textContent = window.parsedJsonResponse; // Show parsed JSON
        document.getElementById("json-tab").classList.add("active");
        document.getElementById("original-tab").classList.remove("active");
    }
}

