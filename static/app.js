document.addEventListener('DOMContentLoaded', function() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert:not(.persistent-alert)');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);
});

document.addEventListener('DOMContentLoaded', function() {
    var importoInputs = document.querySelectorAll('input[name="importo"]');
    
    importoInputs.forEach(function(input) {
        input.addEventListener('blur', function() {
            var value = this.value.replace(',', '.');
            if (!isNaN(parseFloat(value))) {
                this.value = parseFloat(value).toFixed(2);
            }
        });
    });
});