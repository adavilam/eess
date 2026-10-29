(function () {
  "use strict";

  var RUTA_INDICE = "contenido/indice.json";
  var $nav = document.getElementById("nav");
  var $contenido = document.getElementById("contenido");
  var $menu = document.getElementById("menu");
  var titulo = "Ejercicios Espirituales 2026";
  var rutas = [];

  function rutaValida(ruta) {
    return /^contenido\/[^?#]+\.md$/.test(ruta) && ruta.indexOf("..") === -1;
  }

  function rutaActual() {
    var hash = decodeURIComponent(location.hash.replace(/^#\/?/, ""));
    if (rutaValida(hash)) return hash;
    return rutas[0] || null;
  }

  function mostrarError(mensaje) {
    $contenido.textContent = "";
    var p = document.createElement("p");
    p.className = "estado";
    p.textContent = mensaje;
    $contenido.appendChild(p);
  }

  function construirNav(indice) {
    titulo = indice.titulo || titulo;
    $nav.textContent = "";
    indice.secciones.forEach(function (seccion) {
      var h2 = document.createElement("h2");
      h2.textContent = seccion.titulo;
      var ul = document.createElement("ul");
      seccion.items.forEach(function (item) {
        rutas.push(item.ruta);
        var li = document.createElement("li");
        var a = document.createElement("a");
        a.href = "#/" + item.ruta;
        a.textContent = item.titulo;
        a.dataset.ruta = item.ruta;
        li.appendChild(a);
        ul.appendChild(li);
      });
      $nav.appendChild(h2);
      $nav.appendChild(ul);
    });
  }

  function marcarActivo(ruta) {
    Array.prototype.forEach.call($nav.querySelectorAll("a"), function (a) {
      if (a.dataset.ruta === ruta) a.setAttribute("aria-current", "page");
      else a.removeAttribute("aria-current");
    });
  }

  function ajustarEnlaces(ruta) {
    var base = new URL(ruta, document.baseURI);
    var raiz = new URL(".", document.baseURI).pathname;
    Array.prototype.forEach.call($contenido.querySelectorAll("a[href]"), function (a) {
      var href = a.getAttribute("href");
      if (/^(https?:|mailto:)/i.test(href)) {
        a.target = "_blank";
        a.rel = "noopener noreferrer";
        return;
      }
      if (href.charAt(0) === "#") return;
      var destino = new URL(href, base);
      var relativa = decodeURIComponent(destino.pathname.slice(raiz.length));
      if (rutaValida(relativa)) a.setAttribute("href", "#/" + relativa);
    });
  }

  function envolverTablas() {
    Array.prototype.forEach.call($contenido.querySelectorAll("table"), function (t) {
      var caja = document.createElement("div");
      caja.className = "tabla";
      t.parentNode.insertBefore(caja, t);
      caja.appendChild(t);
    });
  }

  function cargar() {
    var ruta = rutaActual();
    if (!ruta) {
      mostrarError("Todavía no hay contenidos publicados.");
      return;
    }
    marcarActivo(ruta);
    fetch(ruta)
      .then(function (r) {
        if (!r.ok) throw new Error("No se encontró " + ruta);
        return r.text();
      })
      .then(function (texto) {
        $contenido.innerHTML = marked.parse(texto, { breaks: true });
        envolverTablas();
        ajustarEnlaces(ruta);
        var h1 = $contenido.querySelector("h1");
        document.title = (h1 ? h1.textContent + " · " : "") + titulo;
        document.body.classList.remove("menu-abierto");
        $menu.setAttribute("aria-expanded", "false");
        window.scrollTo(0, 0);
      })
      .catch(function (e) {
        mostrarError(e.message + ". Si abriste el archivo directamente, usa un servidor local: python -m http.server");
      });
  }

  $menu.addEventListener("click", function () {
    var abierto = document.body.classList.toggle("menu-abierto");
    $menu.setAttribute("aria-expanded", abierto ? "true" : "false");
  });

  window.addEventListener("hashchange", cargar);

  fetch(RUTA_INDICE)
    .then(function (r) {
      if (!r.ok) throw new Error("No se encontró el índice de contenidos");
      return r.json();
    })
    .then(function (indice) {
      construirNav(indice);
      cargar();
    })
    .catch(function (e) {
      mostrarError(e.message + ". Si abriste el archivo directamente, usa un servidor local: python -m http.server");
    });
})();
