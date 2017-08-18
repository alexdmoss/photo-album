<?php

function initGCS() {

  require_once 'vendor/autoload.php';

  $serviceAccount	 = "photo-album@moss-work.iam.gserviceaccount.com";
  $scopes = array('https://www.googleapis.com/auth/devstorage.read_write');

  $client = new Google_Client();
  $client->setAuthConfig('/secret/moss-work-photo-album.json');
  $client->setSubject($serviceAccount);
  $client->setScopes($scopes);

  return new Google_Service_Storage($client);

}

function listGCS($storage, $dir) {

  $files = array();
  $bucket = "wedding-photos-bkt";

  $listObjects = $storage->objects->listObjects($bucket,
    array(
      "prefix" => $dir,
      "delimiter" => "cover.jpg"
    )
  );
  $items = $listObjects->getItems();

  foreach ($items as $item) {
    if ((!empty($item["name"])) && (preg_match("/.jpg/i", $item["name"]))) {
      $files[] = $item["name"];
    }
  }

  return $files;

}

function fastscan($dir) {
  $files = array();
  $dirHandle = opendir($dir);
    while ($file = readdir($dirHandle)) {
      if (($file != ".") && ($file != "..")) {
        $files[] = $file;
      }
    }
  closedir($dirHandle);
  return $files;
}

function make_thumb($src, $dest, $desired_width) {
  $ext = pathinfo($src, PATHINFO_EXTENSION);
  if (($ext == "png") || ($ext == "PNG")) {
    $source_image = imagecreatefrompng($src);
    $width = imagesx($source_image);
    $height = imagesy($source_image);
    $desired_height = floor($height * ($desired_width / $width));
    $virtual_image = imagecreatetruecolor($desired_width, $desired_height);
    imagecopyresampled($virtual_image, $source_image, 0, 0, 0, 0, $desired_width, $desired_height, $width, $height);
    imagepng($virtual_image, $dest);
  } elseif (($ext == "jpg") || ($ext == "JPG") || ($ext == "jpeg") || ($ext == "JPEG")) {
    $source_image = imagecreatefromjpeg($src);

    $exif = exif_read_data($src);
    if(!empty($exif['Orientation'])) {
      switch($exif['Orientation']) {
        case 1: // nothing
        break;
        case 2: // horizontal flip
          $source_image = imageflip($source_image, IMG_FLIP_HORIZONTAL);
          error_log("flipping ".$src." horizontal for ".$desired_width);
        break;
        case 3: // 180 rotate left
          $source_image = imagerotate($source_image,180,0);
          error_log("rotating ".$src." +180 for ".$desired_width);
        break;
        case 4: // vertical flip
          $source_image = imageflip($source_image, IMG_FLIP_VERTICAL);
          error_log("flipping ".$src." vertical for ".$desired_width);
        break;
        case 5: // vertical flip + 90 rotate right
          $source_image = imageflip($source_image, IMG_FLIP_VERTICAL);
          $source_image = imagerotate($source_image,-90,0);
          error_log("rotating ".$src." -90 and flipping vertical for ".$desired_width);
        break;
        case 6: // 90 rotate right
          $source_image = imagerotate($source_image,-90,0);
          error_log("rotating ".$src." -90 for ".$desired_width);
        break;
        case 7: // horizontal flip + 90 rotate right
          $source_image = imageflip($source_image, IMG_FLIP_HORIZONTAL);
          $source_image = imagerotate($source_image,-90,0);
          error_log("rotating ".$src." -90  and flipping horizontal for ".$desired_width);
        break;
        case 8:    // 90 rotate left
          $source_image = imagerotate($source_image,90,0);
          error_log("rotating ".$src." +90 for ".$desired_width);
        break;
      }
    }

    $width = imagesx($source_image);
    $height = imagesy($source_image);
    $desired_height = floor($height * ($desired_width / $width));
    $virtual_image = imagecreatetruecolor($desired_width, $desired_height);
    imagecopyresampled($virtual_image, $source_image, 0, 0, 0, 0, $desired_width, $desired_height, $width, $height);
    imagejpeg($virtual_image, $dest);
  }
}

function getFileType( $file ) {
   return image_type_to_mime_type(exif_imagetype($file));
}

?>
