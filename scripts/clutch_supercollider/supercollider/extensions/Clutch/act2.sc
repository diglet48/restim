// Act 2
ClutchAct2 : ClutchBase {
    setup {
        this.start_clock(bpm: 75/2);
    }

    signal_enabled {
        "signal enabled".postln;

        Pdefn(\amp, 1);
        this.incr_power(value: 0.015);

        this.pulse_set(rate: 30, width: 0.325);
        this.mk_nodeproxies(bias: 0.4);
        this.stroke_0;
    }

    change_tempo_1 {
        this.change_clock_tempo(bpm: 75);
        this.stroke_1;
        this.sweep_signal;
    }

    change_tempo_2 {
        this.change_clock_tempo(bpm: 70);
        this.milk_1;
        this.sweep_signal;
    }

    stroke_0 {
        Pdefn(\depth, Pwhite(0.8, 0.9, inf));
        Pdefn(\wiggle_freq, 1);
        Pdefn(\dur, Pseq([4, Rest(4)], inf));
        Pdefn(\pattern, Pseq([pX3, 0, pY3, 0], inf));
        Pdefn(\legato, 0.85);
        Pdefn(\wiggle, 0.05);
        Pdefn(\amp, 1);

        this.stroke_signal;
    }

    // Commands
    higher_rate { | duration |
        this.pulse_change(duration, powerShift: 0.02, rate: 120, width: 0.35, desc: "Higher Rate");
    }

    intro_1 {
        "intro_1".postln;

        this.pulse_set(rate: 45, width: 0.4);

        Pdefn(\depth, Pwhite(0.6, 0.9, inf));
        Pdefn(\wiggle_freq, 2);
        Pdefn(\wiggle, 0.1);
        Pdefn(\dur, Pseq([8], inf));
        Pdefn(\legato, 0.75);
        Pdefn(\pattern, Pseq([0], inf));
    }

    intro_2 {
        "intro_2".postln;

        this.pulse_set(rate: 40, width: 0.4);

        Pdefn(\depth, Pwhite(0.7, 0.85, inf));
        Pdefn(\wiggle_freq, this.beat_freq(count: 1));
        Pdefn(\atk_ratio, Pseq([0.5, 0.3], inf));
        Pdefn(\wiggle, 0.1);
        Pdefn(\dur, Pseq([4, 4], inf));
        Pdefn(\legato, 0.75);
        Pdefn(\pattern, Pseq([pX3, pY3], inf));
    }

    intro_3 {
        "intro_3".postln;

        this.pulse_set(rate: 45, width: 0.4);

        Pdefn(\depth, Pwhite(0.8, 0.95, inf));
        Pdefn(\wiggle_freq, this.beat_freq(count: 1));
        Pdefn(\atk_ratio, Pseq([0.5, 0.3], inf));
        Pdefn(\wiggle, 0.15);
        Pdefn(\dur, Pseq([2, 2, 2, 2], inf));
        Pdefn(\legato, 0.75);
        Pdefn(\pattern, Pseq([0, 0, pX3, pY3], inf));
    }

    intro_4 {
        "intro_4".postln;

        this.pulse_set(rate: 45, width: 0.4);

        Pdefn(\depth, Pwhite(0.8, 0.95, inf));
        Pdefn(\wiggle_freq, this.beat_freq(count: 0.5));
        Pdefn(\atk_ratio, 0.5);
        Pdefn(\wiggle, 0.05);
        Pdefn(\dur, Pseq([4, 4, 4, 4], inf));
        Pdefn(\legato, 0.6);
        Pdefn(\pattern, Pseq([pX3, pY3, pX3, 0], inf));
    }

    stroke_1 {
        "stroke_1".postln;

        this.pulse_set(rate: 60, width: 0.4);

		Pdefn(\rho_atk_ratio, 0.02);
		Pdefn(\rho_rel_ratio, 0.05);
		Pdefn(\amp, 1);
		Pdefn(\wiggle_freq, this.beat_freq(count: 1));
		Pdefn(\wiggle, 0.01);
		Pdefn(\depth, Pwhite(0.75, 0.95, inf));
		Pdefn(\dur, Pseq([4, 4], inf));
		Pdefn(\start, Pseq([pX3, pY3], inf));
		Pdefn(\end, Pseq([pY3, pX3], inf));
		Pdefn(\legato, 0.6);
		Pdefn(\curve, 3);
        Pdefn(\speed_ratio, 0.375);
    }

    stroke_2 {
        "stroke_2".postln;

        this.pulse_set(rate: 60, width: 0.4);

        Pdefn(\rho_atk_ratio, 0.075);
        Pdefn(\rho_rel_ratio, 0.05);
        Pdefn(\amp, 1);
        Pdefn(\wiggle_freq, this.beat_freq(count: 1));
        Pdefn(\wiggle, 0.1);
        Pdefn(\depth, Pwhite(0.75, 0.95, inf));
        Pdefn(\dur, Pseq([2, 2, 4], inf));
        Pdefn(\start, Pseq([pX3, pX3, pY3], inf));
        Pdefn(\end, Pseq([pY3, pY3, pX3], inf));
        Pdefn(\legato, 0.85);
        Pdefn(\curve, 2);
        Pdefn(\speed_ratio, 0.35);
    }

    stroke_3 {
        "stroke_3".postln;

        this.pulse_set(rate: 60, width: 0.4);

        Pdefn(\rho_atk_ratio, 0.02);
        Pdefn(\rho_rel_ratio, 0.05);
        Pdefn(\amp, 1);
        Pdefn(\wiggle_freq, this.beat_freq(count: 1));
        Pdefn(\wiggle, 0.01);
        Pdefn(\depth, Pwhite(0.75, 0.95, inf));
        Pdefn(\dur, Pseq([2, 2], inf));
        Pdefn(\start, Pseq([pX3, pY3, pY3, pX3], inf));
        Pdefn(\end, Pseq([pY3, pX3, pX3, pY3], inf));
        Pdefn(\legato, 0.9);
        Pdefn(\curve, 3);
        Pdefn(\speed_ratio, 0.3);
    }

    stroke_4 {
        "stroke_4".postln;

        this.pulse_set(rate: 60, width: 0.4);

        Pdefn(\rho_atk_ratio, 0.02);
        Pdefn(\rho_rel_ratio, 0.05);
        Pdefn(\amp, 1);
        Pdefn(\wiggle_freq, this.beat_freq(count: 1));
        Pdefn(\wiggle, 0.05);
        Pdefn(\depth, Pwhite(0.75, 0.95, inf));
        Pdefn(\legato, 0.9);
        Pdefn(\curve, 1);
        Pdefn(\speed_ratio, 0.33);
        Pdefn(\dur, Pseq([
            Pseq([1], 4),
            Pseq([2, 1, Rest(1)], 1)
        ], inf));
        Pdefn(\start, Pseq([pX3, pY3], inf));
        Pdefn(\end, Pseq([pY3, pX3], inf));
    }

    stroke_5 {
        "stroke_5".postln;

        this.pulse_set(rate: 60, width: 0.4);

        Pdefn(\rho_atk_ratio, 0.02);
        Pdefn(\rho_rel_ratio, 0.05);
        Pdefn(\amp, 1);
        Pdefn(\curve, 2);
        Pdefn(\speed_ratio, 0.33);
        Pdefn(\dur, Pseq([2, 2, 1, 1], inf));
        Pdefn(\start, Pseq([pX3, pY3], inf));
        Pdefn(\end, Pseq([pY3, pX3], inf));
        Pdefn(\legato, 0.85);
    }

    go_slow_1 {
        this.slow_1;
        this.sweep_signal;
    }

    go_stroke_2 {
        this.stroke_2;
        this.sweep_signal;
    }

    go_stroke_3 {
        this.stroke_3;
        this.sweep_signal;
    }

    slow_1 {
        "slow_1".postln;

        this.pulse_set(rate: 60, width: 0.4);
        Pdefn(\rho_atk_ratio, 0.02);
        Pdefn(\rho_rel_ratio, 0.05);
        Pdefn(\amp, 1);
        Pdefn(\wiggle_freq, this.beat_freq(count: 0.5));
        Pdefn(\wiggle, 0.2);
        Pdefn(\depth, Pwhite(0.55, 0.75, inf));
        Pdefn(\dur, Pseq([6, 6], inf));
        Pdefn(\start, Pseq([pX, pY], inf));
        Pdefn(\end, Pseq([pY, pX], inf));
        Pdefn(\legato, 0.4); // Increase this for a harder version
        Pdefn(\curve, 2);
        Pdefn(\speed_ratio, 0.5);
    }

    go_milk_1 {
        this.milk_1;
        this.sweep_signal;
    }

    go_milk_3 {
        this.milk_3;
        this.sweep_signal;
    }

    milk_1 {
        "milk_1".postln;

        this.pulse_set(rate: 45, width: 0.4);

        Pdefn(\rho_atk_ratio, 0.02);
        Pdefn(\rho_rel_ratio, 0.05);
        Pdefn(\amp, 1);
        Pdefn(\wiggle_freq, this.beat_freq(count: 0.5));
        Pdefn(\wiggle, 0.25);
        Pdefn(\depth, Pwhite(0.70, 0.75, inf));
        Pdefn(\dur, Pseq([6], inf));
        Pdefn(\start, Pseq([pY], inf));
        Pdefn(\end, Pseq([pX], inf));
        Pdefn(\legato, 0.90);
        Pdefn(\curve, 4);
        Pdefn(\speed_ratio, 0.66);
    }

    milk_2 {
        "milk_2".postln;

        this.pulse_set(rate: 55, width: 0.4);

        Pdefn(\rho_atk_ratio, 0.02);
        Pdefn(\rho_rel_ratio, 0.05);
        Pdefn(\amp, 1);
        Pdefn(\wiggle_freq, this.beat_freq(count: 1));
        Pdefn(\wiggle, 0.1);
        Pdefn(\depth, Pwhite(0.85, 0.9, inf));
        Pdefn(\dur, Pseq([4, 4, 2, 2], inf));
        Pdefn(\start, Pseq([pY], inf));
        Pdefn(\end, Pseq([pX], inf));
        Pdefn(\legato, 0.9);
        Pdefn(\curve, 4);
        Pdefn(\speed_ratio, 0.35);
    }

    milk_3 {
        "milk_3".postln;

        this.pulse_set(rate: 60, width: 0.4);

        Pdefn(\rho_atk_ratio, 0.02);
        Pdefn(\rho_rel_ratio, 0.05);
        Pdefn(\amp, 1);
        Pdefn(\wiggle_freq, this.beat_freq(count: 1));
        Pdefn(\wiggle, 0.1);
        Pdefn(\depth, Pwhite(0.75, 0.9, inf));
        Pdefn(\dur, Pseq([4, 4, 4], inf));
        Pdefn(\start, Pseq([pB, pB, pA], inf));
        Pdefn(\end, Pseq([pA, pA, pB], inf));
        Pdefn(\legato, 0.8);
        Pdefn(\curve, 4);
        Pdefn(\speed_ratio, 0.25);
    }

    milk_4 {
        "milk_4".postln;

        this.pulse_set(rate: 40, width: 0.4);

        Pdefn(\rho_atk_ratio, 0.02);
        Pdefn(\rho_rel_ratio, 0.05);
        Pdefn(\amp, 1);
        Pdefn(\wiggle_freq, this.beat_freq(count: 1));
        Pdefn(\wiggle, 0.1);
        Pdefn(\depth, Pwhite(0.75, 0.90, inf));
        Pdefn(\dur, Pseq([Pseq([2], 8), 8], inf));
        Pdefn(\start, Pseq([pB], inf));
        Pdefn(\end, Pseq([pA], inf));
        Pdefn(\legato, 0.8);
        Pdefn(\curve, 4);
        Pdefn(\speed_ratio, 0.25);
    }

    edge_1 { |duration|
        // Spike
        Pdefn(\spikeAmp, this.spikeAmp);
        Pdefn(\spikeAtk, 0.25);
        Pdefn(\spikeRel, 0.005);
        Pdefn(\spikeSusLevel, 0.75);
        Pdefn(\spikePulseFreq, Pseq([20, 60, 60], inf)); // 120, 60 are good values
        Pdefn(\spikePulseAmp, 1.5);
        Pdefn(\spikeDur, Pseq([4, 2, 2], inf));
        Pdefn(\spikeLegato, 0.85);

        this.pulsar_signal;
        this.edge(duration: duration, add: edgeAdd);
    }

    edge_2 { |duration|
        // Spike
        Pdefn(\spikeAmp, this.spikeAmp);
        Pdefn(\spikeAtk, 0.25);
        Pdefn(\spikeRel, 0.005);
        Pdefn(\spikeSusLevel, 0.80);
        Pdefn(\spikePulseFreq, Pseq([20, 60, 60, 120], inf)); // 120, 60 are good values
        Pdefn(\spikePulseAmp, 1.5);
        Pdefn(\spikeDur, Pseq([8, 2, 2, 4], inf));
        Pdefn(\spikeLegato, 0.85);

        this.pulsar_signal;
        this.edge(duration: duration, add: edgeAdd);
    }
}

