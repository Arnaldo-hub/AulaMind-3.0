/* ==========================================================
   AulaMind Enterprise 3.0 — Panel Comercial (v3.3)
   static/js/admin_comercial.js
   ========================================================== */

(function () {
    "use strict";

    var CFG = window.COMERCIAL_CONFIG || {};

    // ------------------------------------------------------
    // Helpers
    // ------------------------------------------------------

    function apiFetch(url, options) {
        var opts = Object.assign({
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": CFG.csrfToken || ""
            }
        }, options || {});
        return fetch(url, opts).then(function (r) {
            return r.json().catch(function () { return {}; });
        });
    }

    function showToast(message, type) {
        var toast = document.getElementById("toast");
        toast.textContent = message;
        toast.className = "toast show " + (type || "");
        setTimeout(function () {
            toast.className = "toast";
        }, 3800);
    }

    function showLoader(show) {
        document.getElementById("loadingModal")
            .classList.toggle("open", !!show);
    }

    function esc(text) {
        var div = document.createElement("div");
        div.textContent = text == null ? "" : String(text);
        return div.innerHTML;
    }

    function fmtDate(iso) {
        if (!iso) return "—";
        var d = new Date(iso);
        if (isNaN(d)) return "—";
        return d.toLocaleDateString("es-CL", {
            day: "2-digit", month: "2-digit", year: "numeric"
        });
    }

    function fmtDateTime(iso) {
        if (!iso) return "—";
        var d = new Date(iso);
        if (isNaN(d)) return "—";
        return d.toLocaleDateString("es-CL", {
            day: "2-digit", month: "2-digit"
        }) + " " + d.toLocaleTimeString("es-CL", {
            hour: "2-digit", minute: "2-digit"
        });
    }

    // ------------------------------------------------------
    // KPIs
    // ------------------------------------------------------

    function loadKpis() {
        apiFetch(CFG.resumenUrl).then(function (data) {
            if (!data.success) return;
            var k = data.kpis || {};
            document.getElementById("kpiUsuarios").textContent = k.usuarios;
            document.getElementById("kpiTrials").textContent = k.trials;
            document.getElementById("kpiPro").textContent = k.pro_activos;
            document.getElementById("kpiExpirados").textContent = k.expirados;
            document.getElementById("kpiActivaciones").textContent = k.activaciones_mes;
        });
    }

    // ------------------------------------------------------
    // Tabla comercial
    // ------------------------------------------------------

    var currentRows = [];

    function statusPill(row) {
        return '<span class="pill pill-' + esc(row.status) + '">'
            + esc(row.status_label) + "</span>";
    }

    function daysCell(row) {
        if (row.days_left === null || row.days_left === undefined) {
            return '<span class="muted">—</span>';
        }
        var cls = row.days_left <= 2 ? "days-left warn" : "days-left";
        return '<span class="' + cls + '">' + row.days_left
            + (row.days_left === 1 ? " día" : " días") + "</span>";
    }

    function usageCell(row) {
        if (row.status !== "trial") {
            return '<span class="muted">—</span>';
        }
        return esc(row.generations_used) + " docs";
    }

    function actionCell(row) {
        if (row.status === "admin") {
            return '<span class="muted">—</span>';
        }
        var label = row.status === "active"
            ? "Renovar 30 días" : "Activar Plan Pro";
        return '<button class="btn-activate" data-user-id="'
            + esc(row.id) + '" data-user-email="'
            + esc(row.email) + '" data-days="30">'
            + '<i class="fa-solid fa-gem"></i> ' + label
            + "</button>";
    }

    function renderTable(rows) {
        var tbody = document.getElementById("comercialTableBody");
        var empty = document.getElementById("emptyState");

        if (!rows.length) {
            tbody.innerHTML = "";
            empty.style.display = "block";
            return;
        }

        empty.style.display = "none";

        tbody.innerHTML = rows.map(function (row) {
            return "<tr>"
                + '<td class="user-cell"><strong>' + esc(row.name)
                + "</strong><small>" + esc(row.email) + "</small></td>"
                + "<td>" + statusPill(row) + "</td>"
                + "<td>" + daysCell(row) + "</td>"
                + "<td>" + usageCell(row) + "</td>"
                + "<td>" + esc(row.source_label) + "</td>"
                + "<td>" + fmtDate(row.created_at) + "</td>"
                + "<td>" + actionCell(row) + "</td>"
                + "</tr>";
        }).join("");
    }

    function loadUsuarios() {
        var q = document.getElementById("searchInput").value.trim();
        var status = document.getElementById("statusFilter").value;

        var params = new URLSearchParams();
        if (q) params.set("q", q);
        if (status) params.set("status", status);

        var url = CFG.usuariosUrl
            + (params.toString() ? "?" + params.toString() : "");

        apiFetch(url).then(function (data) {
            if (!data.success) {
                showToast(data.error || "Error al cargar docentes.", "error");
                return;
            }
            currentRows = data.items || [];
            renderTable(currentRows);
        });
    }

    // ------------------------------------------------------
    // Eventos de pago
    // ------------------------------------------------------

    var ACTION_LABELS = {
        activated: "Plan activado",
        payment_failed: "Cobro fallido",
        noted: "Evento registrado",
        duplicate: "Duplicado",
        ignored: "Ignorado"
    };

    var PROVIDER_LABELS = {
        mercadopago: "Mercado Pago",
        manual: "Manual"
    };

    function renderEvents(items) {
        var tbody = document.getElementById("eventsTableBody");
        var empty = document.getElementById("eventsEmptyState");

        if (!items.length) {
            tbody.innerHTML = "";
            empty.style.display = "block";
            return;
        }

        empty.style.display = "none";

        tbody.innerHTML = items.map(function (ev) {
            var actionLabel = ACTION_LABELS[ev.action] || ev.action;
            var providerLabel = PROVIDER_LABELS[ev.provider] || ev.provider;
            return "<tr>"
                + "<td>" + fmtDateTime(ev.created_at) + "</td>"
                + "<td>" + esc(providerLabel) + "</td>"
                + '<td><span class="pill pill-' + esc(ev.action) + '">'
                + esc(actionLabel) + "</span></td>"
                + "<td>" + esc(ev.user_email || "—") + "</td>"
                + "<td>" + esc(ev.detail || "—") + "</td>"
                + "</tr>";
        }).join("");
    }

    function loadEventos() {
        apiFetch(CFG.eventosUrl).then(function (data) {
            if (!data.success) return;
            renderEvents(data.items || []);
        });
    }

    // ------------------------------------------------------
    // Modal activar plan
    // ------------------------------------------------------

    var planTargetId = null;

    function openPlanModal(userId, email, days) {
        planTargetId = userId;
        document.getElementById("planModalUser").textContent = email;
        document.getElementById("planDays").value = days || 30;
        document.getElementById("planModal").classList.add("open");
    }

    function closePlanModal() {
        planTargetId = null;
        document.getElementById("planModal").classList.remove("open");
    }

    function submitPlan(event) {
        event.preventDefault();
        if (!planTargetId) return;

        var days = parseInt(
            document.getElementById("planDays").value, 10
        );

        if (!days || days < 1 || days > 3660) {
            showToast("Los días deben estar entre 1 y 3660.", "error");
            return;
        }

        var url = CFG.planUrl.replace("__ID__", planTargetId);

        showLoader(true);

        apiFetch(url, {
            method: "PUT",
            body: JSON.stringify({ days: days })
        }).then(function (data) {
            showLoader(false);
            if (data.success) {
                showToast(data.message || "Plan activado.", "success");
                closePlanModal();
                loadKpis();
                loadUsuarios();
                loadEventos();
            } else {
                showToast(
                    data.error || data.message
                    || "No se pudo activar el plan.",
                    "error"
                );
            }
        }).catch(function () {
            showLoader(false);
            showToast("Error de red. Intenta nuevamente.", "error");
        });
    }

    // ------------------------------------------------------
    // Wiring
    // ------------------------------------------------------

    document.addEventListener("DOMContentLoaded", function () {

        loadKpis();
        loadUsuarios();
        loadEventos();

        var searchTimer = null;

        document.getElementById("searchInput")
            .addEventListener("input", function () {
                clearTimeout(searchTimer);
                searchTimer = setTimeout(loadUsuarios, 350);
            });

        document.getElementById("statusFilter")
            .addEventListener("change", loadUsuarios);

        document.getElementById("btnRefresh")
            .addEventListener("click", function () {
                loadKpis();
                loadUsuarios();
                loadEventos();
                showToast("Datos actualizados.", "success");
            });

        document.getElementById("comercialTableBody")
            .addEventListener("click", function (ev) {
                var btn = ev.target.closest(".btn-activate");
                if (!btn) return;
                openPlanModal(
                    btn.getAttribute("data-user-id"),
                    btn.getAttribute("data-user-email"),
                    btn.getAttribute("data-days")
                );
            });

        document.getElementById("btnCancelPlan")
            .addEventListener("click", closePlanModal);

        document.getElementById("planForm")
            .addEventListener("submit", submitPlan);

        document.getElementById("planModal")
            .addEventListener("click", function (ev) {
                if (ev.target === this) closePlanModal();
            });
    });

})();
