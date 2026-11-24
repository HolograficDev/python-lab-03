const STATUS_TITLES = { planned: "В планах", reading: "Читаем", finished: "Прочитана" };
const ACTION_TITLES = { created: "создана", updated: "изменена", deleted: "удалена" };

const $ = (id) => document.getElementById(id);
let editingId = null;
let chart = null;

function showError(message) {
  const box = $("error");
  box.textContent = message;
  box.hidden = !message;
}

async function api(method, path, body) {
  const response = await fetch(path, {
    method,
    headers: { "Content-Type": "application/json" },
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!response.ok) {
    let detail = `Ошибка ${response.status}`;
    try {
      const data = await response.json();
      detail = typeof data.detail === "string" ? data.detail : JSON.stringify(data.detail);
    } catch (_) {}
    throw new Error(detail);
  }
  return response.status === 204 ? null : response.json();
}

function esc(text) {
  const el = document.createElement("div");
  el.textContent = text ?? "";
  return el.innerHTML;
}

async function loadBooks() {
  const books = await api("GET", "/books");
  $("books-body").innerHTML = books.map((b) => `
    <tr>
      <td>${b.id}</td><td>${esc(b.title)}</td><td>${esc(b.author)}</td>
      <td>${esc(b.genre)}</td><td>${b.pages}</td><td>${STATUS_TITLES[b.status]}</td>
      <td>${esc(b.suggested_by)}</td><td>${b.rating ?? "—"}</td>
      <td>${b.finished_on ?? "—"}</td>
      <td>
        <button class="small" onclick='startEdit(${JSON.stringify(b)})'>Изменить</button>
        <button class="small danger" onclick="removeBook(${b.id})">Удалить</button>
      </td>
    </tr>`).join("");
}

async function loadStatistics() {
  const s = await api("GET", "/statistics");
  const avg = s.average_rating === null ? "—" : s.average_rating.toFixed(2);
  const best = s.best_book ? `${esc(s.best_book.title)} (${s.best_book.rating}/5)` : "—";
  $("stats").innerHTML = `
    <div class="stat"><b>${s.total_count}</b>всего книг</div>
    <div class="stat"><b>${s.by_status.finished}</b>прочитано</div>
    <div class="stat"><b>${s.by_status.reading}</b>читаем сейчас</div>
    <div class="stat"><b>${s.by_status.planned}</b>в планах</div>
    <div class="stat"><b>${avg}</b>средняя оценка</div>
    <div class="stat"><b>${s.total_pages_read}</b>страниц прочитано</div>
    <div class="stat"><b>${best}</b>лучшая книга</div>`;

  if (chart) chart.destroy();
  chart = new Chart($("chart"), {
    type: "bar",
    data: {
      labels: s.finished_by_month.map((m) => m.month),
      datasets: [{ label: "Прочитано книг по месяцам",
                   data: s.finished_by_month.map((m) => m.count),
                   backgroundColor: "#8a6a43" }],
    },
    options: { scales: { y: { beginAtZero: true, ticks: { precision: 0 } } } },
  });
}

async function loadLog() {
  const entries = await api("GET", "/activity-log");
  $("log").innerHTML = entries.map((e) => {
    const time = new Date(e.created_at).toLocaleString("ru-RU");
    return `<li>${time} — ${esc(e.details)} (${ACTION_TITLES[e.action]})</li>`;
  }).join("");
}

async function refresh() {
  try {
    await Promise.all([loadBooks(), loadStatistics(), loadLog()]);
  } catch (error) {
    showError(error.message);
  }
}

function formData() {
  const status = $("status").value;
  return {
    title: $("title").value,
    author: $("author").value,
    genre: $("genre").value,
    pages: Number($("pages").value),
    suggested_by: $("suggested_by").value,
    status,
    rating: $("rating").value ? Number($("rating").value) : null,
    finished_on: $("finished_on").value || null,
  };
}

function resetForm() {
  editingId = null;
  $("book-form").reset();
  $("form-title").textContent = "Добавить книгу";
  $("submit-btn").textContent = "Добавить";
  $("cancel-btn").hidden = true;
}

window.startEdit = (book) => {
  editingId = book.id;
  $("title").value = book.title;
  $("author").value = book.author;
  $("genre").value = book.genre;
  $("pages").value = book.pages;
  $("suggested_by").value = book.suggested_by;
  $("status").value = book.status;
  $("rating").value = book.rating ?? "";
  $("finished_on").value = book.finished_on ?? "";
  $("form-title").textContent = `Изменить книгу №${book.id}`;
  $("submit-btn").textContent = "Сохранить";
  $("cancel-btn").hidden = false;
  window.scrollTo({ top: 0, behavior: "smooth" });
};

window.removeBook = async (id) => {
  if (!confirm("Удалить книгу?")) return;
  try {
    await api("DELETE", `/books/${id}`);
    showError("");
    await refresh();
  } catch (error) {
    showError(error.message);
  }
};

$("book-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    if (editingId === null) await api("POST", "/books", formData());
    else await api("PUT", `/books/${editingId}`, formData());
    showError("");
    resetForm();
    await refresh();
  } catch (error) {
    showError(error.message);
  }
});

$("cancel-btn").addEventListener("click", resetForm);
refresh();
