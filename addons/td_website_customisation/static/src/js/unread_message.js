/** @odoo-module **/

import { rpc } from "web.rpc";

async function fetchUnreadMessages() {
    try {
        const res = await rpc.query({
            route: '/my/messages/unread_count',
            params: {},
        });
        return res;
    } catch (err) {
        console.error("Error fetching unread messages:", err);
        return { total_count: 0, by_user: [] };
    }
}

function updateBellBadge(count) {
    const badge = document.querySelector(".unread-bell-badge");
    if (badge) {
        badge.textContent = count;
        badge.style.display = count > 0 ? 'inline-block' : 'none';
    }
}

function updateDropdownMenu(byUser) {
    const menu = document.querySelector(".unread-messages-menu");
    if (!menu) return;

    const header = menu.querySelector(".dropdown-header");
    menu.innerHTML = '';

    if (header) {
        menu.appendChild(header);
    }

    if (byUser.length === 0) {
        const li = document.createElement('li');
        li.innerHTML = '<span class="dropdown-item-text text-muted">No hay mensajes nuevos</span>';
        menu.appendChild(li);
    } else {
        byUser.slice(0, 5).forEach(item => {
            const li = document.createElement('li');
            li.innerHTML = `
                <a class="dropdown-item" href="/my/messages/thread/${item.partner_id}">
                    <div class="d-flex align-items-center">
                        <div class="flex-grow-1">
                            <strong>${item.partner_name}</strong>
                        </div>
                        <span class="badge bg-primary">${item.unread_count}</span>
                    </div>
                </a>
            `;
            menu.appendChild(li);
        });

        if (byUser.length > 5) {
            const divider = document.createElement('li');
            divider.innerHTML = '<hr class="dropdown-divider"/>';
            menu.appendChild(divider);

            const viewAll = document.createElement('li');
            viewAll.innerHTML = '<a class="dropdown-item text-center" href="/my/messages">Ver todos</a>';
            menu.appendChild(viewAll);
        }
    }
}

async function initUnreadWidget() {
    try {
        const res = await fetchUnreadMessages();
        updateBellBadge(res.total_count);
        updateDropdownMenu(res.by_user);
    } catch (e) {
        console.error('Failed to init unread widget', e);
    }
}

document.addEventListener("DOMContentLoaded", () => {
    initUnreadWidget();
    setInterval(initUnreadWidget, 30000);
});