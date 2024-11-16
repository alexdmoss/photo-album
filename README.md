# photo-album

Photo Slideshow application using FastAPI + TailwindCSS + HTMX. Initial implementation learnt from [this tutorial](https://github.com/tataraba/simplesite/tree/main) - _thank you!_ - but then heavily customised to my needs.

---

## Adding Albums

Currently this isn't very slick!

1. Add a link and name the album in `photo-album/slideshow/templates/main.html`
2. Copy the images to `gs://alexos-photos/$album/processed/`
   1. It is up to you to resize the images first
   2. Use `/videos` if it is a video album instead
   3. Full-size images go into `/originals`
3. Create a copy of the template in `photo-album/slideshow/templates/$album`
   1. This creates a lot of duplicate code which is why this stuff needs sorting out!
   2. Watch for for the formatting of the photo name as a caption

---

## Bugs

- [ ] download option times out - needs progress spinner perhaps

## To Do

- [ ] Make the list of albums look better - preview, image count, etc
- [ ] Hard-coding of page titles etc
- [ ] More htmx less raw JS
- [ ] Fix the image processing stuff - currently just extracted it but not tested/fixed as out-of-band thing
- [ ] Captions that aren't the filename
- [ ] Multiple Album Support
- [ ] Default album based on who you are when sign-in

---

## Local Dev

```sh
poetry install --no-root   # one-off
export DATA_PROJECT_ID=<project-with-auth-secret+firestore>
./run-local.sh
```

> **NB:** Tailwind CSS is a post-processor - if a style is not used, you need to restart the app for it to pick it up!

Note that `./run-local.sh --docker` can also be used, which handles testing the docker container locally whilst loading the required local Google creds.
