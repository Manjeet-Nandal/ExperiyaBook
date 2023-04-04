
function filterPolicy() {
    // document.getElementsByClassName("showMoreNew")[0].click();

    try {
        payout_switch = document.getElementById('payout_switch').checked
        if (payout_switch) {
            filterPolicy_nopayout();
            return;
        }

        start_date = document.getElementById('frmDate').value.toString()
        end_date = document.getElementById('toDate').value.toString()
        period_value = document.getElementById('select-period').value.toString().toUpperCase()
        select_length = document.getElementById('select_length').value

        if (period_value == "LAST_MONTH") {
            period_value = "LAST MONTH"
        }
        else if (period_value == "THIS_MONTH") {
            period_value = "THIS MONTH"
        }
        else if (period_value == "CURRENT_YEAR") {
            period_value = "CURRENT YEAR"
        }

        if (start_date == "" || end_date == "") {
            return
        }
        start_date = start_date.replace("/", "*")
        start_date = start_date.replace("/", "*")

        end_date = end_date.replace("/", "*")
        end_date = end_date.replace("/", "*")

        try {
            index = window.location.href.indexOf("*")
            if (index > 0) {
                // window.location.reload()
                hostname = window.location.hostname
                port = window.location.port
                pathname = '/bima_policy/policy/entry/'

                href = window.location.origin + pathname + start_date + '/' + end_date + '/' + period_value + '/' + select_length

                window.location.replace(href)
            }
            else {
                href = window.location.href + start_date
                href += "/"
                href += end_date
                href += "/"
                href += period_value
                href += "/"
                href += select_length

                window.location.replace(href)
            }
        } catch (error) {

        }

    } catch (error) { }
}

function filterPolicy_nopayout() {
    // document.getElementsByClassName("showMoreNew")[0].click();
    try {
        payout_switch = document.getElementById('payout_switch').checked
        if (payout_switch) {

            start_date = document.getElementById('frmDate').value.toString()
            end_date = document.getElementById('toDate').value.toString()
            period_value = document.getElementById('select-period').value.toString().toUpperCase()
            select_length = document.getElementById('select_length').value

            if (period_value == "LAST_MONTH") {
                period_value = "LAST MONTH"
            }
            else if (period_value == "THIS_MONTH") {
                period_value = "THIS MONTH"
            }
            else if (period_value == "CURRENT_YEAR") {
                period_value = "CURRENT YEAR"
            }

            if (start_date == "" || end_date == "") {
                return
            }
            start_date = start_date.replace("/", "*")
            start_date = start_date.replace("/", "*")

            end_date = end_date.replace("/", "*")
            end_date = end_date.replace("/", "*")

            try {
                index = window.location.href.indexOf("*")
                if (index > 0) {
                    // window.location.reload()
                    hostname = window.location.hostname
                    port = window.location.port
                    pathname = '/bima_policy/policy/entry/'
                    href = window.location.origin + pathname + start_date + '/' + end_date + '/' + period_value + '/' + select_length + '/' + 'true'
                    window.location.replace(href)
                }
                else {
                    href = window.location.href + start_date
                    href += "/"
                    href += end_date
                    href += "/"
                    href += period_value
                    href += "/"
                    href += select_length
                    href += "/"
                    href += 'true'

                    window.location.replace(href)
                }
            } catch (error) {

            }
        }
    } catch (error) { }
}

function selectAllPolicy() {

    var tblInsurance = document.getElementById('tblInsurance')
    var rowLength = tblInsurance.rows.length;
    chkblkrm_isChecked = document.getElementById('chkblkrm').checked
    tr = tblInsurance.getElementsByTagName("tr");

    ids = ''

    if (chkblkrm_isChecked) {
        for (i = 1; i < rowLength; i++) {
            id = `chkblkrm${i}`
            document.getElementById(id).checked = true
            highlight(tr[i])
        }
    }
    else {
        for (i = 1; i < rowLength; i++) {
            id = `chkblkrm${i}`
            document.getElementById(id).checked = false
            highlight(tr[i])
        }
    }
}

function bulk_policy_remove() {
    alert('i am callind')

    var tblInsurance = document.getElementById('tblInsurance')
    var rowLength = tblInsurance.rows.length;
    ids = ''

    for (i = 1; i < rowLength; i++) {

        id = `chkblkrm${i}`

        isChecked = document.getElementById(id).checked

        if (isChecked) {

            ids += '|' + tblInsurance.rows.item(i).cells[2].innerText.trim()
            // document.getElementById(anchor_id).click();
        }
    }
    pathname = `/bima_policy/policy/${ids}/delete`

    window.location.replace(window.location.origin + pathname)
}

function resertDocument() {
    document.location.reload()
}

function highlight(row) {
    SelectedRow = row.cells[0].textContent;
    deHighlight();
    row.style.backgroundColor = 'silver';
    row.classList.toggle("selectedRow");
}

function deHighlight() {
    let table = document.getElementById("tblInsurance");
    let rows = table.rows;
    for (let i = 0; i < rows.length; i++) {
        // to avoid checked 
        try {
            is_checked = document.getElementById(`chkblkrm${i}`).checked
            if (is_checked) {
                continue;
            }
        } catch { }

        // default this line is
        rows[i].style.backgroundColor = "transparent";
    }
}

function searchName() {
    // Declare variables
    var input, filter, table, tr, td, i, txtValue;
    input = document.getElementById("myInput");
    filter = input.value.toUpperCase();
    table = document.getElementById("tblInsurance");
    tr = table.getElementsByTagName("tr");

    // Loop through all table rows, and hide those who don't match the search query
    for (i = 0; i < tr.length; i++) {
        td = tr[i].getElementsByTagName("td")[4];
        if (td) {
            txtValue = td.textContent || td.innerText;
            if (txtValue.toUpperCase().indexOf(filter) > -1) {
                tr[i].style.display = "";
            } else {
                tr[i].style.display = "none";
            }
        }
    }
}

function ExportToExcel(type, fn, dl) {
    var elt = document.getElementById('tblInsurance');
    var wb = XLSX.utils.table_to_book(elt, { sheet: "sheet1" });
    return dl ?
        XLSX.write(wb, { bookType: type, bookSST: true, type: 'base64' }) :
        XLSX.writeFile(wb, fn || ('MySheetName.' + (type || 'xlsx')));
}