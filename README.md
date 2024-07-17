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
- [ ] Handling video
- [ ] The post-processing is annoying - maybe we can get rid of the resizing completely?

## Futures

- [ ] Captions that aren't the filename
- [ ] Multiple Album Support
- [ ] Default album based on who you are when sign-in

---

## Local Dev

```sh
poetry install --no-root
# resize images and put them in TMP_DIR during startup:
poetry run python run.py --resize=true
# run with the resized images in TMP_DIR:
poetry run python run.py
```

> **NB:** Tailwind CSS is a post-processor - if a style is not used, you need to restart the app for it to pick it up!
