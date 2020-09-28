"use strict";
var bannerClassName = "toolbar-1t6TWx";
var toolbars = document.getElementsByClassName(bannerClassName);
if (toolbars.length === 1) {
    var toolbar = toolbars[0];
    var initName = "hide-sidebar-init";
    if (!toolbar.classList.contains(initName)) {
        var sidebarClassName = "sidebar-2K8pFh";
        var elements = document.getElementsByClassName(sidebarClassName);
        if (elements.length === 1) {
            toolbar.classList.add(initName);
            var el = elements[0];

            // Create toggle
            var div = document.createElement("div");
            div.classList.add("iconWrapper-2OrFZ1", "clickable-3rdHwn", "focusable-1YV_-H");
            div.setAttribute("role", "button");
            div.setAttribute("aria-label", "Toggle Sidebar");
            div.setAttribute("tabindex", "0");
            var svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
            svg.setAttribute("width", "24");
            svg.setAttribute("height", "24");
            svg.setAttribute("viewBox", "0 0 24 24");
            var path = document.createElementNS("http://www.w3.org/2000/svg", "path");
            path.setAttribute("fill", "currentColor");

            // From Material icons
            path.setAttribute("d", "M15.41 16.59L10.83 12l4.58-4.59L14 6l-6 6 6 6 1.41-1.41z");
            svg.appendChild(path);
            div.appendChild(svg);

            // Click event
            div.addEventListener("click", () => {
                if (el.style.display === "none") el.style.display = null;
                else el.style.display = "none";
            });

            toolbar.appendChild(div);
        }
    }
}
