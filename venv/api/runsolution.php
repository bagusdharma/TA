<?php
  $q = $_POST["q"];
  if ($_POST["w"] == "") {
    $w = "auto";
  }
  else {
    $w = $_POST["w"];
  }
  $k = $_POST["k"];
  $algo = $_POST["algo"];
  chdir("../");
  $cmd = './proxy_script_runsolution.sh '.$q.' '.$algo.' '.$k.' '.$w.' 2>&1';
  $output = shell_exec($cmd);
  echo $output;
  echo $cmd;
  echo getcwd();
