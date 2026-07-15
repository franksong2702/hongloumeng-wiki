async function renderMermaidDiagrams() {
  if (!window.mermaid) return;

  const diagrams = document.querySelectorAll(".mermaid:not([data-processed='true'])");
  if (!diagrams.length) return;

  window.mermaid.initialize({
    startOnLoad: false,
    securityLevel: "loose",
    theme: document.body.getAttribute("data-md-color-scheme") === "slate" ? "dark" : "default",
  });

  try {
    await window.mermaid.run({ nodes: Array.from(diagrams) });
  } catch (error) {
    console.error("Mermaid rendering failed", error);
  }
}

if (typeof document$ !== "undefined") {
  document$.subscribe(renderMermaidDiagrams);
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", renderMermaidDiagrams);
} else {
  renderMermaidDiagrams();
}
