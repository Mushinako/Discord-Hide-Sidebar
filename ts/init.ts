"use strict";

// Make `HTMLCollectionOf` iterable
interface HTMLCollectionOf<T extends Element> {
    [Symbol.iterator](): Iterator<T>;
}

// Whether `Cache` allows persistent storage
var persist: boolean | undefined = undefined;
// Use `Cache` because `localStorage` does not exist
var cache: Cache | undefined = undefined;

var meServerName = "@me";

var hiddenClassName = "hide-side";          // Hidden flag, cache name
var initClassName = "hide-sidebar-init";    // Initiation flag
var bannerClassName = "toolbar-1t6TWx";     // Banner class name
var serverClassName = "wrapper-1Rf91z";     // Server list class name
var sidebarClassName = "sidebar-2K8pFh";    // Sidebar class name
var rightsideClassName = "chat-3bRxxu";     // Right side class name
var combinedClassName = "content-98HsJk";   // Combined div class name
var scrollerClassName = "scroller-2LSbBU";  // Scroller div class name
var jumpButtonClassName = "barButtonAlt-mYL1lj";    // Button for "jump to present" class name

var keyMarkClassName = "key-el";            // Class to mark keyboard event listener enabled
var sidebarMarkClassName = "sidebar-el";    // Class to mark sidebar mouse event listener enabled

var jumpToPresentText = "Jump To Present";  // Text on "Jump to Present" button

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
var hiddenHeight = "calc(100vh - 22px)";    // Height for hidden sidebar, has to specify due to absolute position

var firstRunSuccess = false;                // Whether first run is successful
var timeoutId: number | undefined = undefined;  // ID of MouseEnter setTimeOut
var processingFlag = false;                 // Whether an action is being processed

var preSvg = '<svg width="24" height="24" viewBox="0 0 24 24"><path fill="currentColor" d="';
var postSvg = '"></path></svg>';
var svgLeft = preSvg + "M15.41 16.59L10.83 12l4.58-4.59L14 6l-6 6 6 6 1.41-1.41z" + postSvg;
var svgRight = preSvg + "M8.59 16.59L13.17 12 8.59 7.41 10 6l6 6-6 6-1.41-1.41z" + postSvg;

var sidebarDiv: HTMLDivElement | undefined = undefined;     // Sidebar div
var buttonDiv: HTMLDivElement | undefined = undefined;      // The div that contains the button

var sidebarOb: MutationObserver | undefined = undefined;    // Sidebar mutation observer
var rightsideOb: MutationObserver | undefined = undefined;  // Right side mutation observer
var combinedOb: MutationObserver | undefined = undefined;   // Combined div mutation observer

var animTime = 0.2;                 // Animation time in seconds
var animTimeMs = animTime * 1000;   // Animation time in milliseconds

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
    sidebarDiv.style.transition = `width ${animTime}s ease-in-out`;
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
    if (processingFlag === true) return;
    processingFlag = true;
    if (await getCache() === "1") {
        hideSide();
    } else {
        showSide();
    }
    processingFlag = false;
}

/**
 * Toggle sidebar visibility
 */
function toggleSidebar(): void {
    if (processingFlag === true) return;
    processingFlag = true;
    if (buttonDiv!.classList.contains(hiddenClassName)) {
        showSide();
    } else {
        hideSide();
    }
    processingFlag = false;
}

/**
 * Hiding the sidebar
 */
function hideSide(): void {
    setCache("1");
    if (buttonDiv === undefined || sidebarDiv === undefined) return;
    buttonDiv.classList.add(hiddenClassName);
    buttonDiv.innerHTML = svgRight;
    sidebarDiv.style.width = hiddenWidth;
    sidebarDiv.style.height = hiddenHeight;
    if (sidebarDiv.classList.contains(sidebarMarkClassName)) return;
    const newSidebarDiv = document.createElement("div");
    newSidebarDiv.style.width = hiddenWidth;
    const baseDiv = <HTMLDivElement>sidebarDiv.parentElement!.parentElement!;
    const newContentDiv = document.createElement("div");
    setTimeout((): void => {
        sidebarDiv!.parentElement!.insertBefore(newSidebarDiv, sidebarDiv!);
        newContentDiv.appendChild(sidebarDiv!);
        newContentDiv.style.position = "absolute";
        newContentDiv.style.zIndex = "2";
        baseDiv.appendChild(newContentDiv);
        sidebarDiv!.addEventListener("mouseenter", mouseEnterHandler);
        sidebarDiv!.addEventListener("mouseleave", mouseLeaveHandler);
        sidebarDiv!.classList.add(sidebarMarkClassName);
    }, animTimeMs);
};

/**
 * Showing the sidebar
 * @throws {ReferenceError} The window does not have the element of interest
 */
function showSide(): void {
    setCache("0");
    if (buttonDiv === undefined || sidebarDiv === undefined) return;
    buttonDiv.classList.remove(hiddenClassName);
    buttonDiv.innerHTML = svgLeft;
    if (!sidebarDiv.classList.contains(sidebarMarkClassName)) {
        sidebarDiv.style.width = "";
        return;
    }
    const baseDiv = <HTMLDivElement>sidebarDiv.parentElement!.parentElement!;
    const contentDiv = <HTMLDivElement>baseDiv.children[baseDiv.childElementCount - 2];
    if (contentDiv.childElementCount !== 2) throw new ReferenceError("Invalid showSide parent");
    contentDiv.removeChild(contentDiv.firstElementChild!);
    contentDiv.insertBefore(sidebarDiv!, contentDiv.firstElementChild);
    setTimeout((): void => {
        sidebarDiv!.style.width = "";
        sidebarDiv!.style.height = "";
    }, 100);
    sidebarDiv!.removeEventListener("mouseenter", mouseEnterHandler);
    sidebarDiv!.removeEventListener("mouseleave", mouseLeaveHandler);
    sidebarDiv!.classList.remove(sidebarMarkClassName);
    if (baseDiv.childElementCount > 1) {
        baseDiv.removeChild(baseDiv.lastElementChild!);
    }
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
        if (ev.key === "w") {
            // <ctrl> + <w>
            // Keyboard close window
            window.close();
            return;
        }
        return;
    }
    if (ev.key === "PageDown" && ev.altKey) {
        // <alt> (+ <shift>) + <PgDn>
        scrollToBottom();
        return;
    }
    return;
};

/**
 * Scrolls chat div to bottom
 * @throws {ReferenceError} The window does not have the element of interest
 */
function scrollToBottom(): void {
    // Check whether "Jump To Present" button is present
    const jumpButtons = document.getElementsByClassName(jumpButtonClassName);
    for (const jumpButton of jumpButtons) {
        const text = (<Text>jumpButton.firstChild).textContent!.trim();
        if (text === jumpToPresentText) {
            // "Jump To Present" button
            (<HTMLButtonElement>jumpButton).click();
            return;
        }
    }
    // No "Jump To Present" button
    const scrollerDivs = document.getElementsByClassName(scrollerClassName);
    if (scrollerDivs.length !== 1) throw ReferenceError("Invalid scroller div");
    const chatDiv = scrollerDivs[0];
    const scrollOptions = <ScrollToOptions>{
        top: chatDiv.scrollHeight,
        left: chatDiv.scrollLeft,
        behavior: "smooth",
    };
    chatDiv.scrollTo(scrollOptions);
}

/**
 * Get the server URL by chopping of the channel URL
 * @returns {string?} URL if exists, else `null`
 */
function getServerUrl(): string | null {
    const paths = location.pathname.split("/");
    if (paths.length < 3) return null;
    return paths[2] === meServerName || /^\d+$/.test(paths[2]) ? "/" + paths[2] : null;
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
    try {
        var mutationObRightsideTarget = getMutationObTarget(rightsideClassName, "right side");
    } catch {
        return;
    }
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
