"use strict";

document.querySelectorAll("[data-print]").forEach((button) => {
  button.addEventListener("click", () => window.print());
});

const addLine = document.querySelector("[data-add-purchase-line]");
if (addLine) {
  addLine.addEventListener("click", () => {
    const total = document.querySelector("#id_lines-TOTAL_FORMS");
    const template = document.querySelector("#purchase-empty-row");
    const body = document.querySelector("#purchase-lines");
    if (!total || !template || !body) return;
    const index = Number(total.value);
    if (!Number.isInteger(index) || index >= 50) return;
    const fragment = template.content.cloneNode(true);
    fragment.querySelectorAll("[name], [id], [for]").forEach((element) => {
      for (const attr of ["name", "id", "for"]) {
        const value = element.getAttribute(attr);
        if (value) element.setAttribute(attr, value.replaceAll("__prefix__", String(index)));
      }
    });
    body.appendChild(fragment);
    total.value = String(index + 1);
    if (index + 1 >= 50) addLine.disabled = true;
    body.lastElementChild?.querySelector("select")?.focus();
  });
}
