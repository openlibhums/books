<script>
document.addEventListener('DOMContentLoaded', function () {
    var toggleButtons = document.querySelectorAll('.toggle-description');
    var descriptionContents = document.querySelectorAll('.description-content');

    toggleButtons.forEach(function (toggleButton, index) {
        var descriptionContent = descriptionContents[index];
        var expanded = false;

        // Apply initial styles
        descriptionContent.style.maxHeight = '90px';
        descriptionContent.style.overflow = 'hidden';
        descriptionContent.style.transition = 'max-height 0.5s ease-out';

        // Defer height measurement to allow fonts/images/layout to load
        requestAnimationFrame(function () {
            requestAnimationFrame(function () {
                var fullHeight = descriptionContent.scrollHeight;

                // Store the full height in a data attribute
                descriptionContent.dataset.fullHeight = fullHeight + 'px';

                // Hide the toggle button if content is short
                if (fullHeight <= 90) {
                    toggleButton.style.display = 'none';
                }
            });
        });

        toggleButton.addEventListener('click', function (e) {
            e.preventDefault();

            if (expanded) {
                descriptionContent.style.maxHeight = '90px';
                toggleButton.textContent = 'Read more';
            } else {
                var fullHeight = descriptionContent.dataset.fullHeight || '1000px';
                descriptionContent.style.maxHeight = fullHeight;
                toggleButton.textContent = 'Show less';
            }

            expanded = !expanded;
        });
    });
});
</script>
