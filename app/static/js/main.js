// Main JavaScript file for Investment Tracker

// Refresh prices function
async function refreshPrices() {
  const btn = event.target.closest("button");
  const originalText = btn.innerHTML;

  btn.disabled = true;
  btn.innerHTML =
    '<i class="bi bi-arrow-clockwise spinner-border spinner-border-sm"></i> Actualizando...';

  try {
    const response = await fetch("/api/refresh-prices", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
    });

    const data = await response.json();

    if (data.success) {
      // Reload page to show updated prices
      location.reload();
    } else {
      alert("Error al actualizar precios");
      btn.innerHTML = originalText;
      btn.disabled = false;
    }
  } catch (error) {
    console.error("Error:", error);
    alert("Error al conectar con el servidor");
    btn.innerHTML = originalText;
    btn.disabled = false;
  }
}

// Format currency
function formatCurrency(value) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value);
}

// Format percentage
function formatPercentage(value) {
  return new Intl.NumberFormat("en-US", {
    style: "percent",
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value / 100);
}

// Show loading spinner
function showLoading(element) {
  const spinner = document.createElement("div");
  spinner.className = "spinner-border spinner-border-sm text-primary";
  spinner.setAttribute("role", "status");
  spinner.innerHTML = '<span class="visually-hidden">Loading...</span>';
  element.appendChild(spinner);
}

// Hide loading spinner
function hideLoading(element) {
  const spinner = element.querySelector(".spinner-border");
  if (spinner) {
    spinner.remove();
  }
}

// Confirm dialog
function confirmAction(message) {
  return new Promise((resolve) => {
    if (confirm(message)) {
      resolve(true);
    } else {
      resolve(false);
    }
  });
}

// Toast notification (using Bootstrap alerts)
function showToast(message, type = "info") {
  const alertDiv = document.createElement("div");
  alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3`;
  alertDiv.style.zIndex = "9999";
  alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

  document.body.appendChild(alertDiv);

  // Auto dismiss after 5 seconds
  setTimeout(() => {
    alertDiv.classList.remove("show");
    setTimeout(() => alertDiv.remove(), 150);
  }, 5000);
}

// Form validation helper
function validateForm(formElement) {
  const inputs = formElement.querySelectorAll(
    "input[required], select[required], textarea[required]",
  );
  let isValid = true;

  inputs.forEach((input) => {
    if (!input.value.trim()) {
      input.classList.add("is-invalid");
      isValid = false;
    } else {
      input.classList.remove("is-invalid");
    }
  });

  return isValid;
}

// Remove validation classes on input
document.addEventListener("DOMContentLoaded", function () {
  const inputs = document.querySelectorAll(".form-control, .form-select");
  inputs.forEach((input) => {
    input.addEventListener("input", function () {
      this.classList.remove("is-invalid");
    });
  });
});

// Auto-dismiss alerts after 5 seconds
document.addEventListener("DOMContentLoaded", function () {
  const alerts = document.querySelectorAll(".alert:not(.alert-dismissible)");
  alerts.forEach((alert) => {
    setTimeout(() => {
      alert.style.opacity = "0";
      setTimeout(() => alert.remove(), 300);
    }, 5000);
  });
});

// Number input formatting
function formatNumberInput(input, decimals = 2) {
  input.addEventListener("blur", function () {
    if (this.value) {
      const number = parseFloat(this.value);
      if (!isNaN(number)) {
        this.value = number.toFixed(decimals);
      }
    }
  });
}

// Initialize tooltips if Bootstrap tooltips are present
document.addEventListener("DOMContentLoaded", function () {
  const tooltipTriggerList = [].slice.call(
    document.querySelectorAll('[data-bs-toggle="tooltip"]'),
  );
  tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
  });
});

// Prevent form double submission
document.addEventListener("DOMContentLoaded", function () {
  const forms = document.querySelectorAll("form");
  forms.forEach((form) => {
    form.addEventListener("submit", function () {
      const submitBtn = this.querySelector('button[type="submit"]');
      if (submitBtn) {
        submitBtn.disabled = true;
        setTimeout(() => {
          submitBtn.disabled = false;
        }, 3000);
      }
    });
  });
});

// Export functions for use in templates
window.Investment = {
  formatCurrency,
  formatPercentage,
  showLoading,
  hideLoading,
  confirmAction,
  showToast,
  validateForm,
  refreshPrices,
};
