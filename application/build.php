<?
require_once("functions.php");
$baseDir = "photos";
$albums = fastscan($baseDir);
if (!empty($albums)) {
  foreach ($albums as $album) {
     print ("<hr /><p>Working with album: ".$album."</p>");
     $images = array();
     $i = 0;
     $dir = $baseDir."/".$album;
     $files = fastscan($dir);
     if (!is_dir($dir."/".$album."/display")) { mkdir($dir."/".$album."/display", 0750); }
     if (!is_dir($dir."/".$album."/thumbs")) { mkdir($dir."/".$album."/thumbs", 0750); }

     foreach ($files as $file) {
       if (is_file($dir."/".$file)) {
         $file_type = getFileType($dir."/".$file);
         if ( strpos( $file_type, 'image' ) !== false ) {
           print ("<p>Working with image: ".$file."</p>");
           $images[] = $file;
           if (!file_exists($dir."/display/".$file)) {
             print ("<p>Creating: ".$dir."/display/".$file."</p>");
             make_thumb($dir."/".$file, $dir."/display/".$file, 700);
           }
           if (!file_exists($dir."/thumbs/".$file)) {
             print ("<p>Creating: ".$dir."/thumbs/".$file."</p>");
             make_thumb($dir."/".$file, $dir."/thumbs/".$file, 100);
           }
         }
       }
     }
  }
}
?>
