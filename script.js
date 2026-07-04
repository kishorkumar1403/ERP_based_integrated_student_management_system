// Campus ERP — small client-side interactions

document.addEventListener("DOMContentLoaded", () => {
  // Auto-dismiss flash messages after 4 seconds
  document.querySelectorAll(".flash").forEach((el) => {
    setTimeout(() => {
      el.style.transition = "opacity .4s ease";
      el.style.opacity = "0";
      setTimeout(() => el.remove(), 400);
    }, 4000);
  });

  // Confirm before any destructive action that doesn't already have its own handler
  document.querySelectorAll("form[data-confirm]").forEach((form) => {
    form.addEventListener("submit", (e) => {
      if (!confirm(form.dataset.confirm)) e.preventDefault();
    });
  });
});
