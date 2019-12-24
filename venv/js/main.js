// / Apply script after whole document is ready
$( document ).ready(function() {
  update_dataset();
  update_graph();

  $("#submit-query").submit(function(e){
    e.preventDefault();
    submit_query($(this));
  });

  $("#upload-dataset").submit(function(e){
    e.preventDefault();
    upload_dataset($(this));
  });

  $("#tab-output").click(function(){
    update_initialquery();
    update_results();
    update_runtime();
  });

});
