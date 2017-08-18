<?
unset($_COOKIE["alalbumpw"]);
setcookie("alalbumpw", "null", time() - 3600);
header("location:/");
?>
