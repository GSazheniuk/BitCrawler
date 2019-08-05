function listen2Queue() {
    var xhr = new XMLHttpRequest();
    var lastLoaded = 0;
    xhr.open("GET", "/queue", true);
    xhr.onprogress = function (a) {
      s = xhr.responseText.substr(lastLoaded, a.loaded - lastLoaded).replace(/}{/g, "}|{").split("|");
      for (var k=0; k<s.length;k++){
          queue = JSON.parse(s[k])["queue"];
          if (!(queue instanceof Array)) {
            queue = [queue];
          }

          for (var i=0; i<queue.length;i++){
            let c = queue[i];
            if (c["status"] == "QUEUED"){
                w = c["wallet"];
                $("#items_list tbody").append(
                    $("<tr itemId='" + w["address"] + "'>"
                    + " <td>" + w["address"] + "</td>"
                    + " <td class='last_date'> </td>"
                    + " <td class='balance'> </td>"
                    + " <td class='trn_in'> </td>"
                    + " <td class='trn_out'> </td>"
                    + " <td>"
                    + "<img src='/static/spinner.svg' class='spinner' style='' />"
                    + " </td>"
                    + "</tr>"));
                $("tr[itemid='" + w["address"] + "']").find(".spinner").show();
            }

            if (c["status"] == "DONE"){
                w = c["wallet"];
                $("tr[itemid='" + w["address"] + "']").find(".spinner").hide();
                $("tr[itemid='" + w["address"] + "']").find(".last_date").text(w["lt"]);
                $("tr[itemid='" + w["address"] + "']").find(".balance").text(w["b"]);
                $("tr[itemid='" + w["address"] + "']").find(".trn_in").text(w["t_r"]);
                $("tr[itemid='" + w["address"] + "']").find(".trn_out").text(w["t_s"]);
            }
          }
      }
      lastLoaded = a.loaded;
    };
    xhr.send();
}

function getItems() {
    $.ajax({
        type: "GET",
        contentType: "application/json; charset=utf-8",
        url: "/getIds",
        dataType: "json",
        success: function (r) {
            $("#items_list tbody").empty();

            r.forEach(function (a) {
                $("#items_list tbody").append(
                    $("<tr itemId='" + a.address + "'>"
                    + " <td>" + a.address + "</td>"
                    + " <td class='last_date'>" + a.lt + "</td>"
                    + " <td class='last_date'>" + a.b + "</td>"
                    + " <td class='last_date'>" + a.t_r + "</td>"
                    + " <td class='last_date'>" + a.t_s + "</td>"
                    + " <td>"
                    + "<img src='/static/spinner.svg' class='spinner' style='display:none' />"
                    + " </td>"
                    + "</tr>"));
            });
        },
        error: function (message) {
            console.error("error has occurred");
            console.error(message);
        }
    });
}

$(document).ready(function(){
    getItems();
    listen2Queue();
});