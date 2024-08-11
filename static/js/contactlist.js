document.addEventListener('DOMContentLoaded', function() {
    const viewButtons = document.querySelectorAll('.view');
    const editButtons = document.querySelectorAll('.edit');
    const changePasswordButtons = document.querySelectorAll('.change-password');
    const deleteButtons = document.querySelectorAll('.delete');

    viewButtons.forEach(button => {
        button.addEventListener('click', function() {
            alert('View user details.');
        });
    });

    editButtons.forEach(button => {
        button.addEventListener('click', function() {
            alert('Edit user details.');
        });
    });

    changePasswordButtons.forEach(button => {
        button.addEventListener('click', function() {
            alert('Change user password.');
        });
    });

    deleteButtons.forEach(button => {
        button.addEventListener('click', function() {
            if (confirm('Are you sure you want to delete this user?')) {
                alert('User deleted.');
            }
        });
    });
});
