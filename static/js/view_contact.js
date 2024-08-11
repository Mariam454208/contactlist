document.getElementById('toggle-enable').addEventListener('click', function() {
    const phoneInput = document.querySelector('input[name="phone_number"]');
    const emailInput = document.querySelector('input[name="email"]');
    const saveButton = document.getElementById('save-button');

    if (phoneInput.disabled && emailInput.disabled) {
        phoneInput.disabled = false;
        emailInput.disabled = false;
        saveButton.disabled = false;
        this.textContent = 'Disable'; 
    } else {
        phoneInput.disabled = true;
        emailInput.disabled = true;
        saveButton.disabled = true;
        this.textContent = 'Enable';
    }
});
