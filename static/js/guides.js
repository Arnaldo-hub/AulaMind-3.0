/******************************************************************************
 * AulaMind Enterprise 3.0 - Guías de Apoyo IA
 ******************************************************************************/

document.addEventListener("DOMContentLoaded", () => {
    "use strict";

    const CONFIG = window.GUIDE_CONFIG || {};
    const CSRF_TOKEN = document.getElementById("csrf_token")?.value || "";
    const API_BASE = "/planning/api/curriculum";

    const URLS = {
        generate: CONFIG.generateUrl,
        history: CONFIG.historyUrl,
        document(id) { return /guides/; },
        exportLinks(id) { return /guides/export-links/; }
    };

    const form = document.getElementById("guideForm");
    const resultSection = document.getElementById("resultSection");
    const result = document.getElementById("guideResult");
    const historyBody = document.getElementById("historyBody");
    const loadingModal = document.getElementById("loadingModal");
    const toast = document.getElementById("toast");

    let currentDocument = null;
    let exportInfo = { word: null, pdf: null };

    function showLoading() { loadingModal?.classList.add("active"); }
    function hideLoading() { loadingModal?.classList.remove("active"); }

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
        const defaultHeaders = { "Content-Type": "application/json", "X-CSRFToken": CSRF_TOKEN };
        const response = await fetch(url, { ...options, headers: { ...defaultHeaders, ...options.headers } });
        const data = await response.json();
        if (!response.ok || data.success === false) throw new Error(data.error || "Error del servidor.");
        return data;
    }

    /**********************************************************************
     * CARGA EN CASCADA DEL CURRÍCULO
     **********************************************************************/

    async function populateSelect(url, selectId, placeholder) {
        const select = document.getElementById(selectId);
        if (!select) return;
        try {
            const response = await fetch(url);
            const data = await response.json();
            if (!data.success) throw new Error(data.message || "Error API");

            select.innerHTML = <option value=""></option>;

            const key = selectId === "curso" ? "courses"
                      : selectId === "asignatura" ? "subjects"
                      : selectId === "unidad" ? "units"
                      : "objectives";

            const items = data[key];
            if (!items || items.length === 0) {
                select.innerHTML = <option value="">No hay datos disponibles</option>;
                select.disabled = true;
                return;
            }

            items.forEach(item => {
                const opt = document.createElement("option");
                if (typeof item === "object" && item !== null) {
                    if (item.code) {
                        opt.value = item.code;
                        opt.textContent = ${item.code} - ;
                        opt.title = item.description || item.code;
                    } else if (item.id) {
                        opt.value = item.id;
                        opt.textContent = item.name || item.id;
                    } else if (item.name) {
                        opt.value = item.name;
                        opt.textContent = item.name;
                    } else {
                        opt.value = JSON.stringify(item);
                        opt.textContent = item.name || item.id || JSON.stringify(item);
                    }
                } else {
                    opt.value = item;
                    opt.textContent = item;
                }
                select.appendChild(opt);
            });
            select.disabled = false;
        } catch (err) {
            console.error(Error cargando :, err);
            select.innerHTML = <option value="">Error cargando datos</option>;
            select.disabled = true;
        }
    }

    // Cargar cursos
    (async () => { await populateSelect(${API_BASE}/courses, "curso", "Selecciona un curso..."); })();

    document.getElementById("curso")?.addEventListener("change", async function () {
        const course = this.value;
        const asignatura = document.getElementById("asignatura");
        const unidad = document.getElementById("unidad");
        const objetivo = document.getElementById("objetivo");

        asignatura.innerHTML = <option value="">Selecciona una asignatura...</option>;
        unidad.innerHTML = <option value="">Selecciona una unidad...</option>;
        objetivo.innerHTML = <option value="">Selecciona un OA...</option>;
        asignatura.disabled = !course;
        unidad.disabled = true;
        objetivo.disabled = true;

        if (!course) return;
        await populateSelect(${API_BASE}/subjects/, "asignatura", "Selecciona una asignatura...");
    });

    document.getElementById("asignatura")?.addEventListener("change", async function () {
        const course = document.getElementById("curso").value;
        const subject = this.value;
        const unidad = document.getElementById("unidad");
        const objetivo = document.getElementById("objetivo");

        unidad.innerHTML = <option value="">Selecciona una unidad...</option>;
        objetivo.innerHTML = <option value="">Selecciona un OA...</option>;
        unidad.disabled = !subject;
        objetivo.disabled = true;

        if (!subject) return;
        await populateSelect(${API_BASE}/units//, "unidad", "Selecciona una unidad...");
    });

    document.getElementById("unidad")?.addEventListener("change", async function () {
        const course = document.getElementById("curso").value;
        const subject = document.getElementById("asignatura").value;
        const unit = this.value;
        const objetivo = document.getElementById("objetivo");

        objetivo.innerHTML = <option value="">Selecciona un OA...</option>;
        objetivo.disabled = !unit;

        if (!unit) return;
        await populateSelect(${API_BASE}/objectives///, "objetivo", "Selecciona un OA...");
    });

    /**********************************************************************
     * GENERAR GUÍA
     **********************************************************************/

    async function generateGuide() {
        const payload = Object.fromEntries(new FormData(form).entries());
        showLoading();
        try {
            const response = await request(URLS.generate, { method: "POST", body: JSON.stringify(payload) });
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

    /**********************************************************************
     * HISTORIAL
     **********************************************************************/

    async function loadHistory() {
        if (!historyBody) return;
        historyBody.innerHTML = <tr><td colspan="4" class="empty-state">Cargando...</td></tr>;
        try {
            const response = await request(URLS.history);
            if (!response.items || response.items.length === 0) {
                historyBody.innerHTML = <tr><td colspan="4" class="empty-state">No existen guías.</td></tr>;
                return;
            }
            historyBody.innerHTML = "";
            response.items.forEach(doc => {
                const created = doc.created_at ? new Date(doc.created_at).toLocaleString() : "";
                const tr = document.createElement("tr");
                tr.innerHTML = 
                    <td></td>
                    <td></td>
                    <td></td>
                    <td>
                        <button class="btn-action btn-open" data-id="">Abrir</button>
                        <button class="btn-action btn-word" data-id="">Word</button>
                        <button class="btn-action btn-pdf" data-id="">PDF</button>
                        <button class="btn-action delete btn-delete" data-id="">Eliminar</button>
                    </td>
                ;
                historyBody.appendChild(tr);
            });
        } catch (error) {
            console.error(error);
            historyBody.innerHTML = <tr><td colspan="4" class="empty-state">Error cargando historial</td></tr>;
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
            // DELETE sin body (Flask-WTF no lee body en DELETE)
            await request(URLS.document(documentId) + ?csrf_token=, { method: "DELETE" });
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
        const id = btn.dataset.id;
        if (btn.classList.contains("btn-open")) { await openDocument(id); return; }
        if (btn.classList.contains("btn-delete")) { await deleteDocument(id); return; }
        if (btn.classList.contains("btn-word")) { currentDocument = id; await loadExportLinks(); exportWord(); return; }
        if (btn.classList.contains("btn-pdf")) { currentDocument = id; await loadExportLinks(); exportPdf(); return; }
    });

    (async () => { try { await loadHistory(); } catch (e) { console.error(e); } })();
});
