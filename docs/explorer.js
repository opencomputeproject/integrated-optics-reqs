const comparison = document.querySelector("#comparison");
const home = document.querySelector("#comparison-home");
const surface = document.querySelector("#comparison-surface");
const viewport = document.querySelector("#matrix-viewport");
const matrix = viewport.querySelector(".matrix");
const optionList = document.querySelector("#option-list");
const status = document.querySelector("#table-status");
const scrollHint = document.querySelector("#scroll-hint");
const viewButtons = [...comparison.querySelectorAll("[data-view]")];
const familyButtons = [...surface.querySelectorAll("[data-filter]")];
const optionHeaders = [...matrix.querySelectorAll("th.option")];
const locationHeaders = [...matrix.querySelectorAll("[data-location]")];
const familyCells = [...surface.querySelectorAll("[data-family]")];
const dialog = document.querySelector("#table-dialog");
const expand = document.querySelector("#expand-table");
const close = document.querySelector("#close-table");
const zoomTools = document.querySelector("#zoom-tools");
const zoomOut = document.querySelector("#zoom-out");
const zoomIn = document.querySelector("#zoom-in");
const zoomFit = document.querySelector("#zoom-fit");
const zoomValue = document.querySelector("#zoom-value");
const minZoom = 75;
const maxZoom = 180;

let activeFamily = "all";
let fitWidth = false;
let zoom = 100;

function updateScrollHint() {
  scrollHint.hidden = viewport.hidden || viewport.scrollWidth <= viewport.clientWidth + 1;
}

function setZoom(percent) {
  zoom = Math.max(minZoom, Math.min(maxZoom, Math.floor(percent + 0.0001)));
  matrix.style.setProperty("--scale", zoom / 100);
  zoomValue.value = `${zoom}%`;
  zoomOut.disabled = zoom === minZoom;
  zoomIn.disabled = zoom === maxZoom;
  zoomFit.setAttribute("aria-pressed", fitWidth);
  updateScrollHint();
}

function fitTable() {
  if (!viewport.clientWidth) return;
  const scaledMinimum = Number.parseFloat(getComputedStyle(matrix).minWidth);
  setZoom(Math.min(100, zoom * viewport.clientWidth / scaledMinimum));
}

function filterFamily(family) {
  activeFamily = family;
  for (const button of familyButtons) {
    button.setAttribute("aria-pressed", button.dataset.filter === family);
  }
  for (const cell of familyCells) {
    cell.hidden = family !== "all" && cell.dataset.family !== family;
  }

  let locationIndex = 0;
  for (const header of locationHeaders) {
    const originalSpan = Number(header.dataset.originalSpan);
    const visible = optionHeaders.slice(locationIndex, locationIndex + originalSpan).filter(option => !option.hidden).length;
    header.colSpan = Math.max(1, visible);
    header.hidden = visible === 0;
    locationIndex += originalSpan;
  }
  const count = optionHeaders.filter(option => !option.hidden).length;
  matrix.style.setProperty("--visible-columns", count);
  const familyLabel = family === "all" ? "all" : family.toUpperCase();
  status.textContent = family === "all"
    ? `Showing ${familyLabel} ${count} options`
    : `Showing ${count} ${familyLabel} ${count === 1 ? "option" : "options"}`;
  viewport.scrollTo(0, 0);
  if (fitWidth) fitTable();
  updateScrollHint();
}

function setView(view) {
  const showOptions = view === "options";
  for (const button of viewButtons) {
    button.setAttribute("aria-pressed", button.dataset.view === view);
  }
  viewport.hidden = showOptions;
  zoomTools.hidden = showOptions;
  optionList.hidden = !showOptions;
  if (fitWidth) fitTable();
  updateScrollHint();
}

for (const header of locationHeaders) {
  header.dataset.originalSpan = header.colSpan;
}
for (const button of familyButtons) {
  button.addEventListener("click", () => filterFamily(button.dataset.filter));
}
for (const button of viewButtons) {
  button.addEventListener("click", () => setView(button.dataset.view));
}
for (const [button, delta] of [[zoomOut, -15], [zoomIn, 15]]) {
  button.addEventListener("click", () => {
    fitWidth = false;
    setZoom(zoom + delta);
  });
}
zoomFit.addEventListener("click", () => {
  fitWidth = true;
  viewport.scrollLeft = 0;
  fitTable();
});
new ResizeObserver(() => {
  if (fitWidth) fitTable();
  updateScrollHint();
}).observe(viewport);

expand.addEventListener("click", () => {
  expand.hidden = true;
  close.hidden = false;
  dialog.append(surface);
  dialog.showModal();
  close.focus();
  if (fitWidth) fitTable();
});
close.addEventListener("click", () => dialog.close());

function restoreTable() {
  home.append(surface);
  expand.hidden = false;
  close.hidden = true;
  if (fitWidth) fitTable();
}

dialog.addEventListener("close", () => {
  restoreTable();
  expand.focus({ preventScroll: true });
});
dialog.addEventListener("click", event => {
  if (event.target === dialog) {
    const bounds = dialog.getBoundingClientRect();
    if (event.clientX < bounds.left || event.clientX > bounds.right ||
        event.clientY < bounds.top || event.clientY > bounds.bottom) {
      dialog.close();
    }
  }
});
surface.addEventListener("click", event => {
  if (dialog.open && event.target.closest('a[href^="#note-"]')) {
    dialog.close();
    restoreTable();
  }
});

const illustrations = document.querySelector("#illustrations");
const picker = document.querySelector("#figure-select");
const sideView = document.querySelector("#side-view");
const topView = document.querySelector("#top-view");
const figureNote = document.querySelector("#figure-note");
const placements = {
  "pluggable-pcb": { y: 60, note: "One of two Front Pluggable Optics configurations shown in the draft figure." },
  "pluggable-npc": { y: 278, note: "Front Pluggable Optics with near-package copper (NPC)." },
  "npo-pcb": { y: 498, note: "Near Package Optics mounted on the PCB." },
  "npo-hdi": { y: 715, note: "Near Package Optics mounted on HDI." },
  "cpo": { y: 933, note: "The illustration labels the table’s standard-packaging CPO option CPO-SP." },
  "cpo-ap": { y: 1150, note: "Co-Packaged Optics with advanced packaging." },
};

function setFigure(id, scroll = false) {
  if (!Object.hasOwn(placements, id)) return;
  const placement = placements[id];
  picker.value = id;
  const name = picker.selectedOptions[0].textContent;
  sideView.setAttribute("viewBox", `244 ${placement.y} 539 182`);
  sideView.setAttribute("aria-label", `${name}, side view`);
  topView.setAttribute("viewBox", `816 ${placement.y} 375 182`);
  topView.setAttribute("aria-label", `${name}, top view`);
  figureNote.textContent = placement.note;
  if (scroll) illustrations.scrollIntoView();
}

function figureFromHash() {
  const id = new URLSearchParams(location.hash.slice(1)).get("figure");
  if (id) setFigure(id, true);
}

picker.addEventListener("change", () => {
  setFigure(picker.value);
  history.replaceState(history.state, "", `#figure=${picker.value}`);
});

for (const link of document.querySelectorAll("[data-figure]")) {
  link.addEventListener("click", event => {
    if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
    event.preventDefault();
    const hash = `#figure=${link.dataset.figure}`;
    if (hash !== location.hash) history.pushState(null, "", hash);
    setFigure(link.dataset.figure, true);
  });
}
window.addEventListener("hashchange", figureFromHash);

let printState;
window.addEventListener("beforeprint", () => {
  if (printState) return;
  const collapsedDraft = [...document.querySelectorAll(".draft details:not([open])")];
  printState = { family: activeFamily, collapsedDraft };
  for (const section of collapsedDraft) section.open = true;
  if (dialog.open) {
    dialog.close();
    restoreTable();
  }
  filterFamily("all");
});
window.addEventListener("afterprint", () => {
  if (!printState) return;
  filterFamily(printState.family);
  for (const section of printState.collapsedDraft) section.open = false;
  printState = undefined;
});

setFigure(picker.value);
document.documentElement.classList.add("enhanced");
setZoom(100);
figureFromHash();
