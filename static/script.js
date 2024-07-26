document.addEventListener('DOMContentLoaded', function() {
    if(window.location.hash) {
        var hash = window.location.hash.substring(1); //Puts hash in variable, and removes the # character
        var hashTab = document.getElementById(hash + '-tab');
        if (hashTab) {
            new bootstrap.Tab(hashTab).show(); // Show the tab corresponding to the hash
        }
    }
});