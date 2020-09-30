"use strict";
var persist;
var cache;
var cn = "hide-side";
var icn = "hide-sidebar-init";
var bcn = "toolbar-1t6TWx";
var scn = "sidebar-2K8pFh";
var vcn = "wrapper-1Rf91z";
var kcn = "key-el";
var mConf = { childList: true };
var g = false;
var pre = '<svg width="24" height="24" viewBox="0 0 24 24"><path fill="currentColor" d="';
var post = '"></path></svg>';
var svgLeft = pre + "M15.41 16.59L10.83 12l4.58-4.59L14 6l-6 6 6 6 1.41-1.41z" + post;
var svgRight = pre + "M8.59 16.59L13.17 12 8.59 7.41 10 6l6 6-6 6-1.41-1.41z" + post;
var btnDiv;
var sideEl;
var dhsb = async () => {
    const toolbars = document.getElementsByClassName(bcn);
    if (toolbars.length !== 1)
        return;
    const toolbar = toolbars[0];
    if (toolbar.classList.contains(icn))
        return;
    const elements = document.getElementsByClassName(scn);
    if (elements.length !== 1)
        return;
    toolbar.classList.add(icn);
    btnDiv = document.createElement("div");
    btnDiv.classList.add("iconWrapper-2OrFZ1", "clickable-3rdHwn", "focusable-1YV_-H");
    btnDiv.setAttribute("role", "button");
    btnDiv.setAttribute("aria-label", "Toggle Sidebar");
    btnDiv.setAttribute("tabindex", "0");
    sideEl = elements[0];
    if (await getCache() === "1")
        hideSide();
    else
        showSide();
    btnDiv.addEventListener("click", () => {
        if (btnDiv.classList.contains(cn))
            showSide();
        else
            hideSide();
    });
    toolbar.appendChild(btnDiv);
    if (!document.body.classList.contains(kcn)) {
        document.addEventListener("keydown", keyEl);
        document.body.classList.add(kcn);
    }
    g = true;
};
var hideSide = () => {
    btnDiv.classList.add(cn);
    btnDiv.innerHTML = svgRight;
    sideEl.style.display = "none";
    setCache("1");
};
var showSide = () => {
    btnDiv.classList.remove(cn);
    btnDiv.innerHTML = svgLeft;
    sideEl.style.display = "";
    setCache("0");
};
var keyEl = (ev) => {
    if (ev.ctrlKey && ev.key === "l") {
        if (btnDiv.classList.contains(cn))
            showSide();
        else
            hideSide();
    }
};
var getServerUrl = () => {
    const paths = location.pathname.split("/");
    if (paths[paths.length - 1] === "")
        paths.pop();
    if (paths.length <= 2)
        return null;
    paths.pop();
    return /^\d+$/.test(paths[paths.length - 1]) ? location.protocol + "//" + location.host + paths.join("/") : null;
};
var getCache = async () => {
    const url = getServerUrl();
    if (url === null)
        return null;
    const response = await cache.match(url);
    return response === undefined ? null : await response.text();
};
var setCache = (val) => {
    const url = getServerUrl();
    if (url !== null)
        cache.put(url, new Response(val));
};
var clearCache = () => cache.keys().then(keys => {
    for (const req of keys)
        cache.delete(req);
});
var checkMut = () => dhsb();
var getMTar = () => {
    const sidebars = document.getElementsByClassName(scn);
    if (sidebars.length !== 1)
        throw new ReferenceError("Invalid window");
    return sidebars[0];
};
var firstRun = async () => {
    while (!g)
        await dhsb();
};
(async () => {
    persist = await navigator.storage.persist();
    if (!persist)
        console.log("%cOh no no save", "color:red;font-size:96px;-webkit-text-stroke:2px yellow;");
    cache = await caches.open(cn);
})();
var mTar = getMTar();
new MutationObserver(checkMut).observe(mTar, mConf);
firstRun();
