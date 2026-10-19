// Convierte las secciones (fieldset) del formulario en pestañas. Las pestañas solo se ven en
// pantallas angostas (styles.css); en escritorio todas las secciones se muestran a la vez.
(() => {
  const form = document.getElementById("form");
  const lista = form.querySelector(".pestanas");
  if (!lista) return;

  const tabs = [...lista.querySelectorAll("[role=tab]")];
  const panels = tabs.map((tab) => document.getElementById(tab.getAttribute("aria-controls")));
  // Los roles de pestaña solo aplican en la interfaz móvil (clase "movil", ver base.html)
  function aplicarModo() {
    const movil = document.documentElement.classList.contains("movil");
    form.classList.toggle("con-pestanas", movil);
    panels.forEach((panel, i) => {
      if (movil) {
        panel.setAttribute("role", "tabpanel");
        panel.setAttribute("aria-labelledby", tabs[i].id);
      } else {
        panel.removeAttribute("role");
        panel.removeAttribute("aria-labelledby");
      }
    });
  }
  window.addEventListener("cambio-modo", aplicarModo);
  aplicarModo();

  function activar(i, enfocar = false) {
    tabs.forEach((tab, j) => {
      tab.setAttribute("aria-selected", String(i === j));
      tab.tabIndex = i === j ? 0 : -1;
      panels[j].classList.toggle("activa", i === j);
    });
    if (enfocar) tabs[i].focus();
  }

  tabs.forEach((tab, i) => tab.addEventListener("click", () => activar(i)));

  // Flechas, Inicio y Fin recorren las pestañas (patrón de pestañas de WAI-ARIA)
  lista.addEventListener("keydown", (e) => {
    const actual = tabs.indexOf(document.activeElement);
    const destino = {
      ArrowRight: (actual + 1) % tabs.length,
      ArrowLeft: (actual - 1 + tabs.length) % tabs.length,
      Home: 0,
      End: tabs.length - 1,
    }[e.key];
    if (actual === -1 || destino === undefined) return;
    e.preventDefault();
    activar(destino, true);
  });

  activar(0);

  window.pestanas = {
    // Muestra la pestaña de una sección (por ejemplo, la del primer campo inválido)
    mostrar(panel) {
      const i = panels.indexOf(panel);
      if (i !== -1) activar(i);
    },
    // Marca las pestañas que tienen campos inválidos
    marcarErrores() {
      panels.forEach((panel, i) => {
        tabs[i].toggleAttribute("data-error", !!panel.querySelector("[aria-invalid=true]"));
      });
    },
  };
})();
