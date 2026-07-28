/******************************************************************************
 * AulaMind Enterprise 3.0
 * static/js/guides.js
 * Módulo: Guías de Apoyo IA
 ******************************************************************************/

document.addEventListener("DOMContentLoaded", () => {
    "use strict";

    const CONFIG = window.GUIDE_CONFIG || {};
    const CSRF_TOKEN = document.getElementById("csrf_token")?.value || "";

    const URLS = {
        generate: CONFIG.generateUrl,
        history: CONFIG.historyUrl,
        document(id) { return `/guides/${id}`; },
        exportLinks(id) { return `/guides/export-links/${id}`; }
    };

    const form = document.getElementById("guideForm");
    const resultSection = document.getElementById("resultSection");
    const result = document.getElementById("guideResult");
    const historyBody = document.getElementById("historyBody");
    const loadingModal = document.getElementById("loadingModal");
    const toast = document.getElementById("toast");

    let currentDocument = null;
    let exportInfo = { word: null, pdf: null };

    function showLoading() {
        loadingModal?.classList.add("active");
    }

    function hideLoading() {
        loadingModal?.classList.remove("active");
    }

    function showToast(message, type = "success") {
        if (!toast) { console.log(message); return; }
        toast.textContent = message;
        toast.className = "toast " + type;
        setTimeout(() => toast.classList.add("show"), 10);
        setTimeout(() => toast.classList.remove("show"), 3000);
    }

    function showResult(content) {
        if (result) result.textContent = content || "";
        if (resultSection) {
            resultSection.style.display = "block";
            resultSection.scrollIntoView({ behavior: "smooth", block: "start" });
        }
    }

    function clearResult() {
        currentDocument = null;
        exportInfo.word = null;
        exportInfo.pdf = null;
        if (result) result.textContent = "";
    }

    async function request(url, options = {}) {
        const defaultHeaders = {
            "Content-Type": "application/json",
            "X-CSRFToken": CSRF_TOKEN
        };

        const response = await fetch(url, {
            ...options,
            headers: { ...defaultHeaders, ...options.headers }
        });

        const data = await response.json();
        if (!response.ok || data.success === false) {
            throw new Error(data.error || "Error del servidor.");
        }
        return data;
    }

    async function generateGuide() {
        const payload = Object.fromEntries(new FormData(form).entries());
        showLoading();
        try {
            const response = await request(URLS.generate, {
                method: "POST",
                body: JSON.stringify(payload)
            });
            currentDocument = response.document_id;
            showResult(response.content);
            showToast("Guía generada correctamente.");
            await loadExportLinks();
            await loadHistory();
        } catch (error) {
            showResult("ERROR\n\n" + error.message);
            showToast(error.message, "error");
        } finally {
            hideLoading();
        }
    }

    async function loadHistory() {
        if (!historyBody) return;
        historyBody.innerHTML = '<tr><td colspan="4" class="empty-state">Cargando...</td></tr>';
        try {
            const response = await request(URLS.history);
            if (!response.items || response.items.length === 0) {
                historyBody.innerHTML = '<tr><td colspan="4" class="empty-state">No existen guías.</td></tr>';
                return;
            }
            historyBody.innerHTML = "";
            response.items.forEach(doc => {
                const created = doc.created_at ? new Date(doc.created_at).toLocaleString() : "";
                const tr = document.createElement("tr");
                tr.innerHTML = `
                    <td>${created}</td>
                    <td>${doc.course || ""}</td>
                    <td>${doc.subject || ""}</td>
                    <td>
                        <button class="btn-action btn-open" data-id="${doc.id}">Abrir</button>
                        <button class="btn-action btn-word" data-id="${doc.id}">Word</button>
                        <button class="btn-action btn-pdf" data-id="${doc.id}">PDF</button>
                        <button class="btn-action delete btn-delete" data-id="${doc.id}">Eliminar</button>
                    </td>
                `;
                historyBody.appendChild(tr);
            });
        } catch (error) {
            console.error(error);
            historyBody.innerHTML = '<tr><td colspan="4" class="empty-state">Error cargando historial</td></tr>';
        }
    }

    async function openDocument(documentId) {
        showLoading();
        try {
            const response = await request(URLS.document(documentId));
            currentDocument = documentId;
            showResult(response.document.content);
            await loadExportLinks();
            showToast("Documento cargado.");
        } catch (error) {
            showToast(error.message, "error");
        } finally {
            hideLoading();
        }
    }

    async function deleteDocument(documentId) {
        if (!confirm("¿Desea eliminar esta guía?")) return;
        showLoading();
        try {
            await request(URLS.document(documentId), { method: "DELETE" });
            if (currentDocument === documentId) clearResult();
            await loadHistory();
            showToast("Guía eliminada.");
        } catch (error) {
            showToast(error.message, "error");
        } finally {
            hideLoading();
        }
    }

    async function loadExportLinks() {
        if (!currentDocument) return;
        try {
            const response = await request(URLS.exportLinks(currentDocument));
            exportInfo.word = response.word;
            exportInfo.pdf = response.pdf;
        } catch (error) {
            console.error(error);
        }
    }

    async function copyGuide() {
        if (!result) return;
        const text = result.textContent.trim();
        if (!text) { showToast("No existe contenido para copiar.", "error"); return; }
        try {
            await navigator.clipboard.writeText(text);
            showToast("Guía copiada al portapapeles.");
        } catch {
            showToast("No fue posible copiar.", "error");
        }
    }

    function exportWord() {
        if (!exportInfo.word) { showToast("Debe generar o abrir una guía.", "error"); return; }
        window.location.href = exportInfo.word;
    }

    function exportPdf() {
        if (!exportInfo.pdf) { showToast("Debe generar o abrir una guía.", "error"); return; }
        window.location.href = exportInfo.pdf;
    }

    // Eventos
    form?.addEventListener("submit", (e) => { e.preventDefault(); generateGuide(); });
    document.getElementById("copyGuide")?.addEventListener("click", copyGuide);
    document.getElementById("downloadWord")?.addEventListener("click", exportWord);
    document.getElementById("downloadPdf")?.addEventListener("click", exportPdf);

    historyBody?.addEventListener("click", async (e) => {
        const btn = e.target.closest("button");
        if (!btn) return;
        const id = parseInt(btn.dataset.id);
        if (btn.classList.contains("btn-open")) { await openDocument(id); return; }
        if (btn.classList.contains("btn-delete")) { await deleteDocument(id); return; }
        if (btn.classList.contains("btn-word")) { currentDocument = id; await loadExportLinks(); exportWord(); return; }
        if (btn.classList.contains("btn-pdf")) { currentDocument = id; await loadExportLinks(); exportPdf(); return; }
    });

    // Inicialización
    (async () => { try { await loadHistory(); } catch (e) { console.error(e); } })();
});