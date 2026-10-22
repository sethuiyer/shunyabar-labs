/* Theme control: auto -> light -> dark -> auto.
   Runs before paint (deferred via the script tag in <head>) to avoid a flash. */
(function () {
  var KEY = "sbl-theme";
  var modes = ["auto", "light", "dark"];
  var labels = { auto: "Auto", light: "Light", dark: "Dark" };

  function stored() {
    try { return localStorage.getItem(KEY); } catch (e) { return null; }
  }

  function current() {
    var m = stored();
    return modes.indexOf(m) === -1 ? "auto" : m;
  }

  function apply(mode) {
    var root = document.documentElement;
    root.setAttribute("data-theme", mode);
    var btn = document.getElementById("theme-toggle");
    if (btn) {
      var label = btn.querySelector(".label");
      if (label) label.textContent = labels[mode];
      btn.setAttribute("aria-label", "Colour theme: " + labels[mode] + ". Activate to change.");
    }
  }

  apply(current());

  document.addEventListener("DOMContentLoaded", function () {
    var btn = document.getElementById("theme-toggle");
    if (!btn) return;
    btn.addEventListener("click", function () {
      var next = modes[(modes.indexOf(current()) + 1) % modes.length];
      try { localStorage.setItem(KEY, next); } catch (e) {}
      apply(next);
    });
  });
})();
