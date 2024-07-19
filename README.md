# photo-album

Photo Slideshow application using FastAPI + TailwindCSS + HTMX. Initial implementation learnt from [this tutorial](https://github.com/tataraba/simplesite/tree/main) - _thank you!_ - but then heavily customised to my needs.

---

## To Do

- [x] Resize images to fit browser window
- [x] Clean up look and feel
- [x] Load images from Google Storage
- [ ] OAuth sign-in
- [x] Download all photos option
- [-] _this was annoying_ Snazzy transitions
- [x] Option to configure speed of carousel
- [x] Option to stop/start carousel
- [ ] Get running in Cloud Run
- [ ] Need to test behaviour when slow internet
- [x] The post-processing is annoying - maybe we can get rid of the resizing completely?
- [ ] Handling video
- [ ] Not sure image sizing is quite right - padding and move things around?
- [ ] Download final set of images and make sure rotation/sizing is correct
- [ ] Home Page content

## Futures

- [ ] This app might be better getting the python to do pre-processing then loading the images into nginx and serving static assets instead
- [ ] Fix the image processing stuff - currently just extracted it but not tested/fixed as out-of-band thing
- [ ] Captions that aren't the filename
- [ ] Multiple Album Support
- [ ] Default album based on who you are when sign-in

---

## Local Dev

```sh
poetry install --no-root
poetry run python run.py
```

> **NB:** Tailwind CSS is a post-processor - if a style is not used, you need to restart the app for it to pick it up!

Note that `./run-local.sh --docker` can also be used, which handles testing the docker container locally whilst loading the required local Google creds.
