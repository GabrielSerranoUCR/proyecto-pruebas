// Reemplaza cada <select> del formulario por una lista desplegable con el estilo de la página.
// El <select> original queda oculto y sigue siendo la fuente del valor (envío y eventos "change").
(() => {
  let abierto = null;

  function crear(select, indice) {
    const campo = select.closest(".campo");
    const etiqueta = campo.querySelector(":scope > span");
    const base = `dd-${indice}`;
    etiqueta.id ||= `${base}-label`;

    const wrapper = document.createElement("div");
    wrapper.className = "dropdown";

    const boton = document.createElement("button");
    boton.type = "button";
    boton.className = "dropdown-boton";
    boton.setAttribute("aria-haspopup", "listbox");
    boton.setAttribute("aria-expanded", "false");
    const valor = document.createElement("span");
    valor.id = `${base}-valor`;
    boton.append(valor);
    boton.setAttribute("aria-labelledby", `${etiqueta.id} ${valor.id}`);

    const lista = document.createElement("ul");
    lista.className = "dropdown-lista";
    lista.id = `${base}-lista`;
    lista.setAttribute("role", "listbox");
    lista.setAttribute("tabindex", "-1");
    lista.setAttribute("aria-labelledby", etiqueta.id);
    lista.hidden = true;
    boton.setAttribute("aria-controls", lista.id);

    const opciones = [...select.options].map((option, i) => {
      const li = document.createElement("li");
      li.id = `${base}-op-${i}`;
      li.setAttribute("role", "option");
      li.dataset.value = option.value;
      li.textContent = option.textContent;
      li.addEventListener("click", (e) => {
        // Evita que el <label> del campo reenvíe el clic al botón y vuelva a abrir la lista
        e.preventDefault();
        cerrar(true);
        elegir(i);
      });
      li.addEventListener("mousemove", () => activar(i));
      lista.append(li);
      return li;
    });

    // El <select> se mueve dentro del contenedor para que el botón sea el control de la etiqueta
    select.before(wrapper);
    wrapper.append(boton, lista, select);
    select.classList.add("visually-hidden");
    select.tabIndex = -1;
    select.setAttribute("aria-hidden", "true");

    let activo = select.selectedIndex;

    function pintar() {
      valor.textContent = select.options[select.selectedIndex].textContent;
      opciones.forEach((li, i) => li.setAttribute("aria-selected", String(i === select.selectedIndex)));
    }

    function activar(i) {
      activo = Math.max(0, Math.min(opciones.length - 1, i));
      opciones.forEach((li, j) => li.classList.toggle("activa", j === activo));
      lista.setAttribute("aria-activedescendant", opciones[activo].id);
      opciones[activo].scrollIntoView({ block: "nearest" });
    }

    // Se llama después de cerrar, para que un manejador de "change" pueda mover el foco
    function elegir(i) {
      if (i !== select.selectedIndex) {
        select.selectedIndex = i;
        select.dispatchEvent(new Event("change", { bubbles: true }));
      }
      pintar();
    }

    function abrir() {
      if (abierto && abierto !== control) abierto.cerrar(false);
      lista.hidden = false;
      // Hacia arriba si la lista quedaría cortada abajo y hay más espacio arriba
      const caja = boton.getBoundingClientRect();
      const abajo = window.innerHeight - caja.bottom;
      lista.classList.toggle("arriba", lista.offsetHeight > abajo && caja.top > abajo);
      boton.setAttribute("aria-expanded", "true");
      activar(select.selectedIndex);
      lista.focus();
      abierto = control;
    }

    function cerrar(devolverFoco) {
      lista.hidden = true;
      boton.setAttribute("aria-expanded", "false");
      if (devolverFoco) boton.focus();
      if (abierto === control) abierto = null;
    }

    boton.addEventListener("click", () => (lista.hidden ? abrir() : cerrar(true)));
    boton.addEventListener("keydown", (e) => {
      if (["ArrowDown", "ArrowUp", "Enter", " "].includes(e.key)) {
        e.preventDefault();
        abrir();
      }
    });

    lista.addEventListener("keydown", (e) => {
      const acciones = {
        ArrowDown: () => activar(activo + 1),
        ArrowUp: () => activar(activo - 1),
        Home: () => activar(0),
        End: () => activar(opciones.length - 1),
        Enter: () => { cerrar(true); elegir(activo); },
        " ": () => { cerrar(true); elegir(activo); },
        Escape: () => cerrar(true),
      };
      if (e.key === "Tab") {
        elegir(activo);
        cerrar(false);
        boton.focus();
        return; // deja que el Tab continúe al siguiente campo
      }
      if (acciones[e.key]) {
        e.preventDefault();
        acciones[e.key]();
      }
    });

    const control = { wrapper, cerrar };
    pintar();
    return control;
  }

  const controles = [...document.querySelectorAll(".campo select")].map(crear);

  document.addEventListener("pointerdown", (e) => {
    if (abierto && !abierto.wrapper.contains(e.target)) abierto.cerrar(false);
  });

  window.dropdowns = controles;
})();
