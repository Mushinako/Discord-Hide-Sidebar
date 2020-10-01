"use strict";
var persist: boolean;
// Use `Cache` because `localStorage` does not exist
var cache: Cache;

var cn = "hide-side";           // Hidden flag, cache name
var icn = "hide-sidebar-init";  // Initiation flag
var bcn = "toolbar-1t6TWx";     // Banner class name
var scn = "sidebar-2K8pFh";     // Sidebar class name
var vcn = "wrapper-1Rf91z";     // Server list class name

var kcn = "key-el";     // Keyboard event listener enabled

var mConf = { childList: true };

var g = false;      // Whether first run is successful

var pre = '<svg width="24" height="24" viewBox="0 0 24 24"><path fill="currentColor" d="';
var post = '"></path></svg>';
var svgLeft = pre + "M15.41 16.59L10.83 12l4.58-4.59L14 6l-6 6 6 6 1.41-1.41z" + post;
var svgRight = pre + "M8.59 16.59L13.17 12 8.59 7.41 10 6l6 6-6 6-1.41-1.41z" + post;

var btnDiv: HTMLDivElement;
var sideEl: HTMLElement;

/**
 * Main function to be run for each server
 */
var dhsb = async (): Promise<void> => {
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
    btnDiv = document.createElement("div");
    btnDiv.classList.add("iconWrapper-2OrFZ1", "clickable-3rdHwn", "focusable-1YV_-H");
    btnDiv.setAttribute("role", "button");
    btnDiv.setAttribute("aria-label", "Toggle Sidebar");
    btnDiv.setAttribute("tabindex", "0");
    // Get data from cache
    sideEl = <HTMLElement>elements[0];
    if (await getCache() === "1") hideSide();
    else showSide();
    // Click event
    btnDiv.addEventListener("click", () => {
        if (btnDiv.classList.contains(cn)) showSide();
        else hideSide();
    });
    // Append
    toolbar.appendChild(btnDiv);
    // Keyboard event
    if (!document.body.classList.contains(kcn)) {
        document.addEventListener("keydown", keyEl);
        document.body.classList.add(kcn);
    }
    // Set success indicator
    g = true;
}

/**
 * Hiding the sidebar
 */
var hideSide = (): void => {
    btnDiv.classList.add(cn);
    btnDiv.innerHTML = svgRight;
    sideEl.style.display = "none";
    setCache("1");
};

/**
 * Showing the sidebar
 */
var showSide = (): void => {
    btnDiv.classList.remove(cn);
    btnDiv.innerHTML = svgLeft;
    sideEl.style.display = "";
    setCache("0");
};

/**
 * Keyboard event handler
 * @param {KeyboardEvent} ev The `keydown` event
 */
var keyEl = (ev: KeyboardEvent): void => {
    if (ev.ctrlKey) {
        if (ev.key === "L") {
            dhsb();
            return;
        }
        if (ev.key === "l") {
            if (btnDiv.classList.contains(cn)) showSide();
            else hideSide();
            return;
        }
        return;
    }
};

/**
 * Get the server URL by chopping of the channel URL
 * @returns {string?} URL if exists, else `null`
 */
var getServerUrl = (): string | null => {
    const paths = location.pathname.split("/");
    if (paths[paths.length - 1] === "") paths.pop();
    if (paths.length <= 2) return null;
    paths.pop();
    return /^\d+$/.test(paths[paths.length - 1]) ? location.protocol + "//" + location.host + paths.join("/") : null;
};

/**
 * Gets cache value with current server URL as key
 * @returns {Promise<string?>} The stored value if exists, else `null`
 */
var getCache = async (): Promise<string | null> => {
    const url = getServerUrl();
    if (url === null) return null;
    const response = await cache.match(url);
    return response === undefined ? null : await response.text();
};

/**
 * Sets cache value with current server URL as key
 * @param {string} val The value to set to
 */
var setCache = (val: string): void => {
    const url = getServerUrl();
    if (url !== null) cache.put(url, new Response(val));
};

/**
 * Clears all cache. Only used for debugging
 */
var clearCache = (): Promise<void> => cache.keys().then(keys => {
    for (const req of keys) cache.delete(req);
});

/**
 * On mutation, call `dhsb`
 */
var checkMut = (): Promise<void> => dhsb();

/**
 * Get sidebar as `MutationObserver` target
 * @returns {Element} The sidebar element
 * @throws {ReferenceError} The window is not the one we want
 */
var getMTar = (): Element => {
    const sidebars = document.getElementsByClassName(scn);
    if (sidebars.length !== 1) throw new ReferenceError("Invalid window");
    return sidebars[0];
};

/**
 * First run, has to be `async` function because the use of `await`
 */
var firstRun = async (): Promise<void> => { while (!g) await dhsb(); };

// Caching
(async (): Promise<void> => {
    // Check if persistent cache is available
    persist = await navigator.storage.persist();
    if (!persist) console.log("%cOh no no save", "color:red;font-size:96px;-webkit-text-stroke:2px yellow;");
    // Make the cache object
    cache = await caches.open(cn);
})();

// Get observee (sidebar)
var mTar = getMTar();

// Observe changes
new MutationObserver(checkMut).observe(mTar, mConf);

// First run
firstRun();
