/**
 * ZERVO Notifications Manager
 * Handles notification panel toggling, unread badges, and marking notifications read.
 */

class NotificationsController {
  constructor() {
    this.wrapper = document.querySelector('.zervo-notifications, #notif-wrapper');
    if (!this.wrapper) return;

    this.btn = this.wrapper.querySelector('.zervo-notifications-btn, #notif-btn');
    this.dropdown = this.wrapper.querySelector('.zervo-notifications-dropdown, #notif-panel');
    this.badge = this.wrapper.querySelector('.zervo-notifications-badge, #notif-badge');
    this.list = this.wrapper.querySelector('.zervo-notifications-list, #notif-list');
    this.emptyState = this.wrapper.querySelector('.zervo-notifications-empty');
    this.markAllBtn = this.wrapper.querySelector('.zervo-notifications-mark-all');

    this.notifications = JSON.parse(localStorage.getItem('zervo_notifications') || '[]');
    this.isOpen = false;

    this.init();
  }

  init() {
    this.render();
    this.bindEvents();
  }

  bindEvents() {
    if (this.btn) {
      this.btn.addEventListener('click', (e) => {
        e.stopPropagation();
        this.toggleDropdown();
      });
    }

    if (this.markAllBtn) {
      this.markAllBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        this.markAllRead();
      });
    }

    document.addEventListener('mousedown', (e) => {
      if (this.isOpen && this.wrapper && !this.wrapper.contains(e.target)) {
        this.closeDropdown();
      }
    });

    document.addEventListener('keydown', (e) => {
      if (this.isOpen && e.key === 'Escape') {
        this.closeDropdown();
      }
    });
  }

  toggleDropdown() {
    this.isOpen ? this.closeDropdown() : this.openDropdown();
  }

  openDropdown() {
    if (!this.dropdown) return;
    this.isOpen = true;
    this.dropdown.classList.remove('hidden', 'opacity-0', 'scale-95', 'pointer-events-none');
    this.dropdown.classList.add('opacity-100', 'scale-100', 'pointer-events-auto');
    if (this.dropdown.style.display !== undefined) {
      this.dropdown.style.display = 'flex';
    }
  }

  closeDropdown() {
    if (!this.dropdown) return;
    this.isOpen = false;
    this.dropdown.classList.remove('opacity-100', 'scale-100', 'pointer-events-auto');
    this.dropdown.classList.add('opacity-0', 'scale-95', 'pointer-events-none');
    setTimeout(() => {
      if (!this.isOpen) this.dropdown.classList.add('hidden');
    }, 200);
  }

  markAllRead() {
    this.notifications.forEach(n => n.read = true);
    localStorage.setItem('zervo_notifications', JSON.stringify(this.notifications));
    this.render();
  }

  render() {
    const unreadCount = this.notifications.filter(n => !n.read).length;

    if (this.badge) {
      if (unreadCount > 0) {
        this.badge.textContent = unreadCount;
        this.badge.classList.remove('hidden');
        this.badge.style.display = 'flex';
      } else {
        this.badge.classList.add('hidden');
        this.badge.style.display = 'none';
      }
    }

    if (this.list) {
      if (this.notifications.length === 0) {
        this.list.innerHTML = '';
        if (this.emptyState) this.emptyState.classList.remove('hidden');
      } else {
        if (this.emptyState) this.emptyState.classList.add('hidden');
        this.list.innerHTML = this.notifications.map(n => `
          <div class="p-4 border-b border-outline-variant/10 hover:bg-surface-variant/20 transition-colors ${n.read ? 'opacity-60' : 'bg-primary/5'}">
            <p class="font-bold text-sm text-on-surface">${n.title || 'Notification'}</p>
            <p class="text-xs text-on-surface-variant mt-1">${n.message || ''}</p>
          </div>
        `).join('');
      }
    }
  }
}

document.addEventListener('DOMContentLoaded', () => {
  window.zervoNotifications = new NotificationsController();
});

export default NotificationsController;
