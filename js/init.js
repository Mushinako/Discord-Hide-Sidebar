"use strict";
var persist;
var cache;

var cn = "hide-side";           // Hidden flag, cache name
var icn = "hide-sidebar-init";  // Initiation flag
var bcn = "toolbar-1t6TWx";     // Banner class name
var scn = "sidebar-2K8pFh";     // Sidebar class name

var pre = '<svg width="24" height="24" viewBox="0 0 24 24"><path fill="currentColor" d="';
var post = '"></path></svg>';
var svgLeft = pre + "M15.41 16.59L10.83 12l4.58-4.59L14 6l-6 6 6 6 1.41-1.41z" + post;
var svgRight = pre + "M8.59 16.59L13.17 12 8.59 7.41 10 6l6 6-6 6-1.41-1.41z" + post;

/**
 * Main function to be run for each server
 */
var dhsb = async () => {
    // Check top banner
    const toolbars = document.getElementsByClassName(bcn);
    if (toolbars.length !== 1) return;
    // Check if toolbar is already initialized
    const toolbar = toolbars[0];
    if (toolbar.classList.contains(icn)) return;
    // Check if there's anything to hide
    const elements = document.getElementsByClassName(scn);
    if (elements.length !== 1) return;
    // Mark banner modified
    toolbar.classList.add(icn);
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
    // Get data from cache
    const el = elements[0];
    if (await getCache() === "1") hide(div, el);
    else show(div, el);
    // Click event
    div.addEventListener("click", () => {
        if (div.classList.contains(cn)) show(div, el);
        else hide(div, el);
    });
    // Append
    toolbar.appendChild(div);
}

/**
 * Hiding the sidebar
 * @param {HTMLDivElement} div The div for the button to be in
 * @param {HTMLElement}    el  The element that contains the sidebar
 */
var hide = (div, el) => {
    div.classList.add(cn);
    div.innerHTML = svgRight;
    el.style.display = "none";
    setCache("1");
};

/**
 * Showing the sidebar
 * @param {HTMLDivElement} div The div for the button to be in
 * @param {HTMLElement}    el  The element that contains the sidebar
 */
var show = (div, el) => {
    div.classList.remove(cn);
    div.innerHTML = svgLeft;
    el.style.display = null;
    setCache("0");
};

/**
 * Get the server URL by chopping of the channel URL
 * @returns {string?} URL if exists, else `null`
 */
var getServerUrl = () => {
    const paths = location.pathname.split("/");
    if (paths[paths.length - 1] === "") paths.pop();
    if (paths.length <= 2) return null;
    paths.pop();
    return /^\d+$/.test(paths[paths.length - 1]) ? location.protocol + "//" + location.host + paths.join("/") : null;
};

/**
 * Gets cache value with current server URL as key
 * @returns {Promise<string>?} The stored value if exists, else `null`
 */
var getCache = async () => {
    const url = getServerUrl();
    if (url === null) return null;
    const response = await cache.match(url);
    return response === undefined ? null : await response.text();
};

/**
 * Sets cache value with current server URL as key
 * @param {string} val The value to set to
 */
var setCache = val => {
    const url = getServerUrl();
    if (url !== null) cache.put(url, new Response(val));
};

/**
 * Clears all cache. Only used for debugging
 */
var clearCache = () => cache.keys().then(keys => { for (const req of keys) cache.delete(req) });

(async () => {
    // Check if persistent cache is available
    persist = await navigator.storage.persist();
    if (!persist) console.log("%cOh no no save", "color:red;font-size:96px;-webkit-text-stroke:2px yellow;");
    // Make the cache object
    cache = await caches.open(cn);
})();
