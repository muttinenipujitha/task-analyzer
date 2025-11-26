const API_BASE = "http://127.0.0.1:8000/api/tasks";

const form = document.getElementById("task-form");
const clearBtn = document.getElementById("clear-tasks");
const loadJsonBtn = document.getElementById("load-json");
const jsonInput = document.getElementById("json-input");
const jsonError = document.getElementById("json-error");

const strategySelect = document.getElementById("strategy");
const strategyDescription = document.getElementById("strategy-description");

const analyzeBtn = document.getElementById("analyze");
const suggestBtn = document.getElementById("suggest");
const statusEl = document.getElementById("status");

const resultsEl = document.getElementById("results");
const suggestionsEl = document.getElementById("suggestions");
const emptyEl = document.getElementById("task-list-empty");

let tasks = [];

const STRATEGY_COPY = {
  smart_balance:
    "Balances urgency, importance, effort and dependencies. Ideal default when you want a realistic view of what to pick next.",
  fastest_wins:
    "Pushes small, low-effort tasks to the top so you can clear your queue quickly and build momentum.",
  high_impact:
    "Optimised for importance. Great when you care more about impact than quantity of tasks completed.",
  deadline_driven:
    "Sorts primarily by due date so you rarely miss deadlines, even if a task is slightly less important.",
};

function setStatus(message, kind = "info") {
  statusEl.textContent = message || "";
  statusEl.classList.remove("loading", "error", "success");
  if (kind === "loading") statusEl.classList.add("loading");
  if (kind === "error") statusEl.classList.add("error");
  if (kind === "success") statusEl.classList.add("success");
}

function refreshEmptyState() {
  if (tasks.length === 0) {
    emptyEl.classList.remove("hidden");
  } else {
    emptyEl.classList.add("hidden");
  }
}

function parseDependencies(input) {
  if (!input) return [];
  return input
    .split(",")
    .map((s) => s.trim())
    .filter(Boolean);
}

function addTaskFromForm(event) {
  event.preventDefault();
  const title = document.getElementById("title").value.trim();
  const due_date = document.getElementById("due_date").value || null;
  const estimated_hoursRaw =
    document.getElementById("estimated_hours").value;
  const importanceRaw = document.getElementById("importance").value;
  const dependenciesRaw = document.getElementById("dependencies").value;

  if (!title) {
    setStatus("Title is required.", "error");
    return;
  }

  const task = {
    id: `T${tasks.length + 1}`,
    title,
    due_date: due_date || null,
    estimated_hours:
      estimated_hoursRaw === "" ? null : Number(estimated_hoursRaw),
    importance: importanceRaw === "" ? null : Number(importanceRaw),
    dependencies: parseDependencies(dependenciesRaw),
  };

  tasks.push(task);
  form.reset();
  refreshEmptyState();
  renderTasksPreview();
  setStatus(
    `Task "${title}" added. Total tasks in memory: ${tasks.length}.`,
    "success"
  );
}

function renderTasksPreview() {
  // We show tasks only after analysis; this is a lightweight helper
  if (tasks.length === 0) {
    resultsEl.innerHTML = "";
    suggestionsEl.innerHTML = "";
    emptyEl.classList.remove("hidden");
  }
}

function handleClearTasks() {
  tasks = [];
  resultsEl.innerHTML = "";
  suggestionsEl.innerHTML = "";
  refreshEmptyState();
  setStatus("Cleared all tasks from memory.", "success");
}

function handleLoadJson() {
  const text = jsonInput.value.trim();
  jsonError.classList.add("hidden");
  jsonError.textContent = "";

  if (!text) {
    jsonError.textContent = "Please paste a JSON array first.";
    jsonError.classList.remove("hidden");
    return;
  }

  try {
    const parsed = JSON.parse(text);
    if (!Array.isArray(parsed)) {
      throw new Error("JSON should be an array of tasks.");
    }
    // Add ids if missing
    tasks = parsed.map((t, idx) => ({
      id: t.id || `T${idx + 1}`,
      ...t,
    }));
    refreshEmptyState();
    renderTasksPreview();
    setStatus(
      `Loaded ${tasks.length} task(s) from JSON. Click Analyze to score them.`,
      "success"
    );
  } catch (err) {
    console.error(err);
    jsonError.textContent = "Invalid JSON: " + err.message;
    jsonError.classList.remove("hidden");
  }
}

function getStrategyDescription(value) {
  return STRATEGY_COPY[value] || STRATEGY_COPY.smart_balance;
}

function updateStrategyDescription() {
  const value = strategySelect.value;
  strategyDescription.textContent = getStrategyDescription(value);
}

async function analyzeTasks() {
  if (tasks.length === 0) {
    setStatus("Add at least one task before analyzing.", "error");
    return;
  }

  const strategy = strategySelect.value || "smart_balance";
  setStatus("Analyzing tasks…", "loading");

  try {
    const response = await fetch(`${API_BASE}/analyze/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ strategy, tasks }),
    });

    if (!response.ok) {
      const errorPayload = await response.json().catch(() => ({}));
      throw new Error(
        errorPayload.detail ||
          "Backend returned status " + response.status
      );
    }

    const data = await response.json();
    renderAnalyzedTasks(data);
    setStatus(
      `Analyzed ${data.length} task(s) using "${strategy.replace(
        "_",
        " "
      )}" strategy.`,
      "success"
    );
  } catch (err) {
    console.error(err);
    setStatus("Failed to analyze tasks: " + err.message, "error");
  }
}

function renderAnalyzedTasks(analyzed) {
  if (!Array.isArray(analyzed) || analyzed.length === 0) {
    resultsEl.innerHTML = "";
    emptyEl.classList.remove("hidden");
    return;
  }

  emptyEl.classList.add("hidden");
  resultsEl.innerHTML = analyzed.map(renderTaskCard).join("");
}

function renderTaskCard(task) {
  const label = (task.priority_label || "").toLowerCase();
  const priorityClass =
    label === "high"
      ? "priority-high"
      : label === "medium"
      ? "priority-medium"
      : "priority-low";

  const metadata = task.metadata || {};
  const parts = [];

  if (metadata.urgency !== undefined) {
    parts.push(`Urgency ${metadata.urgency}`);
  }
  if (metadata.importance !== undefined) {
    parts.push(`Importance ${metadata.importance}`);
  }
  if (metadata.effort_quick_win !== undefined) {
    parts.push(`Quick-win ${metadata.effort_quick_win}`);
  }
  if (metadata.dependency_breadth !== undefined) {
    parts.push(`Blocks ${metadata.dependency_breadth}`);
  }

  const extraFlags = [];
  if (metadata.is_past_due) {
    extraFlags.push("Past due");
  }
  if (metadata.is_in_circular_dependency) {
    extraFlags.push("Circular dependency");
  }

  const due = task.due_date ? new Date(task.due_date) : null;
  const dueDisplay = due
    ? due.toLocaleDateString(undefined, {
        year: "numeric",
        month: "short",
        day: "numeric",
      })
    : "N/A";

  return `
    <article class="task-card">
      <div class="priority-indicator ${priorityClass}"></div>
      <div class="task-title">${task.title || "Untitled task"}</div>
      <div class="task-meta">
        <span class="pill score">Score: ${task.calculated_score}</span>
        <span class="pill">${task.priority_label || "Unknown"} priority</span>
        <span class="pill strategy">${(task.strategy || "")
          .replace("_", " ")
          .toUpperCase()}</span>
      </div>
      <div class="task-meta">
        <span>Due: ${dueDisplay}</span>
        <span>Est. hours: ${
          task.estimated_hours == null ? "N/A" : task.estimated_hours
        }</span>
        <span>Importance: ${
          task.importance == null ? "N/A" : task.importance
        }</span>
      </div>
      <p class="explanation">${task.explanation || ""}</p>
      <div class="metadata">
        ${
          parts.length
            ? parts
                .map(
                  (p) =>
                    `<span>${p
                      .toString()
                      .replace("dependency_breadth", "blocks")}</span>`
                )
                .join("")
            : ""
        }
        ${
          extraFlags.length
            ? extraFlags.map((f) => `<span>${f}</span>`).join("")
            : ""
        }
      </div>
    </article>
  `;
}

async function suggestTopTasks() {
  setStatus("Fetching suggestions…", "loading");
  suggestionsEl.innerHTML = "";

  try {
    const strategy = strategySelect.value || "smart_balance";
    const url = new URL(`${API_BASE}/suggest/`);
    url.searchParams.set("strategy", strategy);
    url.searchParams.set("limit", "3");

    const response = await fetch(url.toString(), {
      method: "GET",
    });

    if (!response.ok) {
      const errorPayload = await response.json().catch(() => ({}));
      throw new Error(
        errorPayload.detail ||
          "Backend returned status " + response.status
      );
    }

    const data = await response.json();
    if (!data.tasks || data.tasks.length === 0) {
      suggestionsEl.innerHTML =
        '<p class="empty-state">No suggestions available yet.</p>';
      setStatus("No suggestions returned from backend.", "info");
      return;
    }

    suggestionsEl.innerHTML = data.tasks.map(renderTaskCard).join("");
    setStatus("Suggested tasks updated.", "success");
  } catch (err) {
    console.error(err);
    setStatus("Failed to fetch suggestions: " + err.message, "error");
  }
}

// Event bindings
form.addEventListener("submit", addTaskFromForm);
clearBtn.addEventListener("click", handleClearTasks);
loadJsonBtn.addEventListener("click", handleLoadJson);
analyzeBtn.addEventListener("click", analyzeTasks);
suggestBtn.addEventListener("click", suggestTopTasks);
strategySelect.addEventListener("change", updateStrategyDescription);

// Initial UI state
updateStrategyDescription();
refreshEmptyState();
