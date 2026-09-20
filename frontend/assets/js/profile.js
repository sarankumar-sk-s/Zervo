/**
 * Profile Dropdown Controller — ZERVO (Frontend Local Storage Session)
 * ✅ Pure frontend session management via localStorage
 * ✅ Standalone client-side application controller
 */

// ── Get current cached user from localStorage or return null ─────────────────
function getCurrentUser() {
  const stored = localStorage.getItem('zervo_current_user');
  return stored ? JSON.parse(stored) : null;
}

// ── Check if user is authenticated ───────────────────────────────────────────
function isAuthenticated() {
  return getCurrentUser() !== null;
}

// ── Fill profile dropdown with user data ──────────────────────────────────────
function fillProfileDropdown(user) {
  if (!user) return;

  const wrapper = document.querySelector('.zervo-profile-wrapper');
  if (!wrapper) return;

  const name = user.name || 'User';
  const email = user.email || '';

  // Update name and email in dropdown header
  const dropdownHeader = wrapper.querySelector('.zervo-profile-rdown .p-4');
  if (dropdownHeader) {
    const allP = dropdownHeader.querySelectorAll('p');
    if (allP[0]) allP[0].textContent = name;
    if (allP[1]) allP[1].textContent = email;
  }

  // Show initials instead of hardcoded avatar image
  const triggerDiv = wrapper.querySelector('.zervo-profile-rtrig > div, #avatar');
  if (triggerDiv) {
    const initials = name.split(' ').map(function(n){ return n[0]; }).join('').substring(0, 2).toUpperCase();
    triggerDiv.innerHTML = '';
    triggerDiv.className = 'w-10 h-10 rounded-full bg-primary flex items-center justify-center text-white font-bold text-sm';
    triggerDiv.textContent = initials;
  }
}

// ── Setup logout event handlers ───────────────────────────────────────────────
function setupLogout() {
  const logoutButtons = document.querySelectorAll(
    '.zervo-profile-rdown a[href="login.html"], .zervo-profile-rdown a[href="#"], #logout-btn'
  );
  logoutButtons.forEach(btn => {
    if (!btn._zervoLogout) {
      btn._zervoLogout = true;
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        localStorage.removeItem('zervo_current_user');
        sessionStorage.clear();
        window.location.href = 'login.html';
      });
    }
  });
}

// ── Initialize profile session on page load ──────────────────────────────────
function initializeProfile() {
  const page = window.location.pathname.split('/').pop();
  const publicPages = ['login.html', 'signup.html', 'forgot-password.html', 'index.html', ''];
  const isPublic = publicPages.indexOf(page) !== -1;

  const cachedUser = getCurrentUser();
  if (cachedUser) {
    fillProfileDropdown(cachedUser);
    setupLogout();

    if (typeof window.initializeDashboard === 'function') {
      window.initializeDashboard();
    } else if (typeof window.loadUserProfile === 'function') {
      window.loadUserProfile();
    } else if (typeof window.initializeSubmission === 'function') {
      window.initializeSubmission();
    } else if (typeof window.initializeRoleSelection === 'function') {
      window.initializeRoleSelection();
    }
  } else if (!isPublic) {
    window.location.href = 'login.html';
  }
}

// ── Dropdown Controller ───────────────────────────────────────────────────────
class ProfileDropdownController {
  constructor() {
    this.isOpen = false;
    this.wrapper = document.querySelector('.zervo-profile-wrapper, #profile-wrapper');
    if (this.wrapper) {
      this.trigger = this.wrapper.querySelector('.zervo-profile-rtrig, #profile-btn');
      this.dropdown = this.wrapper.querySelector('.zervo-profile-rdown, #profile-panel');
      this.bindEvents();
    }
  }

  bindEvents() {
    if (!this.trigger || !this.dropdown) return;

    this.trigger.addEventListener('click', (e) => {
      e.stopPropagation();
      this.toggleDropdown();
    });
    document.addEventListener('mousedown', (e) => {
      if (this.isOpen && !this.wrapper.contains(e.target)) this.closeDropdown();
    });
    document.addEventListener('keydown', (e) => {
      if (this.isOpen && e.key === 'Escape') {
        this.closeDropdown();
        this.trigger.focus();
      }
    });
    this.dropdown.querySelectorAll('[role="menuitem"], a').forEach(item => {
      item.addEventListener('click', () => this.closeDropdown());
    });
  }

  toggleDropdown() { this.isOpen ? this.closeDropdown() : this.openDropdown(); }

  openDropdown() {
    this.isOpen = true;
    this.trigger.setAttribute('aria-expanded', 'true');
    const viewProfileLink = this.dropdown.querySelector('a[href*="editprofile.html"]');
    if (viewProfileLink) {
      const currentPage = window.location.pathname.split('/').pop() || 'index.html';
      viewProfileLink.href = 'editprofile.html?from=' + currentPage;
    }
    this.dropdown.classList.remove('opacity-0', 'scale-95', '-translate-y-2', 'invisible', 'pointer-events-none');
    this.dropdown.classList.add('opacity-100', 'scale-100', 'translate-y-0', 'visible');
    this.dropdown.style.display = 'flex';
  }

  closeDropdown() {
    this.isOpen = false;
    this.trigger.setAttribute('aria-expanded', 'false');
    this.dropdown.classList.remove('opacity-100', 'scale-100', 'translate-y-0', 'visible');
    this.dropdown.classList.add('opacity-0', 'scale-95', '-translate-y-2', 'invisible', 'pointer-events-none');
    this.dropdown.style.display = '';
  }
}

// ── Initialize when DOM is ready ──────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  initializeProfile();
  new ProfileDropdownController();
});

// ── Export auth helpers ───────────────────────────────────────────────────────
window.zervoAuth = {
  getCurrentUser,
  isAuthenticated
};
