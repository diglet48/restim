// Intro
ClutchIntro : ClutchBase {
    setup {
        this.start_clock(bpm: 59.5);
    }

    signal_enabled {
        "signal_enabled".postln;

        this.pulse_set(rate: 40, width: 0.45);
        this.mk_nodeproxies(bias: 0.4);

        Pdefn(\amp, 1);
        Pdefn(\depth, Pwhite(0.7, 0.9, inf));
        Pdefn(\wiggle_freq, 3);
        Pdefn(\dur, Pseq([4, Rest(4)], inf));
        Pdefn(\legato, 0.9);
        Pdefn(\wiggle, 0.1);

        Pdefn(\pattern, Pseq([pX3, pY3], inf));

        this.stroke_signal;
    }

    // Commands
    calibrate_a {
        "calibrate a".postln;

        Pdefn(\pattern, Pseq([pX3, pY3], inf));

        Pdefn(\amp, 1);
        Pdefn(\depth, Pwhite(0.8, 0.9, inf));
        Pdefn(\wiggle_freq, 5);
        Pdefn(\dur, Pseq([2, Rest(2)], inf));
        Pdefn(\legato, 1.0);
        Pdefn(\wiggle, 0.1);
    }

    calibrate_b {
        "calibrate b".postln;

        Pdefn(\pattern, Pseq([pY3, pX3], inf));

        Pdefn(\amp, 1);
        Pdefn(\depth, Pwhite(0.8, 0.9, inf));
        Pdefn(\wiggle_freq, 5);
        Pdefn(\dur, Pseq([2, Rest(2)], inf));
        Pdefn(\legato, 1.0);
        Pdefn(\wiggle, 0.1);
    }

    warmup_0 {
        "warmup_0".postln;

        Pdefn(\pattern, Pseq([pX3, pY3], inf));

        Pdefn(\amp, 1);
        Pdefn(\depth, Pwhite(0.7, 0.9, inf));
        Pdefn(\wiggle_freq, 2);
        Pdefn(\dur, Pseq([4, 4, 2, 2], inf));
        Pdefn(\legato, 0.8);
        Pdefn(\wiggle, 0.15);
    }

    warmup_1 {
        "warmup_1".postln;

        this.pulse_set(rate: 45, width: 0.4);

        Pdefn(\legato, 0.80);
        Pdefn(\dur, Pseq([4, 4], inf));
        Pdefn(\wiggle_freq, 3);
    }

    warmup_2 {
        "warmup_2".postln;

        this.pulse_set(rate: 60, width: 0.4);

        Pdefn(\legato, 0.80);
        Pdefn(\dur, Pseq([4, 2, 2], inf));
        Pdefn(\wiggle_freq, 1);
    }

    warmup_3 {
        "warmup_3".postln;

        this.pulse_set(rate: 60, width: 0.4);

        Pdefn(\legato, 0.75);
        Pdefn(\dur, Pseq([2, 2], inf));
        Pdefn(\wiggle_freq, 3);
    }

    warmup_4 {
        "warmup_4".postln;

        this.pulse_set(rate: 45, width: 0.4);

        Pdefn(\legato, 0.65);
        Pdefn(\dur, Pseq([4, 4, 2], inf));
        Pdefn(\wiggle_freq, 2);
        Pdefn(\wiggle, 0.2);
    }

    warmup_5 {
        "warmup_5".postln;

        this.pulse_set(rate: 50, width: 0.4);
        Pdefn(\pattern, Pseq([pX3, pX3, pX3, pY3], inf));

        Pdefn(\amp, 1);
        Pdefn(\legato, 0.40);
        Pdefn(\dur, Pseq([2], inf));
        Pdefn(\wiggle_freq, 2);
        Pdefn(\wiggle, 0.2);
    }
}
