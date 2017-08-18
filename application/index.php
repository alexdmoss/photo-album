<?
include("secureIt.php");
include("functions.php");
$GCS_BASE_URL = "https://storage.googleapis.com/wedding-photos-bkt";
$albums       = array(
                  "1-the-wedding",
                  "2-photo-booth",
                  "3-photos-from-emily",
                  "4-honeymoon",
                  "5-october-preshoot"
                );
$storObj      = initGCS();
?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" class="wf-active js flexbox webgl no-touch geolocation rgba hsla multiplebgs backgroundsize borderimage borderradius boxshadow textshadow opacity cssanimations csscolumns cssgradients cssreflections csstransforms csstransforms3d csstransitions fontface generatedcontent video svg inlinesvg smil svgclippaths boxsizing csscalc lastchild mediaqueries cssvwunit cssvhunit cssremunit pointerevents no-ie8compat">
 <head>

  <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
	<meta http-equiv="X-UA-Compatible" content="IE=edge">
  <meta name="author" content="Alex Moss, London, GB">
  <meta name="keywords" content="">
  <meta name="description" content="Alex and Louise got married on 22nd April, 2017!">
  <meta name="robots" content="all">
  <meta name="viewport" content="width=device-width, initial-scale=1">
	<meta name="format-detection" content="telephone=no" />

  <title>Photo Gallery - Louise &amp; Alex</title>

  <link rel="shortcut icon" href="/images/favicon.ico">
  <link type="text/css" rel="stylesheet" href="/css/screen-v2.css" />
  <link href="https://fonts.googleapis.com/css?family=Alex+Brush" rel="stylesheet">
  <link href="https://fonts.googleapis.com/css?family=Open+Sans" rel="stylesheet">
  <link type="text/css" rel="stylesheet" href="/css/lightgallery.css" />
  <style type="text/css">
    .lg-outer { background-color: #CCE0FF; }
    .lg-toolbar { background-color: rgba(0, 0, 0, 0.3); color: red; }
    .lg-toolbar .lg-icon { color: #44273B; }
    .lg-actions .lg-next, .lg-actions .lg-prev { background-color: #CCE0FF; color: #44273B; }
    .lg-actions .lg-next:hover, .lg-actions .lg-prev:hover { color: #5982DB; }
    .lg-outer .lg-thumb-item.active, .lg-outer .lg-thumb-item:hover { border-color: #44273B; }
    .lg-progress-bar .lg-progress { background-color: #44273B; }
    .lg-sub-html { background-color: rgba(0, 0, 0, 0.3); }
    .lg-outer .lg-thumb-outer { background-color: rgba(0, 0, 0, 0.3); }
    .lg-outer .lg-toogle-thumb { background-color: rgba(0, 0, 0, 0.3); }
  </style>

  <script type="text/javascript" src="/js/jquery-2.1.1.min.js"></script>

  <!-- A jQuery plugin that adds cross-browser mouse wheel support. (Optional) -->
  <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery-mousewheel/3.1.13/jquery.mousewheel.min.js"></script>

  <script type="text/javascript" src="/js/imagesloaded.pkgd.min.js"></script>
  <script type="text/javascript" src="/js/picturefill.min.js"></script>
  <script type="text/javascript" src="/js/lightgallery.min.js"></script>
  <script type="text/javascript" src="/js/lg-autoplay.min.js"></script>
  <script type="text/javascript" src="/js/lg-fullscreen.min.js"></script>
  <script type="text/javascript" src="/js/lg-thumbnail.min.js"></script>
  <script type="text/javascript" src="/js/lg-zoom.min.js"></script>
  <script type="text/javascript" src="/js/jquery.montage.min.js"></script>
  <script type="text/javascript" src="/js/jquery.innerfade.js"></script>

  <!-- Analytics -->
  <script type="text/javascript" src="/js/ga.js"></script>
  <script>
    (function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
    (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
    m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
    })(window,document,'script','https://www.google-analytics.com/analytics.js','ga');
    ga('create', 'UA-86314861-1', 'auto');
    ga('send', 'pageview');
  </script>

 </head>

 <body>
   <div id="content-load">
    <div id="main" class="main" role="main" style="display: block;">
     <div id="wrapper">
      <div class="content-section blue" id="gallery">

       <div class="content-container">
        <article class="article">
        	<h3><a href="/">Alex &amp; Louise's Wedding Photos!</a></h3>
        	<div class="box">
        	 <ul>
        	  <li>
        		 <div class="box-content">
              <?
              if (isset($_GET['album'])) {
                  $images = array();
                  $album = $_GET['album'];
                  $files = listGCS($storObj, "photos/".$album);
                  foreach ($files as $file) {
                    $ext = pathinfo($file, PATHINFO_EXTENSION);
                    if (($ext == "jpg") || ($ext == "JPG")) {
                      $images[] = basename($file);
                    }
                  }
                  print ("<div class=\"back\"><a href=\"/albums/\">&laquo; Back to Albums</a></div>\n");
                  print ("<div id=\"lightgallery\">\n");
                  foreach ($images as $image) {
                    $caption = str_replace("_", ": ", str_replace(".jpg", " ", str_replace(".JPG", " ", $image)));
                    ?>
                    <a data-download-url="<?=$GCS_BASE_URL."/photos/".$album."/".$image;?>" href="<?=$GCS_BASE_URL."/display/".$album."/".$image;?>">
                     <img src="<?=$GCS_BASE_URL."/thumbs/".$album."/".$image;?>" alt="<?=$caption;?>" title="<?=$caption;?>" />
                    </a>
                    <?
                  }
                  print ("</div>\n");
                  print ("<div class=\"back\"><a href=\"/albums/\">&laquo; Back to Albums</a></div>\n");
              } else { // not viewing an album ?>
              <div class="albums">

                <div class="albumsContainer">
                <?
                 if (!empty($albums)) {
                   foreach ($albums as $album) {
                     $cover = $GCS_BASE_URL."/thumbs/".$album."/cover.jpg";
                       ?>
                       <div class="albumsCard">
                         <a href="/album/<?=$album;?>/"><img src="<?=$cover;?>" alt="<?=$album;?>" title="<?=$album;?>" border="0" /><br /><?=preg_replace("/(\d+) /", "$1. ", ucwords(str_replace("-", " ", $album)));?></a>
                         <br />
                         <a class="download" href="<?=$GCS_BASE_URL;?>/download/<?=$album;?>.zip"><span class="icon-downloadbutton"></span></a>
                       </div>
                       <?
                    }
                  ?>
                  </div>

                  <div class="help">
                   <p>
                    Click on one of the albums above to be taken to the full set of those photos.
                    From there you can select either individual photos or play through the whole lot!
                   </p>
                   <p>
                    If you want to download and keep a copy you can do one of the following:</p>
                    <ul>
                     <li>While viewing a photo, hit the download icon (<span class="icon-downloadbutton"></span>) in the top-right to grab the full resolution picture you like</li>
                     <li>To grab the whole set, click the download icon underneath each album below.</li>
                     <li>Note that these are large images - there's several GB of photos so it'll chew up a lot of space!</li>
                    </ul>
                   </p>
                  </div>
                <? } else { print ("No albums are currently available on the site"); } ?>
              <? } ?>
            </div>
       		 </div>
       		</li>
       	 </ul>
       	 <br class="clearfloat">
       	</div>
       </article>
      </div>
     </div>
    </div>
   </div>
  </div>

  <script type="text/javascript">

  $(function() {

    var $container 	= $('#wrapper'),
        $imgs	      = $container.find('img').hide(),
        totalImgs	  = $imgs.length,
        cnt			    = 0;

    $imgs.each(function(i) {
      var $img	= $(this);
      $('<img/>').load(function() {
        ++cnt;
        if( cnt === totalImgs ) {
          $imgs.show();
          $container.montage({
            liquid	: true,
            minsize	: true,
            margin 	: 0
          });
        }
      }).attr('src',$img.attr('src'));
    });

  });

  </script>

  <script type="text/javascript">

    $(document).ready(function() {
        $("#lightgallery").lightGallery({
          mode: 'lg-fade',
          cssEasing: 'ease',
          easing: 'linear',
          keyPress: true,
          escKey: true,
          hideBarsDelay: 3000,
          pullCaptionUp: true,
          actualSize: true,
          fullScreen: true,
          zoom: false,
          thumbnail: true,
          animateThumb: true,
          thumbMargin: 3
        });
    });

  </script>

 </body>
</html>
