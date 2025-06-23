$(document).ready(function () {
    // Show data in datatable
    const table = $('#data_list').DataTable({
        deferRender: true,
        responsive: true,
        serverSide: true,
        ajax: dataSourceUrl, // Defined in template
        processing: true,
        createdRow: function (row, data, dataIndex) {
            $(row).attr('data-id', data[0]);
        },
        columnDefs: [
            {
                targets: -1,
                orderable: false,
                searchable: false,
                render: function (data, type, row, meta) {
                    var detailUrl = row[row.length - 1];
                    return `<a href="${detailUrl}" class="btn btn-link text-dark" target="_blank">View More Details</a>`;
                }
            }
        ]
    });


    // update rowncount function 
    function updateRowCount() {
        const count = table.rows('.selected').data().length;
        $('#row_count').text(count + ' row(s) selected');
    }

    // Update print qr code  button 
    function updatePrintButton() {
        const count = table.rows('.selected').data().length;
        $('#print_qr_codes').prop('disabled', count === 0);
    }

    // Update print bar code 
    function updatePrintBarcodeButton() {
        const count = table.rows('.selected').data().length;
        $('#print_barcodes').prop('disabled', count === 0);
    }

    // Update print product details 
    function UpdatePrintProductDetailButton() {
        const count = table.rows('.selected').data().length;
        $('#print_product_details').prop('disabled', count === 0);
    }

    // call update buttons 
    $('#data_list tbody').on('click', 'tr', function () {
        $(this).toggleClass('selected');
        updateRowCount();
        updatePrintButton();
        updatePrintBarcodeButton();
        UpdatePrintProductDetailButton();
    });


    // toggle selected clss 
    $('#select-all').on('click', function () {
        var rows = table.rows({ 'search': 'applied' }).nodes();
        $(rows).toggleClass('selected', this.checked);
        updateRowCount();
        updatePrintButton();
        updatePrintBarcodeButton();
        UpdatePrintProductDetailButton();
    });

    // delete data 
    $('#delete-data').on('click', function (e) {
        const selectedIds = $('#data_list tbody tr.selected').map(function () {
            return $(this).data('id');
        }).get();

        if (selectedIds.length === 0) {
            Swal.fire({
                icon: 'info',
                text: "Please select desired recipients first!"
            });
        } else {
            Swal.fire({
                title: "Are you sure you want to delete the selected items?",
                text: "This action cannot be undone. Once deleted.",
                showCancelButton: true,
                confirmButtonText: "Delete",
            }).then((result) => {
                if (result.isConfirmed) {
                    Swal.fire({
                        title: 'Deleting...',
                        text: 'Please wait while we delete the selected items.',
                        allowOutsideClick: false,
                        allowEscapeKey: false,
                        didOpen: () => {
                            Swal.showLoading();
                        }
                    });
                    $.ajax({
                        url: deleteUrl, // Defined in template
                        type: 'POST',
                        data: {
                            selectedIds: selectedIds,
                            csrfmiddlewaretoken: csrfToken // Defined in template
                        },
                        success: function (response) {
                            Swal.fire({
                                position: "center",
                                icon: "success",
                                text: response.message,
                                showConfirmButton: true,
                            }).then(() => {
                                location.reload();
                            });
                        },
                        error: function () {
                            Swal.fire({
                                icon: "error",
                                title: "Oops...",
                                text: "Something went wrong!",
                            });
                        }
                    });
                }
            });
        }
    });


    // print qr codes 
    $('#print_qr_codes').on('click', function () {
        const selectedIds = $('#data_list tbody tr.selected').map(function () {
            return $(this).data('id');
        }).get();

        if (selectedIds.length === 0) {
            Swal.fire({
                icon: 'info',
                text: "Please select at least one product to print QR codes."
            });
            return;
        }

        const url = printQRCodesUrl + "?ids[]=" + selectedIds.join('&ids[]=');
        window.open(url, '_blank');
    });

    // print bar codes 
    $('#print_barcodes').on('click', function () {
        const selectedIds = $('#data_list tbody tr.selected').map(function () {
            return $(this).data('id');
        }).get();

        if (selectedIds.length === 0) {
            Swal.fire({
                icon: 'info',
                text: "Please select at least one product to print barcodes."
            });
            return;
        }

        const url = printBarcodesUrl + "?ids[]=" + selectedIds.join('&ids[]=');
        window.open(url, '_blank');
    });

    // print product details 
    $('#print_product_details').on('click', function () {
        const selectedIds = $('#data_list tbody tr.selected').map(function () {
            return $(this).data('id');
        }).get();

        if (selectedIds.length === 0) {
            Swal.fire({
                icon: 'info',
                text: "Please select at least one product to print barcodes."
            });
            return;
        }

        const url = printProductDetailsUrl + "?ids[]=" + selectedIds.join('&ids[]=');
        window.open(url, '_blank');
    });

    // Initial update
    updateRowCount();
    updatePrintButton();
    updatePrintBarcodeButton();
    UpdatePrintProductDetailButton();

});
