# photo-album

Photo Slideshow application using FastAPI + TailwindCSS + HTMX. Initial implementation learnt from [this tutorial](https://github.com/tataraba/simplesite/tree/main) - _thank you!_ - but then heavily customised to my needs.

---

## To Do

- [x] Resize images to fit browser window
- [x] Clean up look and feel
- [x] Load images from Google Storage
- [x] OAuth sign-in
- [x] Download all photos option
- [-] _this was annoying_ Snazzy transitions
- [x] Option to configure speed of carousel
- [x] Option to stop/start carousel
- [x] Get running in Cloud Run
- [x] The post-processing is annoying - maybe we can get rid of the resizing completely?
- [x] Home Page content
- [x] Clean up logging implementation - lot of duplication
- [ ] Handling video
- [x] Download final set of images and make sure rotation/sizing is correct
- [x] Home link styling
- [x] Move controls to top-right

## Bugs

- [ ] Slow startup. Why?
- [ ] prev/next is not always stopping the slideshow
- [ ] left/right/space keybinds
- [ ] download option times out - needs progress spinner perhaps
- [x] Not sure image sizing is quite right - padding and move things around?
- [x] Direct user to log in instead of just showing error message when times out / going direct to photos?
- [ ] FontAwesome sourced locally
- [ ] Need to test behaviour when slow internet

## Futures

- [ ] Fix the image processing stuff - currently just extracted it but not tested/fixed as out-of-band thing
- [ ] Captions that aren't the filename
- [ ] Multiple Album Support
- [ ] Default album based on who you are when sign-in

---

## Local Dev

```sh
poetry install --no-root
export AUTH_PROJECT_ID=<project-with-auth-secret>
./run-local.sh
```

> **NB:** Tailwind CSS is a post-processor - if a style is not used, you need to restart the app for it to pick it up!

Note that `./run-local.sh --docker` can also be used, which handles testing the docker container locally whilst loading the required local Google creds.
