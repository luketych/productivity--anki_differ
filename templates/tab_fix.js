        // Initialize Bootstrap tabs
        var tabEl = document.querySelector("button[data-bs-toggle='tab']");
        var bsTab = new bootstrap.Tab(tabEl);
        document.querySelectorAll(".nav-link").forEach(tab => {
            tab.addEventListener("click", function(event) {
                event.preventDefault();
                var bsTab = new bootstrap.Tab(this);
                bsTab.show();
            });
        });
