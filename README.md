# Something Big Is Coming — Technical Council, IIIT Delhi

Mobile teaser page opened from a QR code: system boot → user detected → access granted → reveal, ending with a **CAN U GUESS?** form.

## Run

```bash
python3 server.py        # http://localhost:8000
```

`server.py` serves the site and saves guesses to `data/guesses.csv` (server timestamp, name, guess). `data/` is never served and is git-ignored.

Tempo: change `PACE` near the top of the script in `index.html`.
