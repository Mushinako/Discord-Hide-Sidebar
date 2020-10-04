"use strict";
// Whether `Cache` allows persistent storage
var persist: boolean | undefined = undefined;
// Use `Cache` because `localStorage` does not exist
var cache: Cache | undefined = undefined;

var hiddenClassName = "hide-side";          // Hidden flag, cache name
var initClassName = "hide-sidebar-init";    // Initiation flag
var bannerClassName = "toolbar-1t6TWx";     // Banner class name
var serverClassName = "wrapper-1Rf91z";     // Server list class name
var sidebarClassName = "sidebar-2K8pFh";    // Sidebar class name
var rightsideClassName = "chat-3bRxxu";     // Right side class name
var combinedClassName = "content-98HsJk";   // Combined div class name

var keyMarkClassName = "key-el";            // Class to mark keyboard event listener enabled
var sidebarMarkClassName = "sidebar-el";    // Class to mark sidebar mouse event listener enabled

var buttonClassNames = [                    // Classes for the button
    "iconWrapper-2OrFZ1",
    "clickable-3rdHwn",
    "focusable-1YV_-H",
];

var buttonAttributes = {                    // Attributes for the button
    "role": "button",
    "aria-label": "Toggle Sidebar",
    "tabindex": "0",
};

var mutationObConf = { childList: true };   // MutationObserver config
var hiddenWidth = "20px";                   // Width for hidden sidebar

var firstRunSuccess = false;                // Whether first run is successful
var timeoutId: number | undefined = undefined;  // ID of MouseEnter setTimeOut

var preSvg = '<svg width="24" height="24" viewBox="0 0 24 24"><path fill="currentColor" d="';
var postSvg = '"></path></svg>';
var svgLeft = preSvg + "M15.41 16.59L10.83 12l4.58-4.59L14 6l-6 6 6 6 1.41-1.41z" + postSvg;
var svgRight = preSvg + "M8.59 16.59L13.17 12 8.59 7.41 10 6l6 6-6 6-1.41-1.41z" + postSvg;

var sidebarDiv: HTMLDivElement | undefined = undefined;     // Sidebar div
var buttonDiv: HTMLDivElement | undefined = undefined;      // The div that contains the button

var sidebarOb: MutationObserver | undefined = undefined;    // Sidebar mutation observer
var rightsideOb: MutationObserver | undefined = undefined;  // Right side mutation observer
var combinedOb: MutationObserver | undefined = undefined;   // Combined div mutation observer

/**
 * Main function to be run for each server
 */
function discordHideSidebar(): void {
    // Check top banner
    const toolbars = document.getElementsByClassName(bannerClassName);
    if (toolbars.length !== 1) return;
    // Check if toolbar is already initialized
    const toolbar = toolbars[0];
    if (toolbar.classList.contains(initClassName)) return;
    // Check if there's anything to hide
    const elements = document.getElementsByClassName(sidebarClassName);
    if (elements.length !== 1) return;
    // Create toggle
    if (buttonDiv === undefined) {
        buttonDiv = document.createElement("div");
        buttonDiv.classList.add(...buttonClassNames);
        for (const [key, value] of Object.entries(buttonAttributes)) {
            buttonDiv.setAttribute(key, value);
        }
    }
    sidebarDiv = <HTMLDivElement>elements[0];
    // Get data from cache
    loadConfig();
    // Click event
    buttonDiv.addEventListener("click", toggleSidebar);
    // Sidebar transition and mouseover
    sidebarDiv.style.transition = "width 0.3s ease-in-out";
    // Append
    toolbar.appendChild(buttonDiv);
    // Keyboard event
    if (!document.body.classList.contains(keyMarkClassName)) {
        document.addEventListener("keydown", keyHandler);
        document.body.classList.add(keyMarkClassName);
    }
    // Mark banner modified
    toolbar.classList.add(initClassName);
    // Set success indicator
    firstRunSuccess = true;
}

/**
 * Load config from cache and act accordingly
 */
async function loadConfig(): Promise<void> {
    if (await getCache() === "1") {
        hideSide();
    } else {
        showSide();
    }
}

/**
 * Toggle sidebar visibility
 */
function toggleSidebar(): void {
    if (buttonDiv!.classList.contains(hiddenClassName)) {
        showSide();
    } else {
        hideSide();
    }
}

/**
 * Hiding the sidebar
 */
function hideSide(): void {
    buttonDiv!.classList.add(hiddenClassName);
    buttonDiv!.innerHTML = svgRight;
    sidebarDiv!.style.width = hiddenWidth;
    if (!sidebarDiv!.classList.contains(sidebarMarkClassName)) {
        sidebarDiv!.addEventListener("mouseenter", mouseEnterHandler);
        sidebarDiv!.addEventListener("mouseleave", mouseLeaveHandler);
        sidebarDiv!.classList.add(sidebarMarkClassName);
    }
    setCache("1");
};

/**
 * Showing the sidebar
 */
function showSide(): void {
    buttonDiv!.classList.remove(hiddenClassName);
    buttonDiv!.innerHTML = svgLeft;
    sidebarDiv!.style.width = "";
    sidebarDiv!.removeEventListener("mouseenter", mouseEnterHandler);
    sidebarDiv!.removeEventListener("mouseleave", mouseLeaveHandler);
    sidebarDiv!.classList.remove(sidebarMarkClassName);
    setCache("0");
};

/**
 * MouseEnter handler
 *   Expands sidebar
 * @param {MouseEvent} ev The `mouseenter` event
 */
function mouseEnterHandler(ev: MouseEvent): void {
    timeoutId = setTimeout((): void => {
        (<HTMLDivElement>ev.target).style.width = "";
    }, 100);
}

/**
 * MouseLeave handler
 *   Folds sidebar
 * @param {MouseEvent} ev The `mouseleave` event
 */
function mouseLeaveHandler(ev: MouseEvent): void {
    clearTimeout(timeoutId);
    timeoutId = undefined;
    (<HTMLDivElement>ev.target).style.width = hiddenWidth;
}

/**
 * Keyboard event handler
 * @param {KeyboardEvent} ev The `keydown` event
 */
function keyHandler(ev: KeyboardEvent): void {
    if (ev.ctrlKey) {
        if (ev.key === "L") {
            // <ctrl> + <shift> + <l>
            discordHideSidebar();
            return;
        }
        if (ev.key === "l") {
            // <ctrl> + <l>
            toggleSidebar();
            return;
        }
        return;
    }
};

/**
 * Get the server URL by chopping of the channel URL
 * @returns {string?} URL if exists, else `null`
 */
function getServerUrl(): string | null {
    const paths = location.pathname.split("/");
    if (paths[paths.length - 1] === "") {
        paths.pop();
    }
    if (paths.length <= 2) return null;
    paths.pop();
    return /^\d+$/.test(paths[paths.length - 1]) ? location.protocol + "//" + location.host + paths.join("/") : null;
};

/**
 * Gets cache value with current server URL as key
 * @returns {Promise<string?>} The stored value if exists, else `null`
 */
async function getCache(): Promise<string | null> {
    const url = getServerUrl();
    if (url === null) return null;
    const response = await cache!.match(url);
    return response === undefined ? null : await response.text();
};

/**
 * Sets cache value with current server URL as key
 * @param {string} val The value to set to
 */
function setCache(val: string): void {
    const url = getServerUrl();
    if (url !== null) {
        cache!.put(url, new Response(val));
    }
};

/**
 * Clears all cache. Only used for debugging
 */
function clearCache(): void {
    cache!.keys().then(keys => {
        for (const req of keys) {
            cache!.delete(req);
        }
    });
}

/**
 * Get element as `MutationObserver` target
 * @param {string} className Class name to get
 * @param {string} sectionName The name of the section. For logging only
 * @returns {Element} The element of interest
 * @throws {ReferenceError} The window does not have the element of interest
 */
function getMutationObTarget(className: string, sectionName: string): Element {
    const elements = document.getElementsByClassName(className);
    if (elements.length !== 1) throw new ReferenceError(`Incorrect window ${sectionName}`);
    return elements[0];
}

/**
 * On sidebar mutation, reapply hack
 *   This occurs when switching servers
 */
function checkSidebarMutation(): void {
    discordHideSidebar();
    setCombinedMutationCheck();
    setRightsideMutationCheck();
}

/**
 * On right side mutation, reapply hack
 *   This occurs when switching channels
 */
function checkRightsideMutation(): void {
    discordHideSidebar();
}

/**
 * Set sidebar mutation observer
 */
function setSidebarMutationCheck(): void {
    // Get observee (sidebar)
    const mutationObSidebarTarget = getMutationObTarget(sidebarClassName, "sidebar");
    // Observe changes
    if (sidebarOb !== undefined) {
        sidebarOb.disconnect();
    }
    sidebarOb = new MutationObserver(checkSidebarMutation);
    sidebarOb.observe(mutationObSidebarTarget, mutationObConf);
}

/**
 * Set right side mutation observer
 */
function setRightsideMutationCheck(): void {
    // Get observee (sidebar)
    const mutationObRightsideTarget = getMutationObTarget(rightsideClassName, "right side");
    // Observe changes
    if (rightsideOb !== undefined) {
        rightsideOb.disconnect();
    }
    rightsideOb = new MutationObserver(checkRightsideMutation);
    rightsideOb.observe(mutationObRightsideTarget, mutationObConf);
}

/**
 * Set combined mutation observer
 */
function setCombinedMutationCheck(): void {
    // Get observee (sidebar)
    const mutationObCombinedTarget = getMutationObTarget(combinedClassName, "combined");
    // Observe changes
    if (combinedOb !== undefined) {
        combinedOb.disconnect();
    }
    combinedOb = new MutationObserver(checkRightsideMutation);
    combinedOb.observe(mutationObCombinedTarget, mutationObConf);
}

/**
 * Pause for certain time
 * @param {number} time Time to pause in milliseconds
 */
var sleep = (time: number): Promise<void> => new Promise((res): number => setTimeout(res, time));

// Initialization
(async (): Promise<void> => {
    // Check if persistent cache is available
    persist = await navigator.storage.persist();
    if (!persist) console.log("%cOh no no save", "color:red;font-size:96px;-webkit-text-stroke:2px yellow;");
    // Make the cache object
    cache = await caches.open(hiddenClassName);
    // First run
    while (!firstRunSuccess) {
        await sleep(1000);
        discordHideSidebar();
    }
    setSidebarMutationCheck();
    setCombinedMutationCheck();
    setRightsideMutationCheck();
})();
