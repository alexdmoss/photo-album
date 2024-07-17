# photo-album

Photo Slideshow application using FastAPI + TailwindCSS + HTMX. Initial implementation learnt from [this tutorial](https://github.com/tataraba/simplesite/tree/main) - _thank you!_ - but then heavily customised to my needs.

---

## To Do

- [ ] Resize images to fit browser window
- [ ] Clean up look and feel
- [ ] Load images from Google Storage
- [ ] OAuth sign-in
- [ ] Make Captions optional
- [ ] Download all photos option
- [ ] Snazzy transitions
- [ ] Option to configure speed of carousel
- [ ] Option to stop/start carousel

## Futures

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
