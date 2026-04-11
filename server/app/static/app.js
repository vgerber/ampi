const api = (path, options) =>
  fetch(path, options).then((r) => {
    if (!r.ok) throw r;
    return r.json();
  });

async function scanDevices() {
  const btn = document.getElementById("scan-btn");
  const iface =
    document.getElementById("interface-input").value.trim() || "wlan0";
  localStorage.setItem("interface", iface);
  btn.textContent = "Scanning…";
  btn.disabled = true;
  try {
    const devices = await api(
      `/devices?interface=${encodeURIComponent(iface)}`,
    );
    renderDevices(devices);
  } catch (err) {
    alert("Scan failed");
  } finally {
    btn.textContent = "Scan";
    btn.disabled = false;
  }
}

function renderDevices(devices) {
  const container = document.getElementById("devices-list");
  if (!devices.length) {
    container.innerHTML = '<p class="empty">No devices found.</p>';
    return;
  }
  container.innerHTML = devices.map((device) => deviceCard(device)).join("");
  devices.forEach((device) => loadDeviceState(device.name));
}

function deviceCard(device) {
  return `
    <div class="card" id="card-${device.name}">
      <div class="card-title">${device.name} <span class="tag">${device.ip}</span></div>
      <div id="state-${device.name}">Loading…</div>
    </div>`;
}

async function loadDeviceState(deviceName) {
  try {
    const state = await api(`/devices/${deviceName}/states`);
    renderDeviceState(deviceName, state);
  } catch {
    document.getElementById(`state-${deviceName}`).textContent =
      "Failed to load state.";
  }
}

function renderDeviceState(deviceName, state) {
  const container = document.getElementById(`state-${deviceName}`);
  const signalPercent =
    state.signal != null
      ? `${Math.round(Math.min(Math.max(((state.signal + 100) / 60) * 100, 0), 100))}%`
      : "—";

  container.innerHTML = `
    <div class="signal-bar">Signal: ${state.signal ?? "—"} dBm (${signalPercent})</div>
    <div class="state-grid">
      <label>Red</label>
      <input type="range" min="0" max="255" value="${state.red ?? 0}"
        oninput="this.nextElementSibling.textContent=this.value"
        onchange="applyChannel('${deviceName}','red',this.value)">
      <span class="value-display">${state.red ?? 0}</span>

      <label>Yellow</label>
      <input type="range" min="0" max="255" value="${state.yellow ?? 0}"
        oninput="this.nextElementSibling.textContent=this.value"
        onchange="applyChannel('${deviceName}','yellow',this.value)">
      <span class="value-display">${state.yellow ?? 0}</span>

      <label>Green</label>
      <input type="range" min="0" max="255" value="${state.green ?? 0}"
        oninput="this.nextElementSibling.textContent=this.value"
        onchange="applyChannel('${deviceName}','green',this.value)">
      <span class="value-display">${state.green ?? 0}</span>
    </div>
    <div class="buzzer-row">
      <label>Buzzer</label>
      <label class="toggle">
        <input type="checkbox" ${state.buzzer ? "checked" : ""}
          onchange="applyChannel('${deviceName}','buzzer',this.checked?1:0)">
        <span class="toggle-slider"></span>
      </label>
    </div>
    <div class="actions-row">
      <button onclick="loadDeviceState('${deviceName}')">Refresh</button>
      <button class="danger" onclick="applyState('${deviceName}',{red:0,yellow:0,green:0,buzzer:0})">All off</button>
    </div>`;
}

async function applyChannel(deviceName, channel, value) {
  await applyState(deviceName, { [channel]: Number(value) });
}

async function applyState(deviceName, patch) {
  try {
    const state = await api(`/devices/${deviceName}/states`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(patch),
    });
    renderDeviceState(deviceName, state);
  } catch {
    alert(`Failed to update ${deviceName}`);
  }
}

async function loadTasks() {
  try {
    const [tasks, actions] = await Promise.all([
      api("/tasks"),
      api("/actions"),
    ]);
    renderCreateTaskForm(actions);
    renderTasks(tasks);
  } catch {
    document.getElementById("tasks-list").innerHTML =
      '<p class="empty">Failed to load tasks.</p>';
  }
}

function renderCreateTaskForm(actions) {
  const devices = Array.from(document.querySelectorAll("[id^='card-']")).map(
    (el) => el.id.replace("card-", ""),
  );
  const container = document.getElementById("task-create");
  container.innerHTML = `
    <div class="card" style="margin-bottom:1rem">
      <div class="state-grid" style="grid-template-columns: 80px 1fr; margin-bottom:0.5rem">
        <label>Name</label>
        <input id="task-name" type="text" placeholder="task" />
        <label>Device</label>
        <select id="task-device">
          ${devices.length ? devices.map((d) => `<option value="${d}">${d}</option>`).join("") : '<option value="">— scan first —</option>'}
        </select>
        <label>Action</label>
        <select id="task-action" onchange="loadActionSchema()">
          ${actions.map((a) => `<option value="${a}">${a}</option>`).join("")}
        </select>
      </div>
      <div id="task-args"></div>
      <div class="actions-row" style="margin-top:0.75rem">
        <button class="primary" onclick="startTask()">Start</button>
      </div>
    </div>`;
  if (actions.length) loadActionSchema();
}

let currentSchema = {};

async function loadActionSchema() {
  const action = document.getElementById("task-action").value;
  try {
    const schema = await api(`/actions/${action}/schema`);
    currentSchema = schema.properties ?? {};
    const required = schema.required ?? [];
    const argsContainer = document.getElementById("task-args");
    const fields = Object.entries(currentSchema)
      .filter(([key]) => key !== "device")
      .map(([key, def]) => {
        const isRequired = required.includes(key);
        const placeholder =
          def.default !== undefined ? String(def.default) : "";
        return `
          <div class="state-grid" style="grid-template-columns: 80px 1fr; margin-bottom:0.3rem">
            <label>${key}${isRequired ? "*" : ""}</label>
            <input data-arg="${key}" type="text" placeholder="${placeholder}" value="${placeholder}" />
          </div>`;
      })
      .join("");
    argsContainer.innerHTML = fields;
  } catch {
    document.getElementById("task-args").innerHTML = "";
  }
}

async function startTask() {
  const name = document.getElementById("task-name").value.trim() || "task";
  const device_name = document.getElementById("task-device").value;
  const action = document.getElementById("task-action").value;
  const arguments_ = {};
  document.querySelectorAll("[data-arg]").forEach((input) => {
    const value = input.value.trim();
    if (value !== "") {
      try {
        arguments_[input.dataset.arg] = JSON.parse(value);
      } catch {
        arguments_[input.dataset.arg] = value;
      }
    }
  });
  try {
    await api("/tasks", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name,
        device_name,
        action,
        arguments: arguments_,
      }),
    });
    loadTasks();
  } catch (error) {
    const detail = await error
      .json()
      .then((d) => d.detail)
      .catch(() => "Unknown error");
    alert(`Failed to start task: ${detail}`);
  }
}

function renderTasks(tasks) {
  const container = document.getElementById("tasks-list");
  const entries = Object.entries(tasks);
  if (!entries.length) {
    container.innerHTML = '<p class="empty">No running tasks.</p>';
    return;
  }
  container.innerHTML = entries
    .map(
      ([id, meta]) => `
    <div class="task-row">
      <span>${meta.name} <span class="tag">${meta.action}</span> → ${meta.device_name}</span>
      <button class="danger" onclick="deleteTask('${id}')">Stop</button>
    </div>`,
    )
    .join("");
}

async function deleteTask(taskId) {
  try {
    await fetch(`/tasks/${taskId}`, { method: "DELETE" });
    loadTasks();
  } catch {
    alert("Failed to stop task");
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const saved = localStorage.getItem("interface");
  if (saved) document.getElementById("interface-input").value = saved;
  loadTasks();
});
