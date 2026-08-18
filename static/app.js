const $ = (s) => document.querySelector(s);
const chat = $("#chat");
const input = $("#input");
const composer = $("#composer");
const activity = $("#activity");
const activityText = $("#activityText");
const connection = $("#connection");
const counter = $("#counter");
const sessionState = $("#sessionState");
const techLog = $("#techLog");
const modalRoot = $("#modalRoot");
const newSessionBtn = $("#newSession");

let threadId = localStorage.getItem("nexo_thread_id") || crypto.randomUUID();
let socket = null;
let reconnectTimer = null;
let sessionEnded = false;
let maxInteractions = 12;

function connect() {
  if (sessionEnded) return;
  const protocol = location.protocol === "https:" ? "wss" : "ws";
  socket = new WebSocket(`${protocol}://${location.host}/ws/${threadId}`);

  socket.onopen = () => {
    connection.classList.add("online");
    connection.lastChild.textContent = " conectado";
    sessionState.textContent = "Sesión activa";
  };

  socket.onclose = () => {
    connection.classList.remove("online");
    connection.lastChild.textContent = sessionEnded ? " cerrada" : " reconectando";
    if (!sessionEnded) {
      clearTimeout(reconnectTimer);
      reconnectTimer = setTimeout(connect, 1200);
    }
  };

  socket.onerror = () => logTech("error", "Error de WebSocket");
  socket.onmessage = ({ data }) => handleEvent(JSON.parse(data));
}

function send(payload) {
  if (sessionEnded || !socket || socket.readyState !== WebSocket.OPEN) return;
  socket.send(JSON.stringify(payload));
}

function handleEvent(event) {
  logTech(event.type, JSON.stringify(event));

  switch (event.type) {
    case "connected":
      maxInteractions = event.max_interacciones || maxInteractions;
      updateCounter(event.interacciones || 0);
      hideActivity();
      break;
    case "session_meta":
      maxInteractions = event.max_interacciones || maxInteractions;
      updateCounter(event.interacciones || 0);
      break;
    case "node_status":
    case "status":
      setThinking(event.message || "Procesando…");
      break;
    case "message":
      hideActivity();
      addMessage(event.content, "assistant", true);
      break;
    case "opciones_productos":
      hideActivity();
      renderProducts(event);
      break;
    case "opciones_accion":
      hideActivity();
      renderActions(event);
      break;
    case "formulario":
      hideActivity();
      renderForm(event);
      break;
    case "derivacion":
      hideActivity();
      renderDerivation(event.message);
      break;
    case "session_end":
      endSession(event.message, event.reason);
      break;
  }
}

function updateCounter(value) {
  counter.textContent = `${value}/${maxInteractions}`;
}

function setThinking(text) {
  activityText.textContent = text;
  activity.classList.remove("hidden");
  sessionState.textContent = text;
}

function hideActivity() {
  activity.classList.add("hidden");
  if (!sessionEnded) sessionState.textContent = "Sesión activa";
}

function addMessage(text, role, markdown = false) {
  $("#welcome")?.remove();
  const row = document.createElement("div");
  row.className = `row ${role}`;
  const bubble = document.createElement("div");
  bubble.className = `bubble ${markdown ? "markdown" : ""}`;
  if (markdown) bubble.innerHTML = renderMarkdown(text);
  else bubble.textContent = text;
  row.appendChild(bubble);
  chat.appendChild(row);
  scrollBottom();
}

function renderMarkdown(source = "") {
  const safe = escapeHtml(String(source)).replace(/\r/g, "");
  const lines = safe.split("\n");
  let out = "";
  let i = 0;
  let list = null;

  const closeList = () => {
    if (list) { out += `</${list}>`; list = null; }
  };

  while (i < lines.length) {
    const line = lines[i];

    if (line.includes("|") && i + 1 < lines.length && /^\s*\|?\s*:?-{3,}/.test(lines[i + 1])) {
      closeList();
      const headers = splitTable(line);
      i += 2;
      const rows = [];
      while (i < lines.length && lines[i].includes("|")) rows.push(splitTable(lines[i++]));
      out += `<div class="table-wrap"><table><thead><tr>${headers.map(c => `<th>${inlineMd(c)}</th>`).join("")}</tr></thead><tbody>`;
      out += rows.map(r => `<tr>${headers.map((_, idx) => `<td>${inlineMd(r[idx] || "")}</td>`).join("")}</tr>`).join("");
      out += "</tbody></table></div>";
      continue;
    }

    const heading = line.match(/^(#{1,3})\s+(.+)/);
    if (heading) {
      closeList();
      const n = heading[1].length;
      out += `<h${n}>${inlineMd(heading[2])}</h${n}>`;
      i++; continue;
    }

    const bullet = line.match(/^\s*[-*]\s+(.+)/);
    if (bullet) {
      if (list !== "ul") { closeList(); out += "<ul>"; list = "ul"; }
      out += `<li>${inlineMd(bullet[1])}</li>`;
      i++; continue;
    }

    const numbered = line.match(/^\s*\d+[.)]\s+(.+)/);
    if (numbered) {
      if (list !== "ol") { closeList(); out += "<ol>"; list = "ol"; }
      out += `<li>${inlineMd(numbered[1])}</li>`;
      i++; continue;
    }

    closeList();
    if (!line.trim()) out += "<br>";
    else out += `<p>${inlineMd(line)}</p>`;
    i++;
  }
  closeList();
  return out;
}

function inlineMd(text) {
  return text
    .replace(/`([^`]+)`/g, "<code>$1</code>")
    .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
    .replace(/\*([^*]+)\*/g, "<em>$1</em>");
}

function splitTable(line) {
  return line.trim().replace(/^\|/, "").replace(/\|$/, "").split("|").map(x => x.trim());
}

function formatPrice(value) {
  return new Intl.NumberFormat("es-CL", { style: "currency", currency: "CLP", maximumFractionDigits: 0 }).format(value);
}

function renderProducts(event) {
  const block = document.createElement("section");
  block.className = "visual-block";
  block.innerHTML = `<h3>${escapeHtml(event.titulo || "Opciones")}</h3><p>${escapeHtml(event.message || "")}</p>`;
  const cards = document.createElement("div");
  cards.className = "cards";

  (event.opciones || []).forEach(item => {
    const isOffer = event.modo === "ofertas" || item.precio_oferta != null;
    const price = isOffer ? item.precio_oferta : item.precio;
    const productId = item.producto_id || item.id;
    const card = document.createElement("article");
    card.className = "product-card";
    card.innerHTML = `
      <div class="product-image"><img src="${escapeAttr(item.imagen || "https://placehold.co/600x400?text=NEXO")}" alt=""></div>
      <div class="card-body">
        <h4>${escapeHtml(item.nombre)}</h4>
        ${item.descripcion ? `<p>${escapeHtml(item.descripcion)}</p>` : ""}
        ${isOffer ? `<div class="old-price">${formatPrice(item.precio_normal)}</div>` : ""}
        <div class="price">${formatPrice(price)}</div>
        <div class="badges">
          ${item.descuento ? `<span class="badge">-${escapeHtml(item.descuento)}</span>` : ""}
          ${item.stock != null ? `<span class="badge">Stock ${item.stock}</span>` : ""}
        </div>
        <button class="select-btn">Elegir este</button>
      </div>`;
    card.querySelector(".select-btn").addEventListener("click", () => {
      addMessage(`Quiero ${item.nombre}`, "user");
      setThinking(`Preparando ${item.nombre}…`);
      send({ type: "seleccion", producto_id: productId, nombre: item.nombre, modo: event.modo || "productos" });
    });
    cards.appendChild(card);
  });

  block.appendChild(cards);
  chat.appendChild(block);
  scrollBottom();
}

function renderActions(event) {
  const block = document.createElement("section");
  block.className = "action-block";
  block.innerHTML = `<h3>${escapeHtml(event.titulo || "¿Cómo seguimos?")}</h3><p>${escapeHtml(event.message || "")}</p>`;
  const wrap = document.createElement("div");
  wrap.className = "action-options";
  (event.opciones || []).forEach(option => {
    const button = document.createElement("button");
    button.className = "action-option";
    button.textContent = option;
    button.addEventListener("click", () => {
      addMessage(option, "user");
      setThinking("Revisando esa opción…");
      send({ type: "message", content: option });
    });
    wrap.appendChild(button);
  });
  block.appendChild(wrap);
  chat.appendChild(block);
  scrollBottom();
}

function renderForm(form) {
  const product = form.producto || {};
  const fields = (form.campos || []).map(field => `
    <div class="field">
      <label>${escapeHtml(field.label)}</label>
      <input name="${escapeAttr(field.name)}" type="${escapeAttr(field.type || "text")}" placeholder="${escapeAttr(field.placeholder || "")}" ${field.required ? "required" : ""}>
    </div>`).join("");

  modalRoot.innerHTML = `
    <div class="modal">
      <div class="modal-top">
        <div><span class="eyebrow">Solicitud de compra</span><h2>${escapeHtml(form.titulo || "Completa tus datos")}</h2></div>
        <button class="close-btn" data-cancel>×</button>
      </div>
      <div class="description">${escapeHtml(form.descripcion || "")}</div>
      <div class="checkout-product">
        <div><span>Producto</span><strong>${escapeHtml(product.nombre || "Producto")}</strong></div>
        ${product.precio ? `<strong>${formatPrice(product.precio)}</strong>` : ""}
      </div>
      <form id="checkoutForm">
        <div class="form-grid">${fields}</div>
        <div class="modal-actions">
          <button type="button" class="secondary" data-cancel>Cancelar</button>
          <button type="submit" class="primary">Enviar solicitud</button>
        </div>
      </form>
    </div>`;

  modalRoot.classList.remove("hidden");
  modalRoot.querySelectorAll("[data-cancel]").forEach(btn => btn.addEventListener("click", cancelForm));
  $("#checkoutForm").addEventListener("submit", e => {
    e.preventDefault();
    const values = Object.fromEntries(new FormData(e.currentTarget).entries());
    values.accion = "continuar";
    modalRoot.classList.add("hidden");
    setThinking("Registrando tu solicitud…");
    send({ type: "resume", data: values });
  });
}

function cancelForm() {
  modalRoot.classList.add("hidden");
  addMessage("Cancelar la solicitud", "user");
  send({ type: "resume", data: { accion: "cancelar" } });
}

function renderDerivation(message) {
  const box = document.createElement("div");
  box.className = "derivation markdown";
  box.innerHTML = renderMarkdown(message);
  chat.appendChild(box);
  scrollBottom();
}

function endSession(message, reason) {
  if (sessionEnded) return;
  sessionEnded = true;
  hideActivity();
  sessionState.textContent = reason === "compra_registrada" ? "Compra derivada · sesión cerrada" : "Sesión cerrada";
  input.disabled = true;
  $("#send").disabled = true;

  const card = document.createElement("section");
  card.className = "session-card";
  card.innerHTML = `<strong>Interacción finalizada</strong><p>${escapeHtml(message || "Puedes comenzar una conversación nueva.")}</p><button type="button">Iniciar nueva conversación</button>`;
  card.querySelector("button").addEventListener("click", startNewSession);
  chat.appendChild(card);
  scrollBottom();
  socket?.close(1000);
}

function startNewSession() {
  clearTimeout(reconnectTimer);
  if (socket) {
    socket.onclose = null;
    socket.close(1000);
  }
  threadId = crypto.randomUUID();
  localStorage.setItem("nexo_thread_id", threadId);
  sessionEnded = false;
  input.disabled = false;
  $("#send").disabled = false;
  chat.innerHTML = `
    <section class="welcome" id="welcome">
      <span class="kicker">Nueva conversación</span>
      <h1>¿Qué quieres resolver ahora?</h1>
      <p>Esta sesión parte limpia. Puedes buscar, comparar, pedir una recomendación o iniciar otra compra.</p>
      <div class="starter-grid">
        <button class="starter" data-message="¿Qué ofertas tienes hoy?">Ver ofertas <span>→</span></button>
        <button class="starter" data-message="Necesito un notebook para estudiar. ¿Qué me recomiendas?">Recomiéndame un notebook <span>→</span></button>
        <button class="starter" data-message="Compara los notebooks disponibles en una tabla">Comparar notebooks <span>→</span></button>
      </div>
    </section>`;
  bindStarters();
  updateCounter(0);
  connect();
}

function logTech(type, text) {
  const line = document.createElement("div");
  line.className = "tech-line";
  line.textContent = `[${type}] ${text}`;
  techLog.prepend(line);
  while (techLog.children.length > 60) techLog.lastChild.remove();
}

function scrollBottom() { requestAnimationFrame(() => chat.scrollTop = chat.scrollHeight); }
function escapeHtml(value = "") { const div = document.createElement("div"); div.textContent = String(value); return div.innerHTML; }
function escapeAttr(value = "") { return escapeHtml(value).replaceAll('"', '&quot;'); }

composer.addEventListener("submit", e => {
  e.preventDefault();
  const text = input.value.trim();
  if (!text || sessionEnded) return;
  addMessage(text, "user");
  send({ type: "message", content: text });
  input.value = "";
  input.style.height = "auto";
  setThinking("Interpretando tu mensaje…");
});

input.addEventListener("input", () => {
  input.style.height = "auto";
  input.style.height = `${Math.min(input.scrollHeight, 130)}px`;
});

input.addEventListener("keydown", e => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    composer.requestSubmit();
  }
});

function bindStarters() {
  document.querySelectorAll(".starter").forEach(btn => btn.addEventListener("click", () => {
    input.value = btn.dataset.message;
    composer.requestSubmit();
  }));
}

newSessionBtn.addEventListener("click", startNewSession);
bindStarters();
localStorage.setItem("nexo_thread_id", threadId);
connect();
