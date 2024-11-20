<script>
document.addEventListener('DOMContentLoaded', function() {
    var toggleButtons = document.querySelectorAll('.toggle-description');
    var descriptionContents = document.querySelectorAll('.description-content');

    toggleButtons.forEach(function(toggleButton, index) {
        var descriptionContent = descriptionContents[index];
        var expanded = false;
        var originalHeight = descriptionContent.scrollHeight + 'px';

        // Set initial max-height for each description
        descriptionContent.style.maxHeight = '90px';
        descriptionContent.style.overflow = 'hidden';
        descriptionContent.style.transition = 'max-height 0.5s ease-out';

        // Hide the "Show More" link if content is less than or equal to 90px
        if (descriptionContent.scrollHeight <= 90) {
            toggleButton.style.display = 'none'; // Hide the button
        }

        toggleButton.addEventListener('click', function(e) {
            e.preventDefault();
            if (expanded) {
                descriptionContent.style.maxHeight = '90px'; // Collapse to initial height
                toggleButton.textContent = 'Read more';
            } else {
                descriptionContent.style.maxHeight = originalHeight; // Expand to original height
                toggleButton.textContent = 'Show less';
            }
            expanded = !expanded;
        });
    });
});
</script>
