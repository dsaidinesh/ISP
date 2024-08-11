document.addEventListener('DOMContentLoaded', function() {
    if(window.location.hash) {
        var hash = window.location.hash.substring(1);
        var hashTab = document.getElementById(hash + '-tab');
        if (hashTab) {
            new bootstrap.Tab(hashTab).show();
        }
    }
});