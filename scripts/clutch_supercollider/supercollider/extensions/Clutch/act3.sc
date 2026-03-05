ClutchAct3 : ClutchBase {
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
        Pdefn(\spikePulseFreq, Pseq([20, 60, 60, 60, 120, 120], inf));
        Pdefn(\spikePulseAmp, 1.5);
        Pdefn(\spikeDur, Pseq([2, 2, 1, 1, 1, 1], inf));
        Pdefn(\spikeLegato, 0.85);

        this.pulsar_signal;
        this.edge(duration: duration, add: edgeAdd);
    }

    // Commands
    go_edge_1 {
        this.edge_1;
        this.sweep_signal;
    }

    go_milk_1 {
        this.milk_1;
        this.sweep_signal;
    }

    go_milk_2 {
        this.milk_2;
        this.sweep_signal;
    }

    go_milk_3 {
        this.milk_3;
        this.sweep_signal;
    }

    go_milk_4 {
        this.milk_4;
        this.sweep_signal;
    }

    go_milk_edge { |duration|
        this.milk_edge(duration: duration);
        this.sweep_signal;
    }

    go_stroke_1 {
        this.stroke_1;
        this.pingpong_signal;
    }

    go_stroke_2 {
        this.stroke_2;
        this.pingpong_signal;
    }

    go_stroke_3 {
        this.stroke_3;
        this.pingpong_signal;
    }

    go_stroke_4 {
        this.stroke_4;
        this.pingpong_signal;
    }

    higher_rate { | duration |
        "higher rate".postln;
        this.pulse_change(duration, powerShift: 0.02, rate: 120, width: 0.35, desc: "higher_rate");
    }

    lower_rate {
        "lower rate".postln;
        this.pulse_set(rate: 27, width: 0.5);
    }

    milk_0 {
        "milk_0".postln;
        this.pulse_set(rate: 60, width: 0.4);

        Pdefn(\rho_atk_ratio, 0.02);
        Pdefn(\rho_rel_ratio, 0.05);
        Pdefn(\amp, 1);
        Pdefn(\wiggle_freq, this.beat_freq(count: 0.5));
        Pdefn(\wiggle, 0.05);
        Pdefn(\depth, Pwhite(0.8, 0.9, inf));
        Pdefn(\dur, Pseq([4, 4], inf));
        Pdefn(\start, Pseq([pX, pY], inf));
        Pdefn(\end, Pseq([pY, pX], inf));
        Pdefn(\legato, 0.4); // Increase this for a harder version
        Pdefn(\curve, 2);
        Pdefn(\speed_ratio, 0.28);
    }

    milk_1 {
        "milk_1".postln;

        this.pulse_set(rate: 45, width: 0.4);

        Pdefn(\rho_atk_ratio, 0.02);
        Pdefn(\rho_rel_ratio, 0.05);
        Pdefn(\amp, 1);
        Pdefn(\wiggle_freq, this.beat_freq(count: 0.5));
        Pdefn(\wiggle, 0.05);
        Pdefn(\depth, Pwhite(0.85, 0.95, inf));
        Pdefn(\dur, Pseq([4], inf));
        Pdefn(\start, Pseq([pY], inf));
        Pdefn(\end, Pseq([pX3], inf));
        Pdefn(\legato, 0.7);
        Pdefn(\curve, 2);
        Pdefn(\speed_ratio, 0.33);
    }

    milk_2 {
        "milk_2".postln;

        this.pulse_set(rate: 55, width: 0.4);

        Pdefn(\rho_atk_ratio, 0.02);
        Pdefn(\rho_rel_ratio, 0.05);
        Pdefn(\amp, 1);
        Pdefn(\wiggle_freq, this.beat_freq(count: 1));
        Pdefn(\wiggle, 0.05);
        Pdefn(\depth, Pwhite(0.85, 0.95, inf));
        Pdefn(\dur, Pseq([4, 4, 2, 2], inf));
        Pdefn(\start, Pseq([pY, pX], inf));
        Pdefn(\end, Pseq([pX3, pY], inf));
        Pdefn(\legato, 0.75);
        Pdefn(\curve, 3);
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
        Pdefn(\speed_ratio, 0.33);
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
        Pdefn(\dur, Pseq([3, 3, 3, 3, 4], inf));
        Pdefn(\start, Pseq([pY], inf));
        Pdefn(\end, Pseq([pX3], inf));
        Pdefn(\legato, 0.8);
        Pdefn(\curve, 2);
        Pdefn(\speed_ratio, 0.33);
    }

    milk_5 {
        this.milk_4;
    }

    milk_edge { |duration|
        Pdefn(\spikeAmp, this.spikeAmp);
        Pdefn(\spikeAtk, 0.15);
        Pdefn(\spikeRel, 0.005);
        Pdefn(\spikeSusLevel, 0.85);
        Pdefn(\spikePulseFreq, Pseq([20, 60], inf)); // 120, 60 are good values
        Pdefn(\spikePulseAmp, 1.5);
        Pdefn(\spikeDur, Pseq([2, 2, 1, 1, 1, 1], inf));
        Pdefn(\spikeLegato, 0.80);

       this.pulsar_signal;
       this.edge(duration: duration, add: edgeAdd);
     }

    slow {
        Pdefn(\atk, 0.3);
        Pdefn(\rel, 0.3);
        Pdefn(\amp, 1);
        Pdefn(\legato, 0.7);
        Pdefn(\dur, Pseq([8], inf));
        Pdefn(\depth, Pwhite(0.85, 0.95, inf));
        Pdefn(\p1, pB);
        Pdefn(\p2, pA);
        Pdefn(\p3, pX3);
        Pdefn(\p4, pA);
        Pdefn(\curve, 2);
        Pdefn(\speed_in, 2);
        Pdefn(\speed_out, 0.5);
        Pdefn(\curve_in, 2);
        Pdefn(\curve_out, -1);
    }

    slow_1 {
        "slow_1".postln;

        this.pulse_set(rate: 60, width: 0.4);
        this.slow;
    }

    slow_2 {
        "slow_2".postln;

        this.pulse_set(rate: 35, width: 0.4);
        this.slow;
    }

    spike { |duration, rate=30|
        "spike".postln;

        // Spike
        Pdefn(\spikeAmp, this.spikeAmp);
        Pdefn(\spikeAtk, 0.25);
        Pdefn(\spikeRel, 0.005);
        Pdefn(\spikeSusLevel, 0.66);
        Pdefn(\spikePulseFreq, Pseq([rate], inf)); // 120, 60 are good values
        Pdefn(\spikePulseAmp, 1.5);
        Pdefn(\spikeDur, Pseq([16], inf));
        Pdefn(\spikeLegato, 0.5);

        this.pulsar_signal;

        r{
            duration.sleep;

            "spike:end".postln;
            ~spike = nil;
        }.play;
    }

    spike_1 { |duration|
        this.spike(duration: duration, rate: 40);
    }

    spike_2 { |duration|
        this.spike(duration: duration, rate: 24);
    }

    spike_3 { |duration|
        this.spike(duration: duration, rate: 16);
    }

    stroke_0 {
        "stroke_0".postln;

        this.pulse_set(rate: 60, width: 0.4);

        Pdefn(\atk, 0.3);
        Pdefn(\rel, 0.5);
        Pdefn(\amp, 1);
        Pdefn(\legato, 0.8);
        Pdefn(\dur, Pseq([4], inf));
        Pdefn(\depth, Pwhite(0.85, 0.95, inf));
        Pdefn(\p1, pA);
        Pdefn(\p2, pB);
        Pdefn(\p3, 0);
        Pdefn(\p4, pA);
        Pdefn(\curve, 2);
        Pdefn(\speed_in, 1);
        Pdefn(\speed_out, 1);
        Pdefn(\curve_in, 2);
        Pdefn(\curve_out, -2);
    }

    stroke_1 {
        "stroke_1".postln;

        this.pulse_set(rate: 60, width: 0.4);

        Pdefn(\atk, 0.3);
        Pdefn(\rel, 0.3);
        Pdefn(\amp, 1);
        Pdefn(\legato, 0.7);
        Pdefn(\dur, Pseq([4], inf));
        Pdefn(\depth, Pwhite(0.85, 0.95, inf));
        Pdefn(\p1, pA);
        Pdefn(\p2, pB);
        Pdefn(\p3, pX3);
        Pdefn(\p4, pB);
        Pdefn(\curve, 2);
        Pdefn(\speed_in, 1.5);
        Pdefn(\speed_out, 1);
        Pdefn(\curve_in, 2);
        Pdefn(\curve_out, -1);
    }

    stroke_2 {
        "stroke_2".postln;

        this.pulse_set(rate: 60, width: 0.4);

        Pdefn(\atk, 0.3);
        Pdefn(\rel, 0.3);
        Pdefn(\amp, 1);
        Pdefn(\legato, 0.7);
        Pdefn(\dur, Pseq([4], inf));
        Pdefn(\depth, Pwhite(0.85, 0.95, inf));
        Pdefn(\p1, pA);
        Pdefn(\p2, pB);
        Pdefn(\p3, pX3);
        Pdefn(\p4, 0);
        Pdefn(\curve, 2);
        Pdefn(\speed_in, 1);
        Pdefn(\speed_out, 0.5);
        Pdefn(\curve_in, 2);
        Pdefn(\curve_out, -1);
    }

    stroke_3 {
        "stroke_3".postln;

        this.pulse_set(rate: 60, width: 0.4);
        this.stroke_fast;
    }

    stroke_4 {
        "stroke_4".postln;
        this.pulse_set(rate: 40, width: 0.4);
        this.stroke_fast;
    }

    stroke_5 {
        "stroke_5".postln;
        this.pulse_set(rate: 75, width: 0.4);
        this.stroke_fast;
    }

    stroke_fast {
        "stroke_fast".postln;

        this.pulse_set(rate: 60, width: 0.4);

        Pdefn(\atk, 0.3);
        Pdefn(\rel, 0.2);
        Pdefn(\amp, 1);
        Pdefn(\legato, 0.8);
        Pdefn(\dur, Pseq([4, 4, 4, 4, 2, 2], inf));
        Pdefn(\depth, Pwhite(0.85, 0.95, inf));
        Pdefn(\p1, pB);
        Pdefn(\p2, pX);
        Pdefn(\p3, pY3);
        Pdefn(\p4, 0);
        Pdefn(\curve, 2);
        Pdefn(\speed_in, Pseq([1, 1, 1, 1, 0.5, 0.5], inf));
        Pdefn(\speed_out, Pseq([0.5, 0.5, 0.5, 0.5, 0.25, 0.25], inf));
        Pdefn(\curve_in, 4);
        Pdefn(\curve_out, 1);
    }

    tranquil { |duration=8,rate=15|
        "tranquil".postln;

        ~signal = nil; // For now, we'll figure out something better

        Pdefn(\spikeAmp, carrierAmp);
        Pdefn(\spikeAtk, 0.25);
        Pdefn(\spikeRel, 0.005);
        Pdefn(\spikeSusLevel, 0.66);
        Pdefn(\spikePulseFreq, Pseq([rate], inf)); // 120, 60 are good values
        Pdefn(\spikePulseAmp, 1.5);
        Pdefn(\spikeDur, Pseq([16], inf));
        Pdefn(\spikeLegato, 0.5);

        this.pulsar_signal;
        r{
            "spike:end".postln;

            duration.sleep;
            ~spike = nil;
        }.play;
    }
}

ClutchAct31 : ClutchAct3 {
    setup {
        this.start_clock(bpm: 123);
    }

    change_tempo_1 { |duration|
        this.change_clock_tempo(bpm: 100);
        this.milk_0;
        this.sweep_signal;
        this.milk_edge(duration: duration);
    }

    // Funcs
    signal_enabled {
        "signal_enabled".postln;

        this.incr_power(value: 0.02);
        this.pulse_set(rate: 50, width: 0.4);
        this.mk_nodeproxies(bias: 0.325);
        this.stroke_0;
        this.pingpong_signal;
    }

    tantalize_1 { |duration|
        "tantalize_1".postln;
        // Idea: these are like an edge, but with a lower push and a slow stroke.
        // Alter the rate at which the attack happens. Don't go as far up. Add some buzz
        // through frequency modulation.

        // Spike
        Pdefn(\spikeAmp, this.spikeAmp);
        Pdefn(\spikeAtk, 0.25);
        Pdefn(\spikeRel, 0.005);
        Pdefn(\spikeSusLevel, 0.40);
        Pdefn(\spikePulseFreq, Pseq([20], inf)); // 120, 60 are good values
        Pdefn(\spikePulseAmp, 1.5);
        Pdefn(\spikeDur, Pseq([16], inf));
        Pdefn(\spikeLegato, 0.8);

        this.pulsar_signal;
        this.edge(duration: duration, add: edgeAdd);
    }

    tantalize_2 { |duration|
        "tantalize_2".postln;
        // See tantalize 1 for ideas. It needs to be a bit different.

        Pdefn(\spikeAmp, this.spikeAmp);
        Pdefn(\spikeAtk, 0.15);
        Pdefn(\spikeRel, 0.005);
        Pdefn(\spikeSusLevel, 0.40);
        Pdefn(\spikePulseFreq, Pseq([120], inf)); // 120, 60 are good values
        Pdefn(\spikePulseAmp, 1.5);
        Pdefn(\spikeDur, Pseq([16], inf));
        Pdefn(\spikeLegato, 0.8);

        this.pulsar_signal;
        this.edge(duration: duration, add: edgeAdd);
    }
}

ClutchAct32 : ClutchAct3 {
    setup {
        "setup".postln;

        this.start_clock(bpm: 133);
    }

    signal_enabled {
        "signal_enabled".postln;

        this.incr_power(value: 0.025);
        this.pulse_set(rate: 50, width: 0.4);
        this.mk_nodeproxies(bias: 0.325);
        this.milk_0;
        this.sweep_signal;
    }

    change_tempo_1 {
        "change_tempo_1".postln;

        this.change_clock_tempo(bpm: 133);
    }

    // change tempo 2 was removed from the project.

    change_tempo_3 {
        "change_tempo_3".postln;

        this.change_clock_tempo(bpm: 128);
        this.stroke_1;
        this.pingpong_signal;
    }

    change_tempo_4 {
        "change_tempo_4".postln;

        this.change_clock_tempo(bpm: 105);
        this.go_milk_1;
    }

    change_tempo_5 {
        "change_tempo_5".postln;
        this.change_clock_tempo(bpm: 100);
        this.stroke_3;
        this.pingpong_signal;
    }

    load_ruin { |duration|
        "Load RUIN".postln;

        this.pulse_set(rate: 90, width: 0.4);

         // Spike
        Pdefn(\spikeAmp, this.spikeAmp);
        Pdefn(\spikeAtk, 0.25);
        Pdefn(\spikeRel, 0.005);
        Pdefn(\spikeSusLevel, 0.75);
        Pdefn(\spikePulseFreq, Pseq([10], inf)); // 120, 60 are good values
        Pdefn(\spikePulseAmp, 1.5);
        Pdefn(\spikeDur, Pseq([2], inf));
        Pdefn(\spikeLegato, 0.9);

        this.pulsar_signal;
        this.stroke_4;
        this.pingpong_signal;
        r{
            duration.sleep;

            "load_ruin:end".postln;
            this.reset;
        }.play;
    }

    ruin {
        "Ruin".postln;

        this.pulse_set(rate: 10, width: 0.4);

         // Spike
        Pdefn(\spikeAmp, this.spikeAmp);
        Pdefn(\spikeAtk, 0.25);
        Pdefn(\spikeRel, 0.005);
        Pdefn(\spikeSusLevel, 0.75);
        Pdefn(\spikePulseFreq, Pseq([20], inf)); // 120, 60 are good values
        Pdefn(\spikePulseAmp, 1.5);
        Pdefn(\spikeDur, Pseq([2], inf));
        Pdefn(\spikeLegato, 0.9);

        this.pulsar_signal;
        this.milk_1;
        this.sweep_signal;
    }

    cum { |duration|
        "CUM".postln;
        this.pulse_set(rate: 120, width: 0.4); // Don't lower to 30... lower to something like 60.

        Pdefn(\pattern, Pseq([pX3], inf));

        Pdefn(\depth, Pwhite(0.9, 1.0, inf));
        Pdefn(\legato, 0.80);
        Pdefn(\dur, Pseq([8, 4, 2, 4, 4], inf));
        Pdefn(\wiggle_freq, this.beat_freq(2)); // 3
        Pdefn(\wiggle, 0.7); // 0.4

        // Spike
        Pdefn(\spikeFreq, 331); // Mild should keep this mellow
        Pdefn(\spikeAmp, this.spikeAmp);
        Pdefn(\spikeAtk, 0.20);
        Pdefn(\spikeRel, 0.1);
        Pdefn(\spikeSusLevel, 0.90);
        Pdefn(\spikePulseFreq,
          Pseq([
            this.beat_freq(8),
            this.beat_freq(1),
            this.beat_freq(2),
            this.beat_freq(2)], inf));
        Pdefn(\spikePulseAmp, 1.2);
        Pdefn(\spikeDur, Pseq([2, 4, 8, 8], inf));

        this.pulsar_signal;
        this.stroke_signal;
        this.edge(duration: duration, add: edgeAdd);
    }
}