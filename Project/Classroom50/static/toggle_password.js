// Select checkbox and inputs of type password
let showPassword = document.getElementById('showPassword');
let passwords = document.querySelectorAll('input[type="password"]')

// Change password visibility based on the checkbox checked status
showPassword.addEventListener('change', function() {
    if (showPassword.checked) {
        passwords.forEach((password) => {
            password.type = 'text';
        });
    } else {
        passwords.forEach((password) => {
            password.type = 'password';
        });
    }
});