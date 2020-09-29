"use strict";
var persist;
var cache;
var cn = "hide-side";
var icn = "hide-sidebar-init";
var bcn = "toolbar-1t6TWx";
var scn = "sidebar-2K8pFh";
var vcn = "wrapper-1Rf91z";
var mConf = { childList: true };
var g = false;
var pre = '<svg width="24" height="24" viewBox="0 0 24 24"><path fill="currentColor" d="';
var post = '"></path></svg>';
var svgLeft = pre + "M15.41 16.59L10.83 12l4.58-4.59L14 6l-6 6 6 6 1.41-1.41z" + post;
var svgRight = pre + "M8.59 16.59L13.17 12 8.59 7.41 10 6l6 6-6 6-1.41-1.41z" + post;
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
    const div = document.createElement("div");
    div.classList.add("iconWrapper-2OrFZ1", "clickable-3rdHwn", "focusable-1YV_-H");
    div.setAttribute("role", "button");
    div.setAttribute("aria-label", "Toggle Sidebar");
    div.setAttribute("tabindex", "0");
    const el = elements[0];
    if (await getCache() === "1")
        hide(div, el);
    else
        show(div, el);
    div.addEventListener("click", () => {
        if (div.classList.contains(cn))
            show(div, el);
        else
            hide(div, el);
    });
    toolbar.appendChild(div);
    g = true;
};
var hide = (div, el) => {
    div.classList.add(cn);
    div.innerHTML = svgRight;
    el.style.display = "none";
    setCache("1");
};
var show = (div, el) => {
    div.classList.remove(cn);
    div.innerHTML = svgLeft;
    el.style.display = "";
    setCache("0");
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
while (!mTar) {
    const sidebars = document.getElementsByClassName(scn);
    if (sidebars.length !== 1)
        continue;
    mTar = sidebars[0];
}
new MutationObserver(checkMut).observe(mTar, mConf);
firstRun();
