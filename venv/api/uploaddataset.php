<?php
$uploaddir = '../';
$file_name = "dataset";
$file = $_FILES['dataset'];

if ($file_name == NULL) {
  $file_name = underscore($file['name']);
}
else {
  $ext = pathinfo($file['name'], PATHINFO_EXTENSION);
  $file_name = $file_name.'.'.$ext;
}
$uploadfile = $uploaddir.$file_name;

if (move_uploaded_file($file['tmp_name'], $uploadfile)) {
  echo "FILE UPLOADED";
  chdir("../");
  $output = shell_exec("python graph_builder.py 999999 50 2>&1");
  echo $output;
}
else {
  echo "FAILED TO UPLOAD";
}
