let sidebar = document.querySelector(".sidebar");
let closeBtn = document.querySelector("#btn");
let searchBtn = document.querySelector(".bx-search");
// safe event handlers
if (closeBtn) {
  closeBtn.addEventListener("click", ()=>{
    if (sidebar) sidebar.classList.toggle("open");
    menuBtnChange();
  });
}

if (searchBtn) {
  searchBtn.addEventListener("click", ()=>{ // Sidebar open when you click on the search icon
    if (sidebar) sidebar.classList.add("open");
    menuBtnChange();
    // focus input if exists
    const s = document.querySelector('.sidebar input[type="text"]');
    if (s) s.focus();
  });
}

// following are the code to change sidebar button
function menuBtnChange() {
 if(sidebar.classList.contains("open")){
   closeBtn.classList.replace("bx-menu", "bx-menu-alt-right");
 }else {
   closeBtn.classList.replace("bx-menu-alt-right","bx-menu");
 }
}

// Search/filter functionality for sidebar
const searchInput = document.querySelector('.sidebar input[type="text"]');
if (searchInput) {
  searchInput.addEventListener('input', (e) => {
    const q = (e.target.value || '').toLowerCase().trim();
    const items = Array.from(document.querySelectorAll('.sidebar .nav-list > li'));
    // keep the first li (search) and profile li visible
    items.forEach((li, idx) => {
      if (li.classList.contains('profile')) return; // keep profile
      // skip the search li itself
      const isSearchLi = (li.querySelector('input[type="text"]') !== null);
      if (isSearchLi) return;
      const linkNameEl = li.querySelector('.links_name');
      const tooltipEl = li.querySelector('.tooltip');
      const text = (linkNameEl?.textContent || tooltipEl?.textContent || '').toLowerCase();
      if (!q) {
        li.style.display = '';
      } else if (text.includes(q)) {
        li.style.display = '';
      } else {
        li.style.display = 'none';
      }
    });
    if (q && sidebar && !sidebar.classList.contains('open')) sidebar.classList.add('open');
  });
}

// Allow mouse wheel to scroll sidebar when hovered (makes UX better on some setups)
if (sidebar) {
  sidebar.addEventListener('wheel', (e) => {
    // only prevent page scroll when hovering over sidebar
    e.stopPropagation();
  }, { passive: true });
}

// Profile click handler - navigate to profile page
const profileDetails = document.querySelector('.profile-details');
if (profileDetails) {
  profileDetails.addEventListener('click', () => {
    window.location.href = '/profile/';
  });
  profileDetails.style.cursor = 'pointer';
}

// Logout button handler
const logoutBtn = document.querySelector('#logout-btn');
if (logoutBtn) {
  logoutBtn.addEventListener('click', () => {
    // Clear session/token
    localStorage.removeItem('token');
    sessionStorage.removeItem('token');
    // Redirect to login
    window.location.href = '/login/';
  });
}
