# photo-album

Photo Slideshow application using FastAPI + TailwindCSS + HTMX. Initial implementation learnt from [this tutorial](https://github.com/tataraba/simplesite/tree/main) - _thank you!_ - but then heavily customised to my needs.

---

## Adding Albums

Currently this isn't very slick!

1. Create the album document in the `albums` collection - copying an existing one's fields is easiest here
2. Copy the images to `gs://alexos-photos/$album/processed/`
   1. It is up to you to resize the images first
   2. Calling the files `YYYY-MM-DD.rest` or `YYYY.MM.DD (rest)` will format the date
   3. Ensure you set a `cover.jpg` or specify a different image when configuring the album
   4. Use `/videos` if it is a video album instead
   5. Full-size images can be kept in `/originals`, but are not used currently

## Adding Users

They go in the `users` collection, with `photo-album` added to the array of apps they are allowed access to. Don't forget they need granting access to the relevant `albums`.

---

## Bugs

- [ ] download option times out - needs progress spinner perhaps

## To Do

- [x] Image count for albums
- [x] Show whether an album is photo or video
- [x] "Likes" to help see which are popular for e.g. printing/physical album
- [x] Hard-coding of page titles etc
- [ ] More htmx less raw JS
- [ ] Fix the image processing stuff - currently just extracted it but not tested/fixed as out-of-band thing
- [ ] Adding albums is a pain - fix this the next time you create one

### Nice To Have

- [ ] Likes could persist beyond the visit. Currently is storing user but not handling via session storage / unlike
- [ ] Captions that aren't the filename. This requires storing info about the images I think - we handle dates already

---

## Local Dev

```sh
poetry install --no-root   # one-off
export DATA_PROJECT_ID=<project-with-auth-secret+firestore>
./run-local.sh
```

> **NB:** Tailwind CSS is a post-processor - if a style is not used, you need to restart the app for it to pick it up!

Note that `./run-local.sh --docker` can also be used, which handles testing the docker container locally whilst loading the required local Google creds.
