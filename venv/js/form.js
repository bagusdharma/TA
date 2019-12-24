function submit_query(form_data){
  var btn = $("#submit-query-btn");
  var btn_default_text = $("#submit-query-btn").text();
  var btn_loading_text = $("#submit-query-btn").attr("data-loading-text");
  var form = new FormData();
  var data = form_data.serializeArray();

  btn.prop('disabled', true);
  btn.text(btn_loading_text);
  $.each(data,function(key,input){
    if (input.value != null || input.value != ''|| input.value != undefined) {
      form.append(input.name,input.value);
    }
  });
  var runsolution = send_ajax_request('POST', 'api/runsolution.php', form);
  $.when(runsolution).done(function(responseData, textStatus){
    $("#init-success").modal("show");
    $("#tab-output").trigger("click");
    btn.text(btn_default_text);
    btn.prop('disabled', false);
  });
}

function upload_dataset(form_data){
  var btn = $("#upload-dataset-btn");
  var btn_default_text = $("#upload-dataset-btn").text();
  var btn_loading_text = $("#upload-dataset-btn").attr("data-loading-text");
  var form = new FormData();

  btn.prop('disabled', true);
  btn.text(btn_loading_text);
  form.append('dataset', $('#dataset-file')[0].files[0]);
  var uploaddataset = send_ajax_request('POST', 'api/uploaddataset.php', form);
  $.when(uploaddataset).done(function(responseData, textStatus){
    $("#upload-success").modal("show");
    btn.text(btn_default_text);
    btn.prop('disabled', false);
    update_dataset();
    update_graph();
  });
}

function update_graph(){
  var requestNodes = send_ajax_request('GET', 'session/nodes.json');
  var requestEdges = send_ajax_request('GET', 'session/edges.json');

  $.when(requestNodes, requestEdges).done(function(nodes, edges){
    renderGraph(JSON.parse(nodes[0]), JSON.parse(edges[0]));
  });
}

function update_results(){
  var requestResults = send_ajax_request('GET', 'session/web_results.json');
  $("#best-solution-loading").show();
  $("#cand-loading").show();

  var tableToRender = $("#best-solution").hide().html("");
  $.when(requestResults).done(function(responseData, textStatus){
    var response = JSON.parse(responseData)
    $.each(response[1], function(index,item){
      if (index == response[1].length-2) {
        if (item < 0.0) {
          item = 0.0;
        }
      }
      var tableRow = '<tr><th scope="row">'+response[0][index]+'</th><td>'+item+'</td></tr>'
      tableToRender.append(tableRow);
    });
    $("#best-solution-loading").hide();
    tableToRender.show();

    var tableHead = $("#cand-head").hide().html("");
    var tableBody = $("#cand-body").hide().html("");
    $.each(response, function(index,item){
      var tableRow = "<tr>";
      if (index == 0) {
        $.each(item, function(indexHead,itemHead){
          tableRow += '<th scope="col">'+itemHead+'</th>';
        });
        tableRow += "</tr>";
        tableHead.append(tableRow);
      }
      else {
        $.each(item, function(indexBody,itemBody){
          tableRow += '<td>'+itemBody+'</td>';
        });
        tableRow += "</tr>";
        tableBody.append(tableRow);
      }
    });
    $("#cand-loading").hide();
    tableHead.show();
    tableBody.show();
  });
}

function update_initialquery(){
  var requestResults = send_ajax_request('GET', 'session/countsubs_results.json');
  $("#initial-query-loading").show()
  var tableToRender = $("#initial-query").hide().html("");
  $("#initial-query-fixed").hide();
  $.when(requestResults).done(function(responseData, textStatus){
    var response = JSON.parse(responseData)
    $("#initial-query-subs").html(response["potential_subs"]);
    $.each(response["target"], function(index,item){
      if (index != "parent" && index != "label" && index != "is_root" && index != "child" && index != "visited" && index != "id") {
        var tableRow = '<tr><th scope="row">'+index+'</th><td>'+item+'</td></tr>'
        tableToRender.append(tableRow);
      }
    });
    $("#initial-query-loading").hide()
    tableToRender.show();
    $("#initial-query-fixed").show();
  });
}

function update_runtime(){
  var requestResults = send_ajax_request('GET', 'session_log/solution_manual.csv');
  $("#runtime-loading").show()
  var container = $("#runtime").hide().html("");
  $.when(requestResults).done(function(responseData, textStatus){
    var allTextLines = responseData.split(/\r\n|\n/);
    var entries = allTextLines[allTextLines.length-2].split(',');
    var runtime = "Program selesai dengan waktu eksekusi: <b>"+entries[12]+"</b>";
    container.html(runtime);
    $("#runtime-loading").hide();
    container.show();
  });
}

function update_dataset(){
  var requestResults = send_ajax_request('GET', 'dataset.csv');
  $("#dataset-loading").show();
  var tableHead = $("#dataset-head").hide().html("");
  var tableBody = $("#dataset-body").hide().html("");
  $.when(requestResults).done(function(responseData, textStatus){
    var allTextLines = responseData.split(/\r\n|\n/);
    $.each(allTextLines, function(index,item){
      var entries = item.split(',');
      var tableRow = "<tr>";
      if (index == 0) {
        $.each(entries, function(indexHead,itemHead){
          tableRow += '<th scope="col">'+itemHead+'</th>';
        });
        tableRow += "</tr>";
        tableHead.append(tableRow);
      }
      else {
        $.each(entries, function(indexBody,itemBody){
          tableRow += '<td>'+itemBody+'</td>';
        });
        tableRow += "</tr>";
        tableBody.append(tableRow);
      }
    });
    $("#dataset-loading").hide();
    tableHead.show();
    tableBody.show();
  });
}
