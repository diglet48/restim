/*
 * Clutch --- SuperCollider script
 */
(
// Server Settings
s.options.memSize_(2.pow(20));
s.options.numOutputBusChannels_(2);
s.options.sampleRate = 48000;

// Boot the server and add Synths
s.waitForBoot({
	s.sync;

	/*
	 * TRANSLATION
	 * --------------------------------------------------------------------
	 */

	/*
	 * Translate from cartesian to polar coordinates
	 *
	 * The phaseEncoder expects polar coordinates. This synth translates inputs from a
	 * cartesian world into a polar one
	 */
	SynthDef(\polarTranslate, {
		var in, x, y, rho, theta, sig;

		// Read from input busses for the alpha/beta coordinates
		in = In.ar(\in.kr(0), 2);

		// Set up the coordinates
 		x = in[0];
		y = in[1];

		// Clip rho in the range [0, 1] because essentially these are the values the phaseEncoder
		// will support. If you go outside this range, you start getting a signal which
		// inverts the phase information.
		rho = hypot(x, y).clip(0.0, 1.0);
		theta = atan2(y, x);

		// Output signal is split into the magnitude and direction
		sig = [rho, theta];
		Out.ar(\out.kr(0), sig);
	}).add;

	/* Translate from polar to cartesian coordinates */
	SynthDef(\cartesianTranslate, {
		var in, x, y, rho, theta, sig;
		var env;

		// Read from input
		in = In.ar(\in.kr(0), 2);

		rho = in[0];
		theta = in[1];

		x = cos(theta) * rho;
		y = sin(theta) * rho;

		env = EnvGen.kr(
			Env(
				levels: [0, 1, \sus.kr(1.0), 0],
				times: [\atk.kr(5), 0.5, \rel.kr(5)],
				releaseNode: 2
			),
			\gate.kr(1),
			doneAction: 2);

		sig = [x, y];
		Out.ar(\out.kr(0), sig);
	}).add;

	/*
	 * Calibrate a bus by replacing it with with a calibrated signal.
	 * The calibrated signal is a MulAdd block, so one can place the
	 * origin point differently as well as manipulate the amplitude
	 * of the signals in the X and Y direction.
	 */
	SynthDef(\calibrate, {
		var in, sigX, sigY;

		in = In.ar(\bus.kr(0), 2);

		sigX = MulAdd(in[0], mul: \mulX.kr(1), add: \addX.kr(0));
		sigY = MulAdd(in[1], mul: \mulY.kr(1), add: \addY.kr(0));

		ReplaceOut.ar(\bus.kr(0), [sigX, sigY]);
	}).add;

	/*
	 * SIGNAL
	 * ---------------------------------------
	 */

	// Basic Sines are good stimming signals
	//
	// A lot of stimming signals are based on pure sine waves, with nothing else manipulating
	// the signal. While parameters of the signal can change over time.
	SynthDef(\sine, {
		var sig, env;

		sig = SinOsc.ar(\freq.kr(800), \amp.kr(0.5));
		env = EnvGen.kr(
			Env(
				levels: [0, 1, \sus.kr(1.0), 0],
				times: [\atk.kr(5), 0.5, \rel.kr(5)],
				releaseNode: 2
			),
			\gate.kr(1),
			doneAction: Done.freeSelf);
		Out.ar(\out.kr(0), Pan2.ar(sig, \pan.kr(0), env));
	}).add;

	// Optimized version of the phase encoder. This version folds the translation
	// T directly into the phase-matrix, which shaves off two SinOsc ugens.
	// It produces the same signal as \phaseEncoder.
	SynthDef(\phaseEncoder, {
		var freq, amp, phases, pulse, env, z, mix, in, sig;
		var rho, theta, mod;
		var x,y;

		freq = \freq.kr(800, 1); // Carrier frequency
		amp = \amp.kr(0.5, 2); // General amplitude of the carrier signal

		// in represents the steering-signal. It is read as rho,theta from
		// a 2-channel bus.
		in = In.ar(\in.kr(0), 2);

		rho = in[0];
		theta = in[1];

		// Make sure rho stays within bounds

		rho = rho.clip(0.0001, 0.9999);

		x = cos(theta) * rho;
		y = sin(theta) * rho;

		x = x * \mulX.kr(1, 1) + \addX.kr(0, 1);
		y = y * \mulY.kr(1, 1) + \addY.kr(0, 1);

		rho = hypot(x, y).clip(0.0, 1.0);
		theta = atan2(y, x);

		// Modulation bus which allows modulation of the carrier signal
		// in amplitude.
		mod = In.ar(\modulate.ar(0), 1);

		z = pi/6;

		// Set up the phase-matrix for base and offset. Originally, there
		// were 3 phases here, but we can compute the translation T and
		// dump it directly into the matrix.
		phases = [
			[z.neg, z],
			[z, z.neg] + theta // Multiplication is addition in phase-space
		];

		// Set up the mix array between base and offset.
		// Set up the mix array between base and offset.
		// rho needs to be halved.
		r = rho * 0.5;
		mix = [1 - r, r] * 3.sqrt; // Base/Offset mix

		// Build a matrix of phases and mixes. This distributes the SinOsc inside
		// the matrix we have. Uses a lot of channel expansion.
		sig = SinOsc.ar(freq, phase: phases, mul: mix);

		// Mixdown the inner Base/Offset arrays, producing an array of signals for 1,z,z^2
		sig = Mix.new(sig);

		// Overall shape-control of the carrier. This allows for gentle ramps
		// into and out of the signal. This also sets up a gate so the synth
		// is removed upon being done doing work.
		env = EnvGen.kr(
			Env(
				levels: [0, 1, \sus.kr(1.0), 0],
				times: [\atk.kr(5), 0.5, \rel.kr(5)],
				releaseNode: 2
			),
			\gate.kr(1),
			doneAction: 2);

		// Apply the output transformation T, taking the phase-differences
		// and shape the signal by means of the modulation, envelope, and amp.
		sig = sig * mod * env * amp;

		Out.ar(\out.kr(0), sig);
	}).add;

	/*
	 * CONTROL
	 * -------------------------------------
	 */

	// When \stroke plays, we do a single stroke. This lets us set up stroke
	// patterns on an output bus, and change them as we'd like.
	SynthDef(\stroke, {
		var rho, theta, sig;
		var thetaEnv;
		var atk, gate;

		atk = \atk.kr(0.75);
		gate = \gate.kr(1);

		rho = EnvGen.ar(
			Env.new(
				levels: [0, 1, 1, 0],
				times: [atk, \sus.kr(1), \rel.kr(0.5)],
				curve: [-3, 0, 2],
				releaseNode: 2
			),
			gate,
			doneAction: Done.freeSelf);

		theta = SinOsc.ar(\freq.kr(0.5), mul: \sine_mul.kr(0.3), add: \dir.ar(0, 0.1));
		thetaEnv = EnvGen.ar(
			Env.asr(
				attackTime: \sine_atk.kr(0.03),
				sustainLevel: 1,
				releaseTime: \sine_rel.kr(0.03)
			),
			gate
		);
		rho = rho * \depth.kr(1.0);
		theta = theta * thetaEnv;

		sig = [rho, theta] * \amp.kr(0.1);
		Out.ar(\out.kr(0), sig);
	}).add;

    SynthDef(\threeOsc, {
		var rho, theta, sig;
		var dir;
		var env;

		env = EnvGen.ar(
			Env.new(
				levels: [0, 1, 0.9, 0],
				times: [\atk.kr(0.1), \sus.kr(1), \rel.kr(0.1)],
				curve: [-2, 0, 2],
				releaseNode: 2
			),
			\gate.kr(1),
			doneAction: Done.freeSelf);

		dir = SinOsc.ar(\dirFreq.kr(4), mul: \dirMul.kr(pi/2), add: \dir.kr(0));
		rho = SinOsc.ar(\rhoFreq.kr(4), mul: \rhoMul.kr(0.3), add: \depth.kr(0.8));
		theta = SinOsc.ar(\thetaFreq.kr(4), mul: \thetaMul.kr(0.3)) + dir;

		sig = [rho, theta] * env * \amp.kr(1);
		Out.ar(\out.kr(0), sig);
	}).add;

	SynthDef(\spike, {
		var in;
		var sig, env;

		in = In.ar(\modulate.ar(0), 1);

		env = EnvGen.ar(
			Env.new(
				levels: [0, 1, 0.95, 0],
				times: [\atk.kr(1), \sus.kr(0.2), \rel.kr(0.5)],
				curve: [-2, 0, 2],
				releaseNode: 2
			),
			\gate.kr(1),
			doneAction: Done.freeSelf);

		sig = SinOsc.ar(\freq.kr(599));
		sig = sig * in * env * \amp.kr(1.0);

		sig = LinPan2.ar(sig, pos: \pos.kr(0));
		Out.ar(\out.kr(0), sig);
	}).add;

	SynthDef(\pulsar, {
		var in;
		var sig, pulse, env;

		in = In.ar(\modulate.ar(0), 1);

		env = EnvGen.ar(
			Env.new(
				levels: [0, 1, \susLevel.kr(0.5), 0],
				times: [\atk.kr(1), \sus.kr(1.0), \rel.kr(0.5)],
				curve: [-2, 0, 2],
				releaseNode: 2
			),
			\gate.kr(1),
			doneAction: Done.freeSelf);

		sig = SinOsc.ar(\freq.kr(599));
		pulse = SinOsc.ar(\pulseFreq.kr(20, 1), mul: \pulseAmp.kr(1.2, 1)).clip(0, 1);
		sig = sig * in * pulse * env * \amp.kr(1.0);

		sig = LinPan2.ar(sig, pos: \pos.kr(0));
		Out.ar(\out.kr(0), sig);
	}).add;

	SynthDef(\sweep, {
		var rho, theta, sig;
		var gate;
		var start, end;
		var lag;

		gate = \gate.kr(1);

		rho = EnvGen.ar(
			Env(
				levels: [0, 1, 0],
				times: [\rhoAtk.kr(2),
						\rhoRel.kr(0.05)],
				curve: [2, 0, 0],
				releaseNode: 1,
			),
			gate,
			doneAction: Done.freeSelf
		);

		rho = rho + SinOsc.ar(freq: \rhoFreq.kr(16), mul: \rhoAmp.kr(0.2)) * \depth.kr(1.0);

		start = \start.kr(2pi/3);
		end = \end.kr((2pi/3).neg);

		theta = EnvGen.ar(
			Env(
				levels: [start, end],
				times:  [\speed.kr(1)],
				curve:  [\curve.kr(3)]
			)
		);

		sig = [rho, theta] * \amp.kr(1);
		Out.ar(\out.kr(0), sig);
	}).add;

	SynthDef(\pingpong, {
		var rho, theta, sig;
		var rho_curve;
		var gate;

		gate = \gate.kr(1);

		rho = EnvGen.ar(
			Env(
				levels: [0, 1, 0],
				times: [\atk.kr(2), \rel.kr(0.05)],
				curve: [\curve.kr(2), 0],
				releaseNode: 1,
			),
			gate,
			doneAction: Done.freeSelf
		);

		rho = rho * \depth.kr(1.0);

		theta = EnvGen.ar(
			Env(
				levels: [\p1.kr(2pi/3), \p2.kr(0), \p3.kr((2pi/3).neg), \p4.kr(0)],
				times: [\speed_in.kr(1), \speed_out.kr(1), \sus.kr(1)],
				curve: [\curve_in.kr(2), \curve_out.kr(2), 0],
				releaseNode: 2,
			),
			gate,
		);

		sig = [rho, theta] * \amp.kr(1);
		Out.ar(\out.kr(0), sig);
	}).add;

	SynthDef(\hold, {
		var sig;
		var rho, theta;
		var lag, point;

		lag = \lag.kr(0.5);
		point = \point.ar(2pi/3, lag);

		rho = EnvGen.ar(
			Env(
				levels: [0, 1, 0],
				times: [\rhoAtk.kr(2, lag),
						\rhoSustain.kr(1, lag),
						\rhoRel.kr(0.05, lag)],
				curve: [2, 2],
				releaseNode: 1,
			),
			\gate.kr(1),
			doneAction: Done.freeSelf
		);

		rho = rho + SinOsc.ar(freq: \rhoFreq.kr(4, lag), mul: \rhoAmp.kr(0.2, lag));
		rho = rho * \amp.kr(1.0, lag);

		theta = point;

		sig = [rho, theta];
		Out.ar(\out.kr(0), sig);
	}).add;

	SynthDef(\lfPulseCtrl, {
		var sigA, sigB;
		var freq, amp;

		freq = \freq.kr(50, 1);
		amp = \amp.kr(1, 1);

		sigA = LFPulse.ar(
			freq,
			iphase: 0,
			width: \width.kr(0.45, 1),
			mul: amp
		);

		sigB = LFPulse.ar(
			freq,
			iphase: 0.5,
			width: \widthB.kr(0.5, 1),
			mul: amp
		);

		Out.ar(\out.kr(0), [sigA, sigB]);
	}).add;


	s.sync;
	"Setup done.".postln;
})
)

(
	q = ();
	"./03_act_32_script.scd".loadRelative;
	e = ClutchAct32.new(s);
    t = TempoClock.new(queueSize: 512);
	e.run(
		t, q[\act32],
		record: true,
		description: "03_act32"
	);
)

(
	q = ();
	"./03_act_31_script.scd".loadRelative;
	e = ClutchAct31.new(s);
    t = TempoClock.new(queueSize: 512);
	e.run(
		t, q[\act31],
		record: true,
		description: "03_act31"
	);
)

(
	q = ();
	"./02_act_2_script.scd".loadRelative;

	e = ClutchAct2.new(s);
	t = TempoClock.new;
	e.run(t, q[\act2],
		record: true,
		description: "02_act2");
)

(
	q = ();
	"./01_act_1_script.scd".loadRelative;

	e = ClutchAct1.new(s);
	t = TempoClock.new;
	e.run(t, q[\act1],
		record: true,
		description: "01_act1");
)

(
	q = ();
	"./00_intro_script.scd".loadRelative;

	e = ClutchIntro.new(s);
	t = TempoClock.new;
	e.run(t, q[\intro],
		record: true,
		description: "00_intro");
)

e.mk_inv_translate;
~translate.edit;