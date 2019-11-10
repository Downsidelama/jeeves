function refresh_table() {
    $.ajax({
        url: window.location.href,
        type: "POST",
        dataType: "json",
    }).done(
        function (data) {
            console.log(data);
            for (let i = 0; i < data.length; ++i) {
                let current_data = data[i];
                let current_row = $("#row-" + current_data['pk']);
                if (current_row.length) {
                    let row_class = "alert-warning";
                    if (current_data['status'] === "Success") {
                        row_class = "alert-success";
                    } else if (current_data['status'] === "Failed") {
                        row_class = "alert-danger";
                    }

                    if (!current_row.hasClass(row_class)) {
                        current_row.removeClass().addClass("alert").addClass(row_class);
                    }
                }

                let current_progress = $("#progress-" + current_data['pk']);
                let current_progress_bar = $("#progress_bar-" + current_data['pk']);
                if (current_progress.length && current_progress_bar.length) {
                    current_progress.html(current_data['progress'] + "%");
                    current_progress_bar.css("width", current_data['progress'] + "%");
                }

                let current_status = $("#status-" + current_data['pk']);
                if (current_status.length) {
                    if (current_status.html() !== current_data['status']) {
                        current_status.html(current_data['status']);
                    }
                }

                let elapsed_time = $("#elapsed_time-" + current_data['pk']);
                if (elapsed_time.length) {
                    let current_elapsed_time = current_data['elapsed_time'].replace(" ago", "");
                    let new_elapsed_time = "<i class=\"fe fe-clock mr-2\"></i> " + current_elapsed_time;
                    if (elapsed_time.html() !== new_elapsed_time) {
                        elapsed_time.html(new_elapsed_time);
                    }
                }

                let created_at_hr = $("#created_at_hr-" + current_data['pk']);
                if (created_at_hr.length) {
                    let new_created_at_hr = "<i class=\"fe fe-calendar mr-2\"></i> " + current_data['created_at_hr'];
                    if (created_at_hr.html() !== new_created_at_hr) {
                        created_at_hr.html(new_created_at_hr);
                    }
                }
            }
        }
    );

    setTimeout(refresh_table, 5000);
}


requirejs(['jquery'], function ($) {
    $(document).ready(
        function () {
            refresh_table();
        }
    );
});
