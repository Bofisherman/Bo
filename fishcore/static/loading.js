window.addEventListener("load", function () {
  document.getElementById("loader").style.display = "none";
});
  document.getElementById("main-content").style.display = "flex";
  document.getElementById("continue").style.display = "flex";

window.addEventListener('load', function () {
  const loader = document.getElementById('loader');
  loader.classList.add('fade-out');
});