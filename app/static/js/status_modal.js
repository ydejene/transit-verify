// status_modal.js — Terminal Manager status-update modal
// Wires the Pending status badges to the modal, validates the receipt
// format client-side, and posts the update to the dashboard route.

(function () {
  const RECEIPT_PATTERN = /^RCP-\d{4}-\d{3}$/;

  const overlay = document.getElementById("statusModalOverlay");
  if (!overlay) return; // modal only exists for Terminal Manager role

  const form = document.getElementById("statusModalForm");
  const plateEl = document.getElementById("statusModalPlate");
  const violationEl = document.getElementById("statusModalViolation");
  const receiptGroup = document.getElementById("statusModalReceiptGroup");
  const receiptInput = document.getElementById("statusModalReceiptInput");
  const receiptError = document.getElementById("statusModalReceiptError");
  const closeBtn = document.getElementById("statusModalClose");
  const cancelBtn = document.getElementById("statusModalCancel");
  const confirmBtn = document.getElementById("statusModalConfirm");

  let activeAnomalyId = null;
  let activeBadge = null;

  function openModal(badge) {
    activeAnomalyId = badge.dataset.anomalyId;
    activeBadge = badge;
    plateEl.textContent = badge.dataset.plate;
    violationEl.textContent = badge.dataset.violation;
    form.reset();
    updateReceiptFieldState();
    overlay.hidden = false;
  }

  function closeModal() {
    overlay.hidden = true;
    activeAnomalyId = null;
    activeBadge = null;
    receiptError.hidden = true;
  }

  function selectedStatus() {
    return form.querySelector('input[name="statusUpdate"]:checked').value;
  }

  function updateReceiptFieldState() {
    const isResolved = selectedStatus() === "Resolved";
    receiptInput.disabled = !isResolved;
    receiptGroup.dataset.disabled = String(!isResolved);
    if (!isResolved) {
      receiptInput.value = "";
      receiptError.hidden = true;
    }
  }

  document.querySelectorAll(".status-badge--clickable").forEach((badge) => {
    badge.addEventListener("click", () => openModal(badge));
  });

  form.addEventListener("change", updateReceiptFieldState);
  closeBtn.addEventListener("click", closeModal);
  cancelBtn.addEventListener("click", closeModal);
  overlay.addEventListener("click", (event) => {
    if (event.target === overlay) closeModal();
  });

  confirmBtn.addEventListener("click", async () => {
    const status = selectedStatus();
    const receipt = receiptInput.value.trim();

    if (status === "Resolved" && !RECEIPT_PATTERN.test(receipt)) {
      receiptError.hidden = false;
      return;
    }
    receiptError.hidden = true;

    const response = await fetch(`/dashboard/anomalies/${activeAnomalyId}/status`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status, penaltyReceiptRef: status === "Resolved" ? receipt : "" }),
    });

    if (!response.ok) {
      const body = await response.json().catch(() => ({}));
      receiptError.textContent = body.error || "Could not update status.";
      receiptError.hidden = false;
      return;
    }

    location.reload();
  });
})();
