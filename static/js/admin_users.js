/*
===========================================================
AulaMind Enterprise 3.0
static/js/admin_users.js
-----------------------------------------------------------
Módulo M-09: Administración de Usuarios (CRUD AJAX)
===========================================================
*/

(function () {
    "use strict";

    const cfg = window.ADMIN_USERS_CONFIG;

    // ======================================================
    // Referencias DOM
    // ======================================================

    const tableBody = document.getElementById("usersTableBody");
    const emptyState = document.getElementById("emptyState");
    const searchInput = document.getElementById("searchInput");
    const roleFilter = document.getElementById("roleFilter");
    const statusFilter = document.getElementById("statusFilter");

    const btnNewUser = document.getElementById("btnNewUser");
    const modal = document.getElementById("userModal");
    const modalTitle = document.getElementById("modalTitle");
    const userForm = document.getElementById("userForm");
    const btnCancelModal = document.getElementById("btnCancelModal");
    const passwordInput = document.getElementById("password");
    const passwordHint = document.getElementById("passwordHint");

    const loadingModal = document.getElementById("loadingModal");
    const toast = document.getElementById("toast");

    let editingUserId = null;
    let searchTimer = null;

    // ======================================================
    // Utilidades
    // ======================================================

    function url(template, id) {
        return template.replace("__ID__", encodeURIComponent(id));
    }

    function showLoading(show) {
        loadingModal.style.display = show ? "flex" : "none";
    }

    function showToast(message, type) {
        toast.textContent = message;
        toast.className = "toast show " + (type || "info");
        setTimeout(function () {
            toast.className = "toast";
        }, 3500);
    }

    function escapeHtml(value) {
        const div = document.createElement("div");
        div.textContent = value == null ? "" : String(value);
        return div.innerHTML;
    }

    function formatDate(isoString) {
        if (!isoString) return "—";
        const date = new Date(isoString);
        if (isNaN(date)) return "—";
        return date.toLocaleDateString("es-CL", {
            day: "2-digit",
            month: "2-digit",
            year: "numeric",
            hour: "2-digit",
            minute: "2-digit"
        });
    }

    async function apiFetch(fetchUrl, options) {
        const response = await fetch(fetchUrl, Object.assign({
            headers: { "Content-Type": "application/json" }
        }, options));

        let data = {};
        try {
            data = await response.json();
        } catch (e) {
            /* respuesta sin cuerpo JSON */
        }

        if (!response.ok) {
            throw new Error(data.error || "Error " + response.status);
        }
        return data;
    }

    // ======================================================
    // Renderizado de la tabla
    // ======================================================

    function roleBadge(user) {
        if (user.role === "admin") {
            return '<span class="badge badge-admin">Administrador</span>';
        }
        return '<span class="badge badge-teacher">' +
            escapeHtml(user.role_label || "Docente") + "</span>";
    }

    function statusBadge(user) {
        if (user.is_active) {
            return '<span class="badge badge-active">Activo</span>';
        }
        return '<span class="badge badge-inactive">Inactivo</span>';
    }

    function actionButtons(user) {
        const isSelf = String(user.id) === String(cfg.currentUserId);

        let buttons =
            '<button class="btn-icon" data-action="edit" ' +
            'data-id="' + escapeHtml(user.id) + '" title="Editar">' +
            '<i class="fa-solid fa-pen"></i></button>';

        if (!isSelf) {
            const toggleClass = user.is_active
                ? "btn-toggle-off" : "btn-toggle-on";
            const toggleIcon = user.is_active
                ? "fa-user-slash" : "fa-user-check";
            const toggleTitle = user.is_active
                ? "Desactivar" : "Activar";

            buttons +=
                '<button class="btn-icon ' + toggleClass + '" ' +
                'data-action="toggle" data-id="' + escapeHtml(user.id) +
                '" title="' + toggleTitle + '">' +
                '<i class="fa-solid ' + toggleIcon + '"></i></button>';

            buttons +=
                '<button class="btn-icon btn-danger" ' +
                'data-action="delete" data-id="' + escapeHtml(user.id) +
                '" title="Eliminar">' +
                '<i class="fa-solid fa-trash"></i></button>';
        }

        return '<div class="row-actions">' + buttons + "</div>";
    }

    function renderUsers(users) {
        tableBody.innerHTML = "";

        if (!users.length) {
            emptyState.style.display = "block";
            return;
        }

        emptyState.style.display = "none";

        users.forEach(function (user) {
            const tr = document.createElement("tr");
            tr.innerHTML =
                "<td>" +
                    '<div class="user-name">' +
                        escapeHtml(user.full_name) +
                    "</div>" +
                    '<div class="user-email">' +
                        escapeHtml(user.email) +
                    "</div>" +
                "</td>" +
                "<td>" + roleBadge(user) + "</td>" +
                "<td>" + statusBadge(user) + "</td>" +
                "<td>" + formatDate(user.last_login) + "</td>" +
                "<td>" + actionButtons(user) + "</td>";
            tableBody.appendChild(tr);
        });
    }

    // ======================================================
    // Carga de usuarios
    // ======================================================

    async function loadUsers() {
        const params = new URLSearchParams();

        if (searchInput.value.trim()) {
            params.set("q", searchInput.value.trim());
        }
        if (roleFilter.value) {
            params.set("role", roleFilter.value);
        }
        if (statusFilter.value) {
            params.set("status", statusFilter.value);
        }

        const fetchUrl = params.toString()
            ? cfg.listUrl + "?" + params.toString()
            : cfg.listUrl;

        try {
            const data = await apiFetch(fetchUrl);
            renderUsers(data.items || []);
        } catch (err) {
            showToast(err.message, "error");
        }
    }

    // ======================================================
    // Modal crear / editar
    // ======================================================

    function openCreateModal() {
        editingUserId = null;
        modalTitle.textContent = "Nuevo usuario";
        userForm.reset();
        passwordInput.required = true;
        passwordHint.textContent = "Mínimo 8 caracteres.";
        modal.classList.add("open");
    }

    async function openEditModal(userId) {
        try {
            const data = await apiFetch(url(cfg.userUrl, userId));
            const user = data.user;

            editingUserId = user.id;
            modalTitle.textContent = "Editar usuario";
            document.getElementById("firstName").value = user.first_name;
            document.getElementById("lastName").value = user.last_name;
            document.getElementById("email").value = user.email;
            document.getElementById("phone").value = user.phone || "";
            document.getElementById("role").value = user.role;
            passwordInput.value = "";
            passwordInput.required = false;
            passwordHint.textContent =
                "Déjala en blanco para mantener la contraseña actual.";

            modal.classList.add("open");
        } catch (err) {
            showToast(err.message, "error");
        }
    }

    function closeModal() {
        modal.classList.remove("open");
        editingUserId = null;
    }

    // ======================================================
    // Guardar (crear / actualizar)
    // ======================================================

    async function saveUser(event) {
        event.preventDefault();

        const payload = {
            first_name: document.getElementById("firstName").value,
            last_name: document.getElementById("lastName").value,
            email: document.getElementById("email").value,
            phone: document.getElementById("phone").value,
            role: document.getElementById("role").value,
            password: passwordInput.value
        };

        const isEdit = editingUserId !== null;
        const fetchUrl = isEdit
            ? url(cfg.updateUrl, editingUserId)
            : cfg.createUrl;

        showLoading(true);

        try {
            await apiFetch(fetchUrl, {
                method: isEdit ? "PUT" : "POST",
                body: JSON.stringify(payload)
            });

            showToast(
                isEdit
                    ? "Usuario actualizado correctamente."
                    : "Usuario creado correctamente.",
                "success"
            );
            closeModal();
            await loadUsers();
        } catch (err) {
            showToast(err.message, "error");
        } finally {
            showLoading(false);
        }
    }

    // ======================================================
    // Alternar estado
    // ======================================================

    async function toggleUser(userId) {
        showLoading(true);

        try {
            const data = await apiFetch(
                url(cfg.toggleUrl, userId),
                { method: "PATCH" }
            );

            showToast(
                data.user.is_active
                    ? "Usuario activado."
                    : "Usuario desactivado.",
                "success"
            );
            await loadUsers();
        } catch (err) {
            showToast(err.message, "error");
        } finally {
            showLoading(false);
        }
    }

    // ======================================================
    // Eliminar (desactivación lógica)
    // ======================================================

    async function deleteUser(userId) {
        if (!window.confirm(
            "¿Eliminar este usuario? La cuenta quedará desactivada."
        )) {
            return;
        }

        showLoading(true);

        try {
            await apiFetch(
                url(cfg.deleteUrl, userId),
                { method: "DELETE" }
            );

            showToast("Usuario eliminado correctamente.", "success");
            await loadUsers();
        } catch (err) {
            showToast(err.message, "error");
        } finally {
            showLoading(false);
        }
    }

    // ======================================================
    // Eventos
    // ======================================================

    btnNewUser.addEventListener("click", openCreateModal);
    btnCancelModal.addEventListener("click", closeModal);
    userForm.addEventListener("submit", saveUser);

    modal.addEventListener("click", function (event) {
        if (event.target === modal) {
            closeModal();
        }
    });

    document.addEventListener("keydown", function (event) {
        if (event.key === "Escape") {
            closeModal();
        }
    });

    searchInput.addEventListener("input", function () {
        clearTimeout(searchTimer);
        searchTimer = setTimeout(loadUsers, 300);
    });

    roleFilter.addEventListener("change", loadUsers);
    statusFilter.addEventListener("change", loadUsers);

    tableBody.addEventListener("click", function (event) {
        const button = event.target.closest("button[data-action]");
        if (!button) return;

        const userId = button.getAttribute("data-id");
        const action = button.getAttribute("data-action");

        if (action === "edit") {
            openEditModal(userId);
        } else if (action === "toggle") {
            toggleUser(userId);
        } else if (action === "delete") {
            deleteUser(userId);
        }
    });

    // ======================================================
    // Inicialización
    // ======================================================

    loadUsers();

})();
