// Envía el formulario de un modelo a su endpoint de la API y muestra el resultado.
(() => {
  const form = document.getElementById("form");
  const result = document.getElementById("result");
  const resultBody = document.getElementById("result-body");
  const placeholder = [...resultBody.childNodes];
  const button = form.querySelector("button[type=submit]");

  // Si no fuma, la cantidad de cigarrillos se fija en 0
  const smoker = form.elements.currentSmoker;
  const cigs = form.elements.cigsPerDay;
  if (smoker && cigs) {
    const sync = () => {
      cigs.disabled = smoker.value === "0";
      if (cigs.disabled) cigs.value = "0";
    };
    smoker.addEventListener("change", () => {
      sync();
      // Al habilitarlo se vacía para obligar a ingresar la cantidad real
      if (!cigs.disabled) { cigs.value = ""; cigs.focus(); }
    });
    sync();
  }

  function fieldError(input) {
    const value = input.value.trim();
    const min = Number(input.min);
    const max = Number(input.max);
    // En un input type=number, el texto no numérico llega como value vacío
    if (input.validity.badInput) return "Debe ser un número";
    if (value === "") return "Campo requerido";
    const number = Number(value);
    if (!Number.isFinite(number)) return "Debe ser un número";
    if (input.dataset.type === "int" && !Number.isInteger(number)) return "Debe ser un número entero";
    if ("minExclusive" in input.dataset ? number <= min : number < min) {
      return "minExclusive" in input.dataset ? `Debe ser mayor que ${min}` : `Debe ser al menos ${min}`;
    }
    if (number > max) return `Debe ser como máximo ${max}`;
    return null;
  }

  function validate() {
    let first = null;
    for (const input of form.querySelectorAll("input:not(:disabled)")) {
      const error = fieldError(input);
      const message = input.parentElement.querySelector(".campo-error");
      message.textContent = error || "";
      message.hidden = !error;
      if (error) input.setAttribute("aria-invalid", "true");
      else input.removeAttribute("aria-invalid");
      if (error && !first) first = input;
    }
    if (first) first.focus();
    return !first;
  }

  function buildPayload() {
    const payload = {};
    for (const el of form.querySelectorAll("[name]")) {
      payload[el.name] = el.dataset.type === "int" ? parseInt(el.value, 10) : parseFloat(el.value);
    }
    return payload;
  }

  function render(className, ...nodes) {
    result.className = `tarjeta resultado ${className}`;
    resultBody.replaceChildren(...nodes);
  }

  function el(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;
    return node;
  }

  function showError(title, items = []) {
    const nodes = [el("strong", null, title)];
    if (items.length) {
      const list = el("ul");
      items.forEach((item) => list.append(el("li", null, item)));
      nodes.push(list);
    }
    render("err", ...nodes);
  }

  // Número grande con la unidad más pequeña en la misma línea
  function valor(data) {
    const node = el("div", "valor", data.prediccion.toFixed(2));
    if (data.unidad) node.append(el("span", "unidad", data.unidad));
    return node;
  }

  function showResult(data) {
    render("ok",
      el("div", null, "Predicción del modelo"),
      valor(data),
      el("div", "meta", `Modelo ${data.modelo} · ${data.fecha} ${data.hora}`),
      el("div", "meta", `Ejecución ${data.id_ejecucion}`));
  }

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    // Quita el resultado anterior para no mostrarlo junto a una entrada nueva
    render("", ...placeholder);
    if (!validate()) return;

    button.disabled = true;
    try {
      const response = await fetch(form.dataset.endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(buildPayload()),
      });
      const data = await response.json().catch(() => ({}));
      if (response.ok) {
        showResult(data);
      } else if (response.status === 400) {
        showError(data.error || "Parámetro inválido",
          (data.errores || []).map((e) => (e.campo ? `${e.campo}: ${e.detalle}` : e.detalle)));
      } else {
        showError(data.error || `Error del servidor (${response.status})`);
      }
    } catch {
      showError("No se pudo conectar con la API. Verifique que el servidor esté en ejecución.");
    } finally {
      button.disabled = false;
    }
  });
})();
