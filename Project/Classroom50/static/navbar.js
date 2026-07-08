// Query nav link that directs to the current route path
var currentNavLink = document.querySelector('.nav-link[href="' + window.location.pathname + '"]');

// If such nav link exists
if (!(currentNavLink === null)) {

    // Make the nav link active
    currentNavLink.classList.add('active');
    currentNavLink.setAttribute('aria-current', 'page');
}