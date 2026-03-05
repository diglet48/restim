# Tools

Clutch is made using two tools:

## OTIOSC

The Go program `otiosc` reads a timeline in OpenTimelineIO format and extracts markers of a given marker color. It then writes those markers into a format recognizable by SuperCollider.

Suppose we have a marker at timecode `01:02:03:14` saying `hello world`. Then running the command

```
$ ./otiosc convert --name='foo' --color=RED timeline.otio timeline.scd
```

Reads every marker in red, and converts that into a file `timeline.scd` with contents:

```
q[\foo] = [
    [02, 03 + (14/30), {
        e.hello_world;
    }]
]
```

A range-marker is translated into `e.hello_world(15.5)` for a marker with a duration of `15.5` seconds.

This sets up a script at the SuperCollider side, stores that in the dictionary `q` at key `\foo`, translating each event into an offset. The events are invoked on the object `e`.

## SuperCollider

This is the main script I used for Clutch.

There's an extension to SuperCollider (called Clutch) which has to be installed, because in SuperCollider you can only get access to the OO features of the language in extensions. The top of the class hierarchy is in `core` and then extended by each act.

The main file `clutch.scd` contains the SynthDefs as well as some of the base setup.

Typical run is:

```
(
	q = ();
	"./00_intro_script.scd".loadRelative;

	e = ClutchIntro.new(s);
	t = TempoClock.new;
	e.run(t, q[\intro],
		record: true,
		description: "00_intro");
)
```

1. A new dictionary `q` is created.
2. We load events into this dictionary.
3. An appropriate clutch-object is initialized in `e`.
4. A tempoclock is generated.
5. We run `e` on the tempoclock with the script `q[\intro]`. This loads all the events of the script in as future events in the tempoclock.

The first command usually calls `e.start_clock(bmp: x)` which sets up a tempoclock at BPM x. Then a `ProxySpace` is generated and the tempoclock is set up to control this proxyspace. Synths then play on this proxy space, usually through the variable `~signal`.

The advantage of having to tempoclocks is that we can follow a beat of a song, but still inject new events in SMPTE Timecode.

Most of the core signal generation is using polar coordinates rather than an XY cartesian plane.

### Development

During development, it is easier to set up a small test file in which you can manually inject event changes and alter their feel dynamically. This lets you audition many different setups quickly.

For some cases, I would generate 2-3 variants of a signal, then test them out and pick the one I thought felt the best or captured what I wanted to most. Doing multiple of those lets you batch multiple tests into a single ESTIM-session which makes it far more effective. Then I would take notes and adapt accordingly.

### Delivery

Each act was generated on its own, then assembled in the NLE. Normalization happened in the NLE as well.

Generally, the rule is that you want your chain to be reproducible, so you can add changes easily.