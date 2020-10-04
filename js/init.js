"use strict";
var persist = undefined;
var cache = undefined;
var hiddenClassName = "hide-side";
var initClassName = "hide-sidebar-init";
var bannerClassName = "toolbar-1t6TWx";
var serverClassName = "wrapper-1Rf91z";
var sidebarClassName = "sidebar-2K8pFh";
var rightsideClassName = "chat-3bRxxu";
var combinedClassName = "content-98HsJk";
var keyMarkClassName = "key-el";
var sidebarMarkClassName = "sidebar-el";
var buttonClassNames = [
    "iconWrapper-2OrFZ1",
    "clickable-3rdHwn",
    "focusable-1YV_-H",
];
var buttonAttributes = {
    "role": "button",
    "aria-label": "Toggle Sidebar",
    "tabindex": "0",
};
var mutationObConf = { childList: true };
var hiddenWidth = "20px";
var firstRunSuccess = false;
var timeoutId = undefined;
var preSvg = '<svg width="24" height="24" viewBox="0 0 24 24"><path fill="currentColor" d="';
var postSvg = '"></path></svg>';
var svgLeft = preSvg + "M15.41 16.59L10.83 12l4.58-4.59L14 6l-6 6 6 6 1.41-1.41z" + postSvg;
var svgRight = preSvg + "M8.59 16.59L13.17 12 8.59 7.41 10 6l6 6-6 6-1.41-1.41z" + postSvg;
var sidebarDiv = undefined;
var buttonDiv = undefined;
var sidebarOb = undefined;
var rightsideOb = undefined;
var combinedOb = undefined;
function discordHideSidebar() {
    const toolbars = document.getElementsByClassName(bannerClassName);
    if (toolbars.length !== 1)
        return;
    const toolbar = toolbars[0];
    if (toolbar.classList.contains(initClassName))
        return;
    const elements = document.getElementsByClassName(sidebarClassName);
    if (elements.length !== 1)
        return;
    if (buttonDiv === undefined) {
        buttonDiv = document.createElement("div");
        buttonDiv.classList.add(...buttonClassNames);
        for (const [key, value] of Object.entries(buttonAttributes)) {
            buttonDiv.setAttribute(key, value);
        }
    }
    sidebarDiv = elements[0];
    loadConfig();
    buttonDiv.addEventListener("click", toggleSidebar);
    sidebarDiv.style.transition = "width 0.3s ease-in-out";
    toolbar.appendChild(buttonDiv);
    if (!document.body.classList.contains(keyMarkClassName)) {
        document.addEventListener("keydown", keyHandler);
        document.body.classList.add(keyMarkClassName);
    }
    toolbar.classList.add(initClassName);
    firstRunSuccess = true;
}
async function loadConfig() {
    if (await getCache() === "1") {
        hideSide();
    }
    else {
        showSide();
    }
}
function toggleSidebar() {
    if (buttonDiv.classList.contains(hiddenClassName)) {
        showSide();
    }
    else {
        hideSide();
    }
}
function hideSide() {
    buttonDiv.classList.add(hiddenClassName);
    buttonDiv.innerHTML = svgRight;
    sidebarDiv.style.width = hiddenWidth;
    if (!sidebarDiv.classList.contains(sidebarMarkClassName)) {
        sidebarDiv.addEventListener("mouseenter", mouseEnterHandler);
        sidebarDiv.addEventListener("mouseleave", mouseLeaveHandler);
        sidebarDiv.classList.add(sidebarMarkClassName);
    }
    setCache("1");
}
;
function showSide() {
    buttonDiv.classList.remove(hiddenClassName);
    buttonDiv.innerHTML = svgLeft;
    sidebarDiv.style.width = "";
    sidebarDiv.removeEventListener("mouseenter", mouseEnterHandler);
    sidebarDiv.removeEventListener("mouseleave", mouseLeaveHandler);
    sidebarDiv.classList.remove(sidebarMarkClassName);
    setCache("0");
}
;
function mouseEnterHandler(ev) {
    timeoutId = setTimeout(() => {
        ev.target.style.width = "";
    }, 100);
}
function mouseLeaveHandler(ev) {
    clearTimeout(timeoutId);
    timeoutId = undefined;
    ev.target.style.width = hiddenWidth;
}
function keyHandler(ev) {
    if (ev.ctrlKey) {
        if (ev.key === "L") {
            discordHideSidebar();
            return;
        }
        if (ev.key === "l") {
            toggleSidebar();
            return;
        }
        return;
    }
}
;
function getServerUrl() {
    const paths = location.pathname.split("/");
    if (paths[paths.length - 1] === "") {
        paths.pop();
    }
    if (paths.length <= 2)
        return null;
    paths.pop();
    return /^\d+$/.test(paths[paths.length - 1]) ? location.protocol + "//" + location.host + paths.join("/") : null;
}
;
async function getCache() {
    const url = getServerUrl();
    if (url === null)
        return null;
    const response = await cache.match(url);
    return response === undefined ? null : await response.text();
}
;
function setCache(val) {
    const url = getServerUrl();
    if (url !== null) {
        cache.put(url, new Response(val));
    }
}
;
function clearCache() {
    cache.keys().then(keys => {
        for (const req of keys) {
            cache.delete(req);
        }
    });
}
function getMutationObTarget(className, sectionName) {
    const elements = document.getElementsByClassName(className);
    if (elements.length !== 1)
        throw new ReferenceError(`Incorrect window ${sectionName}`);
    return elements[0];
}
function checkSidebarMutation() {
    discordHideSidebar();
    setCombinedMutationCheck();
    setRightsideMutationCheck();
}
function checkRightsideMutation() {
    discordHideSidebar();
}
function setSidebarMutationCheck() {
    const mutationObSidebarTarget = getMutationObTarget(sidebarClassName, "sidebar");
    if (sidebarOb !== undefined) {
        sidebarOb.disconnect();
    }
    sidebarOb = new MutationObserver(checkSidebarMutation);
    sidebarOb.observe(mutationObSidebarTarget, mutationObConf);
}
function setRightsideMutationCheck() {
    const mutationObRightsideTarget = getMutationObTarget(rightsideClassName, "right side");
    if (rightsideOb !== undefined) {
        rightsideOb.disconnect();
    }
    rightsideOb = new MutationObserver(checkRightsideMutation);
    rightsideOb.observe(mutationObRightsideTarget, mutationObConf);
}
function setCombinedMutationCheck() {
    const mutationObCombinedTarget = getMutationObTarget(combinedClassName, "combined");
    if (combinedOb !== undefined) {
        combinedOb.disconnect();
    }
    combinedOb = new MutationObserver(checkRightsideMutation);
    combinedOb.observe(mutationObCombinedTarget, mutationObConf);
}
var sleep = (time) => new Promise((res) => setTimeout(res, time));
(async () => {
    persist = await navigator.storage.persist();
    if (!persist)
        console.log("%cOh no no save", "color:red;font-size:96px;-webkit-text-stroke:2px yellow;");
    cache = await caches.open(hiddenClassName);
    while (!firstRunSuccess) {
        await sleep(1000);
        discordHideSidebar();
    }
    setSidebarMutationCheck();
    setCombinedMutationCheck();
    setRightsideMutationCheck();
})();
