
const menuBtn = document.getElementById("menuBtn");
const nav = document.getElementById("nav");
const form = document.getElementById("contactForm");
const statusText = document.getElementById("formStatus");

document.getElementById("year").textContent =
  new Date().getFullYear();

menuBtn.addEventListener("click", () => {
  const isOpen = nav.classList.toggle("open");
  menuBtn.setAttribute("aria-expanded", String(isOpen));
});

nav.querySelectorAll("a").forEach((link) => {
  link.addEventListener("click", () => {
    nav.classList.remove("open");
    menuBtn.setAttribute("aria-expanded", "false");
  });
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  statusText.textContent = "Sending message...";
  const submitButton = form.querySelector('button[type="submit"]');
  submitButton.disabled = true;

  const data = {
    name: form.elements.name.value.trim(),
    email: form.elements.email.value.trim(),
    message: form.elements.message.value.trim()
  };

  try {
    const response = await fetch("/api/contact", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data)
    });

    const result = await response.json();

    if (!response.ok) {
      throw new Error(result.detail || "Unable to send message.");
    }

    statusText.textContent = result.message;
    form.reset();
  } catch (error) {
    statusText.textContent =
      error.message || "Could not connect to the server. Please try again.";
  } finally {
    submitButton.disabled = false;
  }
});