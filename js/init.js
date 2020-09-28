"use strict";
window.dhsb = () => {
    // Check top banner
    const bannerClassName = "toolbar-1t6TWx";
    const toolbars = document.getElementsByClassName(bannerClassName);
    if (toolbars.length !== 1) return;
    // Check if toolbar is already initialized
    const toolbar = toolbars[0];
    const initName = "hide-sidebar-init";
    if (toolbar.classList.contains(initName)) return;
    // Check if there's anything to hide
    const sidebarClassName = "sidebar-2K8pFh";
    const elements = document.getElementsByClassName(sidebarClassName);
    if (elements.length !== 1) return;
    // Mark banner modified
    toolbar.classList.add(initName);
    // Create toggle
    const div = document.createElement("div");
    div.classList.add("iconWrapper-2OrFZ1", "clickable-3rdHwn", "focusable-1YV_-H");
    div.setAttribute("role", "button");
    div.setAttribute("aria-label", "Toggle Sidebar");
    div.setAttribute("tabindex", "0");
    // Create svg (from Material icons)
    /*
    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.setAttribute("width", "24");
    svg.setAttribute("height", "24");
    svg.setAttribute("viewBox", "0 0 24 24");
    const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
    path.setAttribute("fill", "currentColor");
    path.setAttribute("d", "M15.41 16.59L10.83 12l4.58-4.59L14 6l-6 6 6 6 1.41-1.41z");
    svg.appendChild(path);
    div.appendChild(svg);
    */
    const svgLeft = '<svg width="24" height="24" viewBox="0 0 24 24"><path fill="currentColor" d="M15.41 16.59L10.83 12l4.58-4.59L14 6l-6 6 6 6 1.41-1.41z"></path></svg>';
    div.innerHTML = svgLeft;
    // Click event
    const el = elements[0];
    div.addEventListener("click", () => el.style.display = el.style.display === "none" ? null : "none");
    // Append
    toolbar.appendChild(div);
}