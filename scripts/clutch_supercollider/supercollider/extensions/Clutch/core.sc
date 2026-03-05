/*
 * Clutch is the main object containing shared code between acts
 */
ClutchCore {
    var proxySpace, tempoClock;
    var srv;
    var bus, grp;
    var carrierFreq, carrierAmp, spikeAmp;
    var pA, pB, pC, pX, pY, pX3, pY3;
    var pulseRate, pulseWidth;
    var edgeAdd, spikeMul;

    *new { |server|
        ^super.new.init(server)
    }

    spikeAmp {
        ^carrierAmp * spikeMul;
    }

    init { |server|
        "init Core".postln;
        // Configuration
        srv = server;
        carrierFreq = 907; // 797
        carrierAmp = -8.dbamp;

        edgeAdd = 0.03; // Alternative: 0.025
        spikeMul = 1.6; // Alternative: 1.25. If too evil at the end, we should turn it down

        pX = (pi/2).neg;
        pY = pX.neg;
        pX3 = (pi/3).neg;
        pY3 = pX3.neg;

        pA = (2pi / 3).neg;
        pB = pA.neg;
        pC = 3pi / 2;

        this.pulse_set(rate: 60, width: 0.45);

        // Buses
        bus = Dictionary.new;
        bus.add(\xy -> Bus.audio(srv, 2));
        bus.add(\alpha -> Bus.newFrom(bus[\xy], 0, numChannels: 1));
        bus.add(\beta  -> Bus.newFrom(bus[\xy], 1, numChannels: 1));

        bus.add(\polar -> Bus.audio(srv, 2));
        bus.add(\rho   -> Bus.newFrom(bus[\polar], 0, numChannels: 1));
        bus.add(\theta -> Bus.newFrom(bus[\polar], 1, numChannels: 1));

        bus.add(\pulse -> Bus.audio(srv, 2));
        bus.add(\gamma -> Bus.newFrom(bus[\pulse], 0, numChannels: 1));
        bus.add(\delta -> Bus.newFrom(bus[\pulse], 1, numChannels: 1));

        bus.add(\translate -> Bus.audio(srv, 2));

        // Groups
        grp = Dictionary.new;
        grp.add(\signal -> Group.new);
        grp.add(\translation -> Group.after(grp[\signal]));
        grp.add(\carrier -> Group.after(grp[\translation]));

        // Pdefns
        Pdefn(\carrierAmp, carrierAmp);
        Pdefn(\carrierFreq, carrierFreq);

        Pdefn(\strokeAmp, Pwhite(0.75, 90));
        Pdefn(\strokeLegato, 0.75);

        Pdefn(\sweepAtk, 0.05);
        Pdefn(\sweepRel, 0.05);

        Pdefn(\spikeFreq, 599);
        this.phrase_lib;
    }

    // Override this
    phrase_lib {
        "Core Phraselib is empty".postln;
    }

    doesNotUnderstand { arg selector ... args;
        ("WARNING: doesNotUnderstand: " ++ selector).postln;
    }

    // Run a script
    run { | tClock, script, record=false, description="clutch" |
	    var timeCode, skippedEvents, tCode;

        if(record, {
            srv.record("./results" ++ "/SC_" ++ description ++ "_" ++ Date.getDate.stamp ++ ".wav");
        });

	    skippedEvents = 0;

        tCode = { | m=0, s=0 |
            m * 60 + s
        };

	    script.do{ |a|
		    timeCode = tCode.(a[0], a[1]);

		    if (timeCode >= 0, {
			    tClock.schedAbs(timeCode, {
				    ("@" ++ a[0].asString ++ "m" ++ a[1].asFloat.asStringPrec(5) ++ "s ---:").postln;
				    a[2].value;
			    });
		    },{
			    skippedEvents = skippedEvents + 1;
		    });
	    };

	    ("Skipped " ++ skippedEvents.asString ++ " events in the past due to offset").postln;
	    ("Added " ++ (script.size.asString) ++ " events to the timeClock").postln;
    }

    fadeout { |fadeTime=8|
        "fadeout".postln;
        ~carrier.stop(fadeTime: fadeTime);
    }

    done {
        "done.".postln;

        if (srv.isRecording, {
            srv.stopRecording;
        });
    }

    start_clock { |bpm=120|
        ("setup, clock at " ++ bpm.asString ++ " bpm").postln;

        tempoClock = TempoClock(123/60);
        proxySpace = ProxySpace(clock: tempoClock).fadeTime_(0.5).quant_(2);
        proxySpace.push;
    }

    change_clock_tempo { |bpm=60|
        ("tempo_change: " ++ bpm.asString ++ " bpm").postln;

        tempoClock.tempo = bpm/60;
    }

    pulse_reset {
        Pdefn(\pulseRate, pulseRate);
        Pdefn(\pulseWidth, pulseWidth);
    }

    pulse_set { |rate=60, width=0.45 |
        pulseRate = rate;
        pulseWidth = width;

        this.pulse_reset;
    }

    reduce_rate { |rate_ratio=0.85, width_ratio=1.0|
        var rate, width;
        "reduce rate".postln;

        rate = pulseRate;
        width = pulseWidth;

        this.pulse_set(rate: rate * rate_ratio, width: width * width_ratio);
    }

    freq_change { |duration, freqShift=0, desc="freq_change"|
        var f;
        desc.postln;

        f = carrierFreq;

        Pdefn(\carrierFreq, f + freqShift);

        r{
            duration.sleep;
            (desc ++ ":end").postln;

            Pdefn(\carrierFreq, f);
        }.play;
    }

    pulse_change {  | duration, powerShift=0.01, rate=27, width=0.45, desc="Good Slave" |
        desc.postln;

        Pdefn(\pulseRate, rate);
        Pdefn(\pulseWidth, width);

        this.incr_power(value: powerShift);

        r{
            duration.sleep;
            (desc ++ ":end").postln;

            this.decr_power(value: powerShift);
            this.pulse_reset;
        }.play;
    }

    good_slave { | duration |
        this.pulse_change(duration, powerShift: 0.01, rate: 27, width: 0.45, desc: "Good Slave");
    }

    reward { | duration|
        this.pulse_change(duration, powerShift: 0.01, rate: 35, width: 0.45, desc: "Reward");
    }

    push { |duration|
        this.pulse_change(duration, powerShift: 0.005, rate: 60, width: 0.4, desc: "Push");
    }

    push_2 { |duration|
        this.pulse_change(duration, powerShift: 0.005, rate: 35, width: 0.4, desc: "Push 2");
    }

    set_power { |value|
        carrierAmp = value;
        ("set_power: " ++ carrierAmp.asString).postln;

        Pdefn(\carrierAmp, carrierAmp);
    }

    // Reducing width from 0.4 to 0.3 should increase power by a factor of 1.33. This makes it easy.
    change_power { |mul=1.0,add=0|
        ("change_power, mul: " ++ mul.asString ++ " add: " ++ add.asString).postln;

        this.set_power((carrierAmp * mul) + add);
    }

    // We should just remove these
    incr_power { |value=0.005|
        "incr_power".postln;
        this.set_power(value: carrierAmp + value);
    }

    decr_power { |value=0.005|
        "decr_power".postln;
        this.set_power(value: carrierAmp - value);
    }

    // Create node proxies of different kinds
    mk_pulse {
        Pdefn(\pulseIPhase, 0);

        ~pulse.play(bus[\pulse], 2, grp[\signal]);
        ~pulse = Pmono(
            \lfPulseCtrl,
            \dur, 1,
            \freq, Pdefn(\pulseRate),
            \width, Pdefn(\pulseWidth),
            \widthB, 0.4,
            \iphase, Pdefn(\pulseIPhase),
            \amp, 1,
        );
    }

    mk_inv_translate {
        ~translate.play(bus[\translate], 2, grp[\translate]);
        ~translate = Pmono(
            \cartesianTranslate,
            \dur, 1,
            \in, bus[\polar],
        );
    }

    mk_carrier { |bias=0.5|
        var mulX, addX;

        mulX = 1 + bias;
        addX = bias.neg;

        ~carrier.play(0, 2, grp[\carrier]);
        ~carrier = Pmono(
            \phaseEncoder,
            \freq, Pdefn(\carrierFreq),
            \in, bus[\polar],
            \modulate, bus[\gamma],
            \atk, 4,
            \rel, 8,
            \addX, addX,
            \mulX, mulX,
            \amp, Pdefn(\carrierAmp),
        );
    }

    mk_signal {
        ~signal.play(bus[\polar], 2, grp[\signal]);
        ~signal.fadeTime = 1;
    }

    mk_spike {
        ~spike.play(0, 2, grp[\carrier]);
        ~spike.fadeTime = 1;
    }

    mk_nodeproxies { |bias=0.5|
        "making nodeproxies".postln;

        this.mk_pulse;
        this.mk_signal;
        this.mk_spike;
        this.mk_carrier(bias: bias);
    }

    beat_freq { |count=1|
        ^(tempoClock.tempo * count);
    }
}

ClutchBase : ClutchCore {
    edge { |duration, add=0.01|
        ("edge").postln;

        this.incr_power(value: add);

        r{
            duration.sleep;
            "edge:end".postln;

            this.decr_power(value: add);
            this.reset;
        }.play;
    }

    reset {
        "RESET".postln;

        Pdefn(\spikeFreq, 599);
        ~signal = nil;
        ~spike = nil;
    }

    // Signal enables
    stroke_signal {
        "stroke signal".postln;

        ~signal = Pbind(
            \type, \phrase,
            \instrument, \stroke_base,

            \amp, Pdefn(\amp, 1),
            \legato, Pdefn(\legato),
            \wiggle_freq, Pdefn(\wiggle_freq),
            \wiggle, Pdefn(\wiggle),
            \depth, Pdefn(\depth),
            \dur, Pdefn(\dur),
            \dir, Pdefn(\pattern),
        );
    }

    sweep_signal {
        "sweep signal".postln;

        ~signal = Pbind(
            \type, \phrase,
            \instrument, \sweep_base,

            \rho_atk_ratio, Pdefn(\rho_atk_ratio),
            \rho_rel_ratio, Pdefn(\rho_rel_ratio),
            \amp, Pdefn(\amp),
            \legato, Pdefn(\legato),
            \wiggle_freq, Pdefn(\wiggle_freq),
            \wiggle, Pdefn(\wiggle),
            \dur, Pdefn(\dur),
            \depth, Pdefn(\depth),
            \start, Pdefn(\start),
            \end, Pdefn(\end),
            \speed_ratio, Pdefn(\speed_ratio),
            \curve, Pdefn(\curve),
        )
    }

    pingpong_signal {
        "pingpong signal".postln;

        ~signal = Pbind(
            \type, \phrase,
            \instrument, \pingpong_base,

            \atk, Pdefn(\atk),
            \rel, Pdefn(\rel),
            \amp, Pdefn(\amp),
            \legato, Pdefn(\legato),
            \dur, Pdefn(\dur),
            \depth, Pdefn(\depth),
            \p1, Pdefn(\p1),
            \p2, Pdefn(\p2),
            \p3, Pdefn(\p3),
            \p4, Pdefn(\p4),
            \curve, Pdefn(\curve),
            \speed_in, Pdefn(\speed_in),
            \speed_out, Pdefn(\speed_out),
            \curve_in, Pdefn(\curve_in),
            \curve_out, Pdefn(\curve_out),
        );
    }

    pulsar_signal {
        "pulsar spike".postln;

        ~spike = Pbind(
            \instrument, \pulsar,
            \modulate, bus[\delta],
            \atk, Pdefn(\spikeAtk),
            \rel, Pdefn(\spikeRel),
            \amp, Pdefn(\spikeAmp),
            \pos, 1,
            \pulseFreq, Pdefn(\spikePulseFreq),
            \pulseAmp, Pdefn(\spikePulseAmp),
            \dur, Pdefn(\spikeDur),
            \susLevel, Pdefn(\spikeSusLevel),
            \legato, Pdefn(\spikeLegato),
            \freq, Pdefn(\spikeFreq),
        );
    }

    edge_signal {
        ~signal = Pbind(
        	\type, \phrase,
    		\instrument, \osc_base,
    		\amp, Pdefn(\amp),

            \dur, Pdefn(\dur),
            \legato, Pdefn(\legato),
            \dir, Pdefn(\dir),
            \depth, Pdefn(\depth),

            \dirFreq, Pdefn(\dirFreq),
            \dirMul, Pdefn(\dirMul),

            \rhoFreq, Pdefn(\rhoFreq),
            \rhoMul, Pdefn(\rhoMul),

            \thetaFreq, Pdefn(\thetaFreq),
            \thetaMul, Pdefn(\thetaMul),
    	);
    }

    // Pattern library
    pattern { |pat|
        switch(pat)
            {\xy}   { Pdefn(\pattern, Pseq([pX, pY], inf))}
            {\yx}   { Pdefn(\pattern, Pseq([pY, pX], inf))}
            {\xz}   { Pdefn(\pattern, Pseq([pX, 0], inf))}
            {\xyz}  { Pdefn(\pattern, Pseq([pX, pY, 0], inf))}
            {\xyyx} { Pdefn(\pattern, Pseq([pX, pY, pY, pX], inf))}
            {\xxxy} { Pdefn(\pattern, Pseq([Pseq([pX], 3), pY], inf))}
            {\xyxz} { Pdefn(\pattern, Pseq([pX, pY, pX, 0], inf))}
            {\xzyz} { Pdefn(\pattern, Pseq([pX, 0, pY, 0], inf))}
            { "WARNING: Unknown pattern"}
    }

    // Phrase library
    phrase_lib {
        Pdef(\stroke_base, {
            arg dir,
                dur,
                depth,
                wiggle_freq=2,
                legato=0.8,
                wiggle=0.3,
                atk_ratio=0.5,
                rel_ratio=(1/6),
                sine_ratio=0.333;

            dur = dur.value;

            Pbind(\instrument, \stroke,
                \freq, wiggle_freq.value,
                \depth, depth.value,
                \dur, dur,
                \dir, dir.value,

                \atk, dur * atk_ratio,
                \rel, dur * rel_ratio,

                \sine_mul, wiggle.value,
                \sine_atk, dur * sine_ratio,
                \sine_rel, dur * sine_ratio,

                \legato, legato.value;
            )
        });

        Pdef(\pingpong_base, {
            arg atk, rel, curve,
	            p1, p2, p3, p4,
	            speed_in, speed_out,
	            curve_in, curve_out,
	            depth,
                dur;

            Pbind(\instrument, \pingpong,
                \depth, depth.value,
                \atk, atk.value,
                \rel, rel.value,
                \curve, curve.value,
                \dur, dur.value,
                \p1, p1.value,
                \p2, p2.value,
                \p3, p3.value,
                \p4, p4.value,
                \speed_in, speed_in.value,
                \speed_out, speed_out.value,
                \curve_in, curve_in.value,
                \curve_out, curve_out.value,
            )
        });

        Pdef(\sweep_base, {
            arg dur,
                wiggle_freq=8,
                wiggle=0.2,
                depth,
                legato,
                curve=(3.neg),
                rho_atk_ratio=0.2,
                rho_rel_ratio=0.2,
                start, end, speed_ratio;

            dur = dur.value;
            speed_ratio = speed_ratio.value;

            Pbind(\instrument, \sweep,
                \rhoFreq, wiggle_freq.value,
                \rhoAmp, wiggle.value,
                \depth, depth.value,

                \rhoAtk, dur * rho_atk_ratio,
                \rhoRel, dur * rho_rel_ratio,

                \legato, legato.value,

                \curve, curve.value,
                \start, start.value,
                \end, end.value,
                \speed, dur * speed_ratio,
            )
        });

    	Pdef(\osc_base, {
            arg dur,

                atk_ratio=0.25,
                rel_ratio=0.125;

            dur = dur.value;

            Pbind(
                \instrument, \threeOsc,

                \dur, dur,

                \atk, dur * atk_ratio,
                \rel, dur * rel_ratio
            )
        });
    }
}