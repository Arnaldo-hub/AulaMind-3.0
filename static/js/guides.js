/******************************************************************************
 * AulaMind Enterprise 3.0 - Guías de Apoyo IA
 ******************************************************************************/

document.addEventListener("DOMContentLoaded", function() {
    "use strict";

    var CONFIG = window.GUIDE_CONFIG || {};
    var CSRF_TOKEN = document.getElementById("csrf_token") ? document.getElementById("csrf_token").value : "";
    var API_BASE = "/planning/api/curriculum";

    var URLS = {
        generate: CONFIG.generateUrl,
        history: CONFIG.historyUrl,
        document: function(id) { return "/guides/" + id; },
        exportLinks: function(id) { return "/guides/export-links/" + id; }
    };

    var form = document.getElementById("guideForm");
    var resultSection = document.getElementById("resultSection");
    var result = document.getElementById("guideResult");
    var historyBody = document.getElementById("historyBody");
    var loadingModal = document.getElementById("loadingModal");
    var toast = document.getElementById("toast");

    var currentDocument = null;
    var exportInfo = { word: null, pdf: null };

    function showLoading() { if(loadingModal) loadingModal.classList.add("active"); }
    function hideLoading() { if(loadingModal) loadingModal.classList.remove("active"); }

    function showToast(message, type) {
        type = type || "success";
        if (!toast) { console.log(message); return; }
        toast.textContent = message;
        toast.className = "toast " + type;
        setTimeout(function() { toast.classList.add("show"); }, 10);
        setTimeout(function() { toast.classList.remove("show"); }, 3000);
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

    async function request(url, options) {
        options = options || {};
        var defaultHeaders = { "Content-Type": "application/json", "X-CSRFToken": CSRF_TOKEN };
        var mergedHeaders = Object.assign({}, defaultHeaders, options.headers || {});
        
        var response = await fetch(url, Object.assign({}, options, { headers: mergedHeaders }));
        var data = await response.json();
        
        if (!response.ok || data.success === false) {
            throw new Error(data.error || "Error del servidor.");
        }
        return data;
    }

    /**********************************************************************
     * CARGA EN CASCADA DEL CURRICULO
     **********************************************************************/

    async function populateSelect(url, selectId, placeholder) {
        var select = document.getElementById(selectId);
        if (!select) return;
        try {
            var response = await fetch(url);
            var data = await response.json();
            if (!data.success) throw new Error(data.message || "Error API");

            select.innerHTML = "<option value=\"\">" + placeholder + "</option>";

            var key = selectId === "curso" ? "courses"
                      : selectId === "asignatura" ? "subjects"
                      : selectId === "unidad" ? "units"
                      : "objectives";

            var items = data[key];
            if (!items || items.length === 0) {
                select.innerHTML = "<option value=\"\">No hay datos disponibles</option>";
                select.disabled = true;
                return;
            }

            items.forEach(function(item) {
                var opt = document.createElement("option");
                if (typeof item === "object" && item !== null) {
                    if (item.code) {
                        opt.value = item.code;
                        opt.textContent = item.code + " - " + (item.description || "");
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
            console.error("Error cargando " + selectId + ":", err);
            select.innerHTML = "<option value=\"\">Error cargando datos</option>";
            select.disabled = true;
        }
    }

    // Cargar cursos
    (async function() { 
        await populateSelect(API_BASE + "/courses", "curso", "Selecciona un curso..."); 
    })();

    var cursoSelect = document.getElementById("curso");
    if (cursoSelect) {
        cursoSelect.addEventListener("change", async function() {
            var course = this.value;
            var asignatura = document.getElementById("asignatura");
            var unidad = document.getElementById("unidad");
            var objetivo = document.getElementById("objetivo");

            asignatura.innerHTML = "<option value=\"\">Selecciona una asignatura...</option>";
            unidad.innerHTML = "<option value=\"\">Selecciona una unidad...</option>";
            objetivo.innerHTML = "<option value=\"\">Selecciona un OA...</option>";
            asignatura.disabled = !course;
            unidad.disabled = true;
            objetivo.disabled = true;

            if (!course) return;
            await populateSelect(API_BASE + "/subjects/" + encodeURIComponent(course), "asignatura", "Selecciona una asignatura...");
        });
    }

    var asignaturaSelect = document.getElementById("asignatura");
    if (asignaturaSelect) {
        asignaturaSelect.addEventListener("change", async function() {
            var course = document.getElementById("curso").value;
            var subject = this.value;
            var unidad = document.getElementById("unidad");
            var objetivo = document.getElementById("objetivo");

            unidad.innerHTML = "<option value=\"\">Selecciona una unidad...</option>";
            objetivo.innerHTML = "<option value=\"\">Selecciona un OA...</option>";
            unidad.disabled = !subject;
            objetivo.disabled = true;

            if (!subject) return;
            await populateSelect(API_BASE + "/units/" + encodeURIComponent(course) + "/" + encodeURIComponent(subject), "unidad", "Selecciona una unidad...");
        });
    }

    var unidadSelect = document.getElementById("unidad");
    if (unidadSelect) {
        unidadSelect.addEventListener("change", async function() {
            var course = document.getElementById("curso").value;
            var subject = document.getElementById("asignatura").value;
            var unit = this.value;
            var objetivo = document.getElementById("objetivo");

            objetivo.innerHTML = "<option value=\"\">Selecciona un OA...</option>";
            objetivo.disabled = !unit;

            if (!unit) return;
            await populateSelect(API_BASE + "/objectives/" + encodeURIComponent(course) + "/" + encodeURIComponent(subject) + "/" + encodeURIComponent(unit), "objetivo", "Selecciona un OA...");
        });
    }

    /**********************************************************************
     * GENERAR GUIA
     **********************************************************************/

    async function generateGuide() {
        var payload = Object.fromEntries(new FormData(form).entries());
        showLoading();
        try {
            var response = await request(URLS.generate, { method: "POST", body: JSON.stringify(payload) });
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
        historyBody.innerHTML = "<tr><td colspan=\"4\" class=\"empty-state\">Cargando...</td></tr>";
        try {
            var response = await request(URLS.history);
            if (!response.items || response.items.length === 0) {
                historyBody.innerHTML = "<tr><td colspan=\"4\" class=\"empty-state\">No existen guías.</td></tr>";
                return;
            }
            historyBody.innerHTML = "";
            response.items.forEach(function(doc) {
                var created = doc.created_at ? new Date(doc.created_at).toLocaleString() : "";
                var tr = document.createElement("tr");
                tr.innerHTML = 
                    "<td>" + created + "</td>" +
                    "<td>" + (doc.course || "") + "</td>" +
                    "<td>" + (doc.subject || "") + "</td>" +
                    "<td>" +
                        "<button class=\"btn-action btn-open\" data-id=\"" + doc.id + "\">Abrir</button>" +
                        "<button class=\"btn-action btn-word\" data-id=\"" + doc.id + "\">Word</button>" +
                        "<button class=\"btn-action btn-pdf\" data-id=\"" + doc.id + "\">PDF</button>" +
                        "<button class=\"btn-action delete btn-delete\" data-id=\"" + doc.id + "\">Eliminar</button>" +
                    "</td>";
                historyBody.appendChild(tr);
            });
        } catch (error) {
            console.error(error);
            historyBody.innerHTML = "<tr><td colspan=\"4\" class=\"empty-state\">Error cargando historial</td></tr>";
        }
    }

    async function openDocument(documentId) {
        showLoading();
        try {
            var response = await request(URLS.document(documentId));
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
            var url = URLS.document(documentId) + "?csrf_token=" + encodeURIComponent(CSRF_TOKEN);
            await request(url, { method: "DELETE" });
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
            var response = await request(URLS.exportLinks(currentDocument));
            exportInfo.word = response.word;
            exportInfo.pdf = response.pdf;
        } catch (error) {
            console.error(error);
        }
    }

    async function copyGuide() {
        if (!result) return;
        var text = result.textContent.trim();
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
    if (form) form.addEventListener("submit", function(e) { e.preventDefault(); generateGuide(); });
    
    var copyBtn = document.getElementById("copyGuide");
    if (copyBtn) copyBtn.addEventListener("click", copyGuide);
    
    var wordBtn = document.getElementById("downloadWord");
    if (wordBtn) wordBtn.addEventListener("click", exportWord);
    
    var pdfBtn = document.getElementById("downloadPdf");
    if (pdfBtn) pdfBtn.addEventListener("click", exportPdf);

    if (historyBody) {
        historyBody.addEventListener("click", async function(e) {
            var btn = e.target.closest("button");
            if (!btn) return;
            var id = btn.dataset.id;
            if (btn.classList.contains("btn-open")) { await openDocument(id); return; }
            if (btn.classList.contains("btn-delete")) { await deleteDocument(id); return; }
            if (btn.classList.contains("btn-word")) { currentDocument = id; await loadExportLinks(); exportWord(); return; }
            if (btn.classList.contains("btn-pdf")) { currentDocument = id; await loadExportLinks(); exportPdf(); return; }
        });
    }

    (async function() { 
        try { await loadHistory(); } catch (e) { console.error(e); } 
    })();
});
