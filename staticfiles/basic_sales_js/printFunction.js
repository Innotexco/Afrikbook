
$(document).ready(function() {
    // Function to print the content
    function printContent() {
        var contentToPrint = $('#printContent').html();
        
        // Use template literals to create the HTML structure
        var printDocument = `
            <html>
                <head>
                    <title>Print Document</title>
                    <!-- Include additional head content if needed -->
                    <link href="https://cdnjs.cloudflare.com/ajax/libs/toastr.js/latest/css/toastr.min.css" rel="stylesheet">
                    <link href="https://unpkg.com/tailwindcss@2.2.16/dist/tailwind.min.css" rel="stylesheet">
     

                </head>
                <body>
                    ${contentToPrint}
                </body>
            </html>`;
        var printWindow = window.open('', '_blank');

        printWindow.document.write(printDocument);
        printWindow.document.close();
        printWindow.print();
        printWindow.close();
    }

    // Open Modal
    $('#openModalButton').click(function() {
        var tableContent = $('#printContent').html();
        $('#modalContent').html(tableContent);
        // $('#printModal').css('display', 'block');
    });

    // Print Button in Modal
    $('#printModalContentButton').click(function() {
        // Call the printContent function when the print button is clicked in the modal
        printContent();
    });
});

