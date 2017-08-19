
---
Alex Moss, 2017-08-18
---

# Introduction

A PhotoAlbum built in PHP and fronted by NGINX. Both components are in Docker containers.

The solution is designed to run in Kubernetes within GCP, with docker-compose file also included. The Google-specific elements are relatively minimal - relying on Google Cloud Storage for the image storage and GCE's load balancers. Note that in the case of GCS this is also baked into the code to source the images directly from GCS to the client.

I did muck around with GKE's persistentdisk options, but couldn't get this to work reliably with the pods moving around. I had a brief dabble with NFS to sort out the mess but this also felt a bit overkill for now.

I also tried mounting the GCS bucket on each pod which worked (used gcsfuse - pretty cool!) - but performance was horrendous, particularly listing directories. With the large number of images involved this wasn't great!

Loading the images on the glass, with a bit of API calling to build the list, just seemed an easier way to go for read-only assets - although I had to sacrifice the code I had in place which auto-built the thumbnails (this is now in build.php if you want to run it locally ...).

Maybe a future enhancement is to use Google's Vision API within AppEngine to do it instead ... ;)

---

# How To Use

## Initial Setup

These initial setup instructions assume you are running on Google's Container Engine (GKE) and using Google Cloud Storage (GCS).

For first-time set up, you must be authenticated to access your GKE cluster (which in my case was already created - there are plenty of guides out there on this if needed). This is done through `gcloud auth login`.

The namespace used throughout is 'photo-album' - you will need to update this in all four .yml files in the k8s/ directory if you wish to use something different.

1. Create your namespace:

      `kubectl apply -f ./k8s/create-namespace.yml`

2. [optional] Create a static IP for your GCP load balancer (the ingress) to use

      `gcloud compute addresses create photo-album-ip --global`

      If you skip this step, then you should remove the line containing 'global-static-ip-name:' in the create-ingress.yml. You will then get an ephemeral IP (which is held as long as you don't delete and recreate your ingress).

3. Create your ingress, which uses GCP Load Balancing:

      `kubectl apply -f ./k8s/create-ingress.yml`

4. Create your GCS bucket:

      `gsutil mb -p ${GCP_PROJECT}  -l ${GCP_REGION} -c regional gs://${GCP_BUCKET_NAME}/`
      `gsutil iam ch allUsers:objectViewer gs://{GCP_BUCKET_NAME}`

      GCP_PROJECT and GCP_REGION must match where you want it defined. GCP_BUCKET_NAME is your choice, but must match what is in config/var.sh.

      If you don't want to make all objects in the bucket public, you can target individual files:

      `gsutil acl ch -u AllUsers:R gs://{[GCS_BUCKET_NAME}/{OBJECT_NAME}`

## Adding an Album

Preparing an album locally is recommended. Due to the horrendous performance of GCS when mounted to the container, I stripped away the self setup of a new album.

Your folder structure for a new album should be as follows:

    `{GCS_BUCKET_NAME}/photos/{ALBUM-NAME}`  - your full-size images - available through the download button
    `{GCS_BUCKET_NAME}/thumbs/{ALBUM-NAME}`  - small thumbnails - I used 100 pixel wide
    `{GCS_BUCKET_NAME}/display/{ALBUM-NAME}` - medium sized images - what is displayed in the gallery

You should also place an image called cover.jpg inside the thumbs/{ALBUM-NAME}/ folder - this is the image used on the page that lists all the albums. It does not need a full-size/display-size image and is ignored when listing the folder contents.

If you don't want to use GCS, then you can mount volumes locally by adding lines to docker-compose.yml:

    `/path/to/photos:/data/photos`
    (repeat for thumbs/ and display/)

This is a good option when you're using build.php to generate your thumbnails - although keep in mind that index.php is coded to source images from the GCS bucket.

---

# TODO:

## Bugs

1. Zoom options in LightGallery are broken - disabled for now

## Nice-to-have

1. envsubst for e.g. namespace and version in k8s yaml
2. Slicker way to perform data uploads
