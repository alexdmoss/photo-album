<?
include ("/secret/pass.php");
if (isset($_COOKIE['alalbumpw'])) {
//  if ($_COOKIE['alalbumpw'] != $hash) {
  if (password_verify(password_hash($_COOKIE['alalbumpw'], PASSWORD_BCRYPT), $hash)) {
    header("location:/login/");
  }
} else {
  header("location:/login/");
}
?>
