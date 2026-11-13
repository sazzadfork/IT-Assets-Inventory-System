function confirmDelete() {
    return confirm("Are you sure you want to delete this asset?");
}


function filterAssets() {

    const searchInput = document.getElementById("searchInput");
    const departmentFilter = document.getElementById("departmentFilter");
    const statusFilter = document.getElementById("statusFilter");
    const table = document.getElementById("assetTable");

    if (!searchInput || !departmentFilter || !statusFilter || !table) {
        return;
    }

    const searchText = searchInput.value.toLowerCase().trim();
    const department = departmentFilter.value.toLowerCase().trim();
    const status = statusFilter.value.toLowerCase().trim();

    const rows = table.querySelectorAll("tbody tr");

    rows.forEach(function(row) {

        // No-data row হলে বাদ দাও
        if (row.cells.length < 8) {
            return;
        }

        const rowText = row.innerText.toLowerCase();

        // Department = 6th column
        const departmentText =
            row.cells[5].innerText.toLowerCase().trim();

        // Status = 7th column
        const statusText =
            row.cells[6].innerText.toLowerCase().trim();


        const searchMatch =
            searchText === "" ||
            rowText.includes(searchText);


        const departmentMatch =
            department === "" ||
            departmentText === department;


        const statusMatch =
            status === "" ||
            statusText === status;


        if (
            searchMatch &&
            departmentMatch &&
            statusMatch
        ) {

            row.style.display = "";

        } else {

            row.style.display = "none";

        }

    });

}