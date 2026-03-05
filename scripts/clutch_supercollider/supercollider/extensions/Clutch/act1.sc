// Act 1
//
ClutchAct1 : ClutchBase {
    setup {
        this.start_clock(bpm: 120);
    }

    signal_enabled {
        "signal_enabled".postln;

        this.incr_power(value: 0.01);
        this.pulse_set(rate: 35, width: 0.4);
        this.mk_nodeproxies(bias: 0.40);
        this.stroke_0;
        this.stroke_signal;
    }

    go_stroke_1 {
        this.stroke_1;
        this.stroke_signal;
    }

    go_stroke_2 {
        this.stroke_2;
        this.stroke_signal;
    }

    go_stroke_3 {
        this.stroke_3;
        this.stroke_signal;
    }

    go_stroke_4 {
        this.stroke_4;
        this.stroke_signal;
    }

    // Commands
    stroke_0 {
        Pdefn(\pattern, Pseq([pX3, pY3], inf));
        Pdefn(\depth, Pwhite(0.8, 0.9, inf));
        Pdefn(\wiggle_freq, 2);
        Pdefn(\dur, Pseq([8, 8], inf));
        Pdefn(\legato, 0.5);
        Pdefn(\wiggle, 0.05);
        Pdefn(\amp, 1);
    }

    stroke_1 {
        "stroke_1".postln;

        this.pulse_set(rate: 45, width: 0.4);

        Pdefn(\pattern, Pseq([pX3, pY3, pX3, 0], inf));

        Pdefn(\depth, Pwhite(0.8, 0.9, inf));
        Pdefn(\legato, 0.85);
        Pdefn(\dur, Pseq([2, 2, 2, 2], inf));
        Pdefn(\wiggle_freq, 2);
        Pdefn(\wiggle, 0.1);
    }

    stroke_2 {
        "stroke_2".postln;

        this.pulse_set(rate: 55, width: 0.4);

        Pdefn(\pattern, Pseq([0, 0, 0, pX3, 0, 0, 0, pY3], inf));

        Pdefn(\depth, Pwhite(0.8, 0.9, inf));
        Pdefn(\legato, 0.65);
        Pdefn(\dur, Pseq([2, 2, 2, 2], inf));
        Pdefn(\wiggle_freq, 1);
        Pdefn(\wiggle, 0.1);
    }

    stroke_3 {
        "stroke_3".postln;

        this.pulse_set(rate: 60, width: 0.4);

        Pdefn(\pattern, Pseq([pX3, pX3, pY3, 0], inf));

        Pdefn(\depth, Pwhite(0.8, 0.9, inf));
        Pdefn(\legato, 0.40);
        Pdefn(\dur, Pseq([2, 2, 2, 2], inf));
        Pdefn(\wiggle_freq, 5);
        Pdefn(\wiggle, 0.05);
    }

    stroke_4 {
        "stroke_4".postln;

        Pdefn(\pattern, Pseq([pX3, pX3, pX3, pY3], inf));

        this.pulse_set(rate: 40, width: 0.45);

        Pdefn(\amp, 1);
        Pdefn(\depth, Pwhite(0.7, 0.9, inf));
        Pdefn(\wiggle_freq, 3);
        Pdefn(\dur, Pseq([2, 4], inf));
        Pdefn(\legato, 0.4);
        Pdefn(\wiggle, 0.2);
    }

    stroke_5 {
        "stroke_5".postln;

        Pdefn(\pattern, Pseq([pX3, pX3, pX3, pY3], inf));

        this.pulse_set(rate: 40, width: 0.45);

        Pdefn(\amp, 1);
        Pdefn(\depth, Pwhite(0.7, 0.9, inf));
        Pdefn(\wiggle_freq, 1);
        Pdefn(\dur, Pseq([2], inf));
        Pdefn(\legato, 0.4);
        Pdefn(\wiggle, 0.001);
    }

    change_tempo_1 {
        "tempo_change".postln;

        this.change_clock_tempo(bpm: 119);

        this.stroke_0;
        this.stroke_signal;
    }

    edge_1 { | duration |
        // Stroke

        Pdefn(\pattern, Pseq([pX3, pX3, pX3, pY3], inf));

        Pdefn(\amp, 1);
        Pdefn(\legato, 0.40);
        Pdefn(\dur, Pseq([2], inf));
        Pdefn(\wiggle_freq, 2);
        Pdefn(\wiggle, 0.2);

        // Spike
        Pdefn(\spikeAmp, this.spikeAmp);
        Pdefn(\spikeAtk, 0.25);
        Pdefn(\spikeRel, 0.005);
        Pdefn(\spikeSusLevel, 0.85);
        Pdefn(\spikePulseFreq, Pseq([60], inf)); // 120, 60 are good values
        Pdefn(\spikePulseAmp, 1.5);
        Pdefn(\spikeDur, Pseq([8], inf));
        Pdefn(\spikeLegato, 0.75);

        this.pulsar_signal;
        this.edge(duration: duration, add: edgeAdd);
    }

    edge_2 { | duration |
        // Stroke
        Pdefn(\pattern, Pseq([pX3, pY3, pX3, pY3], inf));

        Pdefn(\amp, 1);
        Pdefn(\legato, 0.40);
        Pdefn(\dur, Pseq([2], inf));
        Pdefn(\wiggle_freq, 2);
        Pdefn(\wiggle, 0.2);

        // Spike
        Pdefn(\spikeAmp, this.spikeAmp);
        Pdefn(\spikeAtk, 0.25);
        Pdefn(\spikeRel, 0.005);
        Pdefn(\spikeSusLevel, 0.85);
        Pdefn(\spikePulseFreq, Pseq([60], inf)); // 120, 60 are good values
        Pdefn(\spikePulseAmp, 1.5);
        Pdefn(\spikeDur, Pseq([4], inf));
        Pdefn(\spikeLegato, 0.65);

        this.pulsar_signal;
        this.edge(duration: duration, add: edgeAdd);
    }

    test { | duration |
        this.edge(duration: duration, add: edgeAdd);
    }
}
