function confirmDeletion(contactId) {
    if (confirm('Are you sure you want to delete this contact?')) {
        window.location.href = '/delete_contact/' + contactId;
    }
}

function validateForm() {
    const firstName = document.querySelector('input[name="first_name"]').value;
    const lastName = document.querySelector('input[name="second_name"]').value;
    const phoneNumber = document.querySelector('input[name="phone_number"]').value;

    if (!firstName || !lastName || !phoneNumber) {
        alert('Please fill in all required fields.');
        return false;
    }
    return true;
}

document.addEventListener('DOMContentLoaded', function() {
    const deleteButtons = document.querySelectorAll('.delete-button');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(event) {
            event.preventDefault();
            const contactId = button.getAttribute('data-contact-id');
            confirmDeletion(contactId);
        });
    });

    const form = document.querySelector('form');
    if (form) {
        form.addEventListener('submit', function(event) {
            if (!validateForm()) {
                event.preventDefault();
            }
        });
    }
});
