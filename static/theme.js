// Day / night toggle. The saved choice wins; otherwise follow the device setting.
(function () {
  var root = document.documentElement;
  var btn = document.getElementById('theme-toggle');
  function label() { btn.textContent = root.dataset.theme === 'dark' ? '☀️ Day' : '🌙 Night'; }
  label();
  btn.addEventListener('click', function () {
    var next = root.dataset.theme === 'dark' ? 'light' : 'dark';
    root.dataset.theme = next;
    try { localStorage.setItem('theme', next); } catch (e) {}
    label();
  });
})();
