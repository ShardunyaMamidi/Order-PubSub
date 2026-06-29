const ws = new WebSocket(`ws://${location.host}/ws`);

ws.onmessage = (event) => {
  const { order_id, stage, status } = JSON.parse(event.data);
  updateRow(order_id, stage, status);
};

ws.onerror = () => console.error("WebSocket error");
ws.onclose = () => console.warn("WebSocket closed");

document.getElementById("order-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const item = document.getElementById("item").value.trim();
  const quantity = parseInt(document.getElementById("quantity").value);
  await placeOrder(item, quantity);
});

async function placeOrder(item, quantity) {
  const res = await fetch("/order", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ item, quantity }),
  });

  if (!res.ok) {
    console.error("Failed to place order");
    return;
  }

  const { order_id } = await res.json();
  addRow(order_id, item);
}

function addRow(order_id, item) {
  const tbody = document.getElementById("orders-body");
  const row = document.createElement("tr");
  row.id = `order-${order_id}`;
  row.innerHTML = `
    <td>${order_id.slice(0, 8)}...</td>
    <td>${item}</td>
    <td id="${order_id}-inventory" class="pending">pending</td>
    <td id="${order_id}-notification" class="pending">pending</td>
    <td id="${order_id}-analytics" class="pending">pending</td>
  `;
  tbody.prepend(row);
}

function updateRow(order_id, stage, status) {
  const cell = document.getElementById(`${order_id}-${stage}`);
  if (!cell) return;
  cell.textContent = status === "done" ? "✓" : "✗";
  cell.className = status === "done" ? "done" : "failed";
}
