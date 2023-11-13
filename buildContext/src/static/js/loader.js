var truelight = truelight || {};

truelight.loader = (function() {
    var loaderId = 'truelight-loader';

    function createLoader() {
        var loaderDiv = document.createElement('div');
        loaderDiv.id = loaderId;
        loaderDiv.className = 'bg-dark position-fixed translate-middle w-100 vh-100 top-50 start-50 d-flex align-items-center justify-content-center';
        loaderDiv.style.zIndex = '9999'; // Make sure the loader is on top of everything
        loaderDiv.innerHTML = `
            <div class="spinner-border text-primary" style="width: 3rem; height: 3rem;" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
        `;
        return loaderDiv;
    }

    function show() {
        var existingLoader = document.getElementById(loaderId);
        if (!existingLoader) {
            var loader = createLoader();
            document.body.appendChild(loader);
        }
    }

    function hide() {
        var loader = document.getElementById(loaderId);
        if (loader) {
            loader.remove();
        }
    }

    return {
        show: show,
        hide: hide
    };
})();

// Example usage:
// truelight.loader.show();
// truelight.loader.hide();
