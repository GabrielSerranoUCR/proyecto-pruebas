// Envía el formulario de un modelo a su endpoint de la API y muestra el resultado.
(() => {
  const form = document.getElementById("form");
  const result = document.getElementById("result");
  const resultBody = document.getElementById("result-body");
  const placeholder = [...resultBody.childNodes];
  const button = form.querySelector("button[type=submit]");
  // Espera tras la última tecla antes de validar el campo, y temporizador pendiente por campo
  const DEBOUNCE_MS = 400;
  const timers = new WeakMap();
  // En la interfaz móvil (clase "movil", ver base.html) el resultado es una pantalla aparte
  const pagina = form.closest(".modelo");
  const resumen = document.getElementById("resumen");
  const resumenDatos = document.getElementById("resumen-datos");

  // Un "Sí/No" con data-habilita activa otro campo; con "No" ese campo queda en 0
  // (por ejemplo, si no fuma, los cigarrillos por día; si no hay codeudor, su ingreso)
  for (const toggle of form.querySelectorAll("select[data-habilita]")) {
    const target = form.elements[toggle.dataset.habilita];
    const sync = () => {
      target.disabled = toggle.value === "0";
      if (target.disabled) {
        target.value = "0";
        cancelCheck(target);
        showFieldError(target, null);
      }
    };
    toggle.addEventListener("change", () => {
      sync();
      // Al habilitarlo se vacía para obligar a ingresar el valor real
      if (!target.disabled) { target.value = ""; target.focus(); }
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

  function showFieldError(input, error) {
    const message = input.parentElement.querySelector(".campo-error");
    message.textContent = error || "";
    message.hidden = !error;
    if (error) input.setAttribute("aria-invalid", "true");
    else input.removeAttribute("aria-invalid");
    window.pestanas?.marcarErrores();
  }

  function validate() {
    let first = null;
    for (const input of form.querySelectorAll("input:not(:disabled)")) {
      cancelCheck(input);
      const error = fieldError(input);
      showFieldError(input, error);
      if (error && !first) first = input;
    }
    if (first) {
      // En móvil el campo puede estar en otra pestaña: se muestra antes de enfocarlo
      window.pestanas?.mostrar(first.closest("fieldset"));
      first.focus();
    }
    return !first;
  }

  // Validación de un solo campo mientras se escribe (con espera) y al salir de él.
  // Solo se validan los campos que el usuario ya modificó; los demás esperan al envío.
  function cancelCheck(input) {
    clearTimeout(timers.get(input));
    timers.delete(input);
  }

  function checkField(input) {
    cancelCheck(input);
    if (!input.disabled) showFieldError(input, fieldError(input));
  }

  form.addEventListener("input", (event) => {
    const input = event.target;
    if (!input.matches("input")) return;
    input.dataset.touched = "";
    cancelCheck(input);
    timers.set(input, setTimeout(() => checkField(input), DEBOUNCE_MS));
  });

  // focusout, a diferencia de blur, se propaga hasta el formulario
  form.addEventListener("focusout", (event) => {
    const input = event.target;
    if (input.matches("input") && ("touched" in input.dataset || input.hasAttribute("aria-invalid"))) {
      checkField(input);
    }
  });

  function buildPayload() {
    const payload = {};
    for (const el of form.querySelectorAll("[name]:not([data-local])")) {
      if (el.dataset.type === "str") payload[el.name] = el.value;
      else payload[el.name] = el.dataset.type === "int" ? parseInt(el.value, 10) : parseFloat(el.value);
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

  // Número grande con la unidad más pequeña en la misma línea; en clasificación, la etiqueta
  function valor(data) {
    if (data.etiqueta) return el("div", "valor", data.etiqueta);
    const node = el("div", "valor", data.prediccion.toFixed(2));
    if (data.unidad) node.append(el("span", "unidad", data.unidad));
    return node;
  }

  function showResult(data) {
    render("ok",
      el("div", null, "Predicción del modelo"),
      valor(data),
      ...(data.probabilidad !== undefined
        ? [el("div", "meta", `${data.descripcion_probabilidad}: ${(data.probabilidad * 100).toFixed(1)} %`)]
        : []),
      el("div", "meta", `Modelo ${data.modelo} · ${data.fecha} ${data.hora}`),
      el("div", "meta", `Ejecución ${data.id_ejecucion}`));
  }

  // Texto de una leyenda sin su número ("01 Datos personales" -> "Datos personales")
  function tituloSeccion(fieldset) {
    return [...fieldset.querySelector("legend").childNodes]
      .filter((node) => node.nodeType === Node.TEXT_NODE)
      .map((node) => node.textContent).join("").trim();
  }

  // Resumen de lo ingresado, con las mismas etiquetas y opciones que ve el usuario
  function llenarResumen() {
    const nodes = [];
    for (const fieldset of form.querySelectorAll("fieldset")) {
      const lista = el("dl");
      for (const campo of fieldset.querySelectorAll(".campo")) {
        const control = campo.querySelector("[name]");
        const texto = control.tagName === "SELECT"
          ? control.options[control.selectedIndex].textContent
          : control.value;
        const fila = el("div");
        fila.append(el("dt", null, campo.querySelector(":scope > span").textContent), el("dd", null, texto));
        lista.append(fila);
      }
      nodes.push(el("h3", null, tituloSeccion(fieldset)), lista);
    }
    resumenDatos.replaceChildren(...nodes);
    resumen.open = false;
  }

  function mostrarPantallaResultado() {
    llenarResumen();
    if (!document.documentElement.classList.contains("movil")) return;
    pagina.classList.add("viendo-resultado");
    // Una entrada en el historial para que "atrás" del teléfono vuelva al formulario
    history.pushState({ resultado: true }, "");
    window.scrollTo(0, 0);
  }

  function volverAlFormulario() {
    pagina.classList.remove("viendo-resultado");
    window.scrollTo(0, 0);
  }

  window.addEventListener("popstate", volverAlFormulario);
  document.getElementById("recalcular").addEventListener("click", () => {
    if (history.state?.resultado) history.back(); // dispara popstate
    else volverAlFormulario();
  });

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
    mostrarPantallaResultado();
  });
})();
