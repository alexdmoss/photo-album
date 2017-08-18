<?php
include ("/secret/pass.php");
$pw = $_POST['alalbumpw'];
$pw = stripslashes($pw);
if($pw == $password) {
    setcookie(
      'alalbumpw',
      password_hash($sessionKey, PASSWORD_BCRYPT),
      time()+3600,
      "/",
      "alexandlou.co.uk",
      false,
      true);
    header("location:/albums/");
} else {
    header("location:/wrong/");
}
?>
