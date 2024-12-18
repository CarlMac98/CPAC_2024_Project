s.boot;
s.options.numWireBufs = 150;
Server.killAll;




(
MIDIdef.noteOn(\simpleNotes, {
|val, num, chan, src, ptrdelay = 0.2, rate = 0.5, buf = 0, dryWet = 1 |
{
var amp, freq, x, mod1, mod2, ptr, maxgraindur, sig; // chan & src declared but not used
freq = num.midicps;
amp = val.linexp(1, 127, 0.01, 0.25);
mod2 = SinOsc.ar(2 * freq * [0, 0.1].midiratio, mul: 450);
mod1 = SinOsc.ar(0,5 * freq * [0, 0.1].midiratio + mod2, mul: 800);
x = SinOsc.ar(freq * [0, 0.1].midiratio + mod1) * amp;
x = x * Env.perc.kr(2);
// We implement the granulator effect
	ptr = Phasor.ar(0, BufRateScale.ir(0), 0, BufFrames.ir(0));
	maxgraindur = ptrdelay / rate;
	BufWr.ar(x, buf, ptr);
	sig = GrainBuf.ar(
		numChannels: 2,
		trigger: Dust.kr(16),
		dur: min(0.3, maxgraindur),
		sndbuf: buf,
		rate: rate,
		pos: (ptr - (ptrdelay  * SampleRate.ir))  / BufFrames.ir(buf),
		envbufnum: -1,
		interp: 4,
		maxGrains: 64
	);
	Out.ar(0, XFade2.ar(x, sig, dryWet));
}.play;
});
 )



MIDIdef(\simpleNotes).disable;
MIDIdef(\simpleNotes).enable;

(
~amp = {
	arg fundFreq, p_pose = 2;
	var i = 0;
	var n = 50;
	// Amplpitude array creation
	a = Array.fill(n,{0});
    n.do({
		a[i] =((2*p_pose.squared)/(squared(i+1)*pi.squared*(p_pose-1)))*sin((i+1)*pi/p_pose);
		i = i+1;
	});
	// We normalize the array amplitude so that the sum of all the sinusoids is 1 (we apply a -3dB attenuation to avoid multiple notes playing at the same time and avoid clipping)
    a = a.normalizeSum * 0.5;
	// return as an array both arrays
	a;
};
// Frequency modes calculation
~freq = {
	arg fundFreq, stiffness = 0;
	var i = 0;
	var n = 50;
	// here we just divide by 1000 to have more sensibility on the input number
	var stiffness_small = stiffness/(1000);
	// This is a constant detune that will be applied to each frequency mode except the fundamental
	var detune = stiffness_small + (stiffness_small.squared);
	// This is a part of the detuning that will depend on the frequency mode
	var variable_part = pi.squared * stiffness_small.squared/8;
	// Frequency array creation (here we apply the detuning to each frequency mode)
	f = Array.fill(n,{0});
    n.do({
		f[i] =(i+1)*fundFreq * (1 + detune + ((i+1).squared * variable_part));
		i = i+1;
	});
	f[0]=fundFreq;
	f;
};
// String simulation Synth
MIDIdef(\simpleNotes,{ |trig = 1, midinote = 70, modulation , vel = 1, buf = 0, rate = 2, ptrdelay = 0.2, dryWet = 0|
	var env, amp, freq, p, x, sig, ptr, gran, maxgraindur;
    amp = ~amp.value(midinote.midicps, modulation) * vel;
    freq = ~freq.value(midinote.midicps, 11);
	env = EnvGen.kr(Env.perc(0.01, 0.2 + vel, 1, curve:-4), trig, doneAction: 2);
	// All sine waves summed together
	x = SinOsc.ar(freq, 0, amp).sum;
	// We implement the granulator effect
	ptr = Phasor.ar(0, BufRateScale.ir(0), 0, BufFrames.ir(0));
	maxgraindur = ptrdelay / rate;
	BufWr.ar(x * env, buf, ptr);
	sig = GrainBuf.ar(
		numChannels: 2,
		trigger: Dust.kr(16),
		dur: min(0.3, maxgraindur),
		sndbuf: buf,
		rate: rate,
		pos: (ptr - (ptrdelay  * SampleRate.ir))  / BufFrames.ir(buf),
		envbufnum: -1,
		interp: 4,
		maxGrains: 64
	);
	Out.ar(0, XFade2.ar(x * env, sig, dryWet));
}).add;
)

(
MIDIdef.noteOn(\simpleNotes, {
|val, num, chan, src| // chan & src declared but not used
{
var sig, freq, amp, mod1, mod2;
/*freq = num.midicps;
amp = val.linexp(1, 127, 0.01, 0.25);
sig = SinOsc.ar(freq * [0, 0.1].midiratio) * amp;
sig = sig * Env.perc.kr(2);*/
freq = num.midicps;
amp = val.linexp(1, 127, 0.01, 0.25);
mod2 = SinOsc.ar(2 * freq * [0, 0.1].midiratio, mul: 450);
mod1 = SinOsc.ar(0,5 * freq * [0, 0.1].midiratio + mod2, mul: 800);
x = SinOsc.ar(freq * [0, 0.1].midiratio + mod1) * amp;
x = x * Env.perc.kr(2);
}.play;
});
 )
MIDIIn.connectAll;
(
MIDIdef.noteOn(\simpleNotes,{
	|val, num, chan, src|
{

		Rongs.ar(trigger: val, sustain: 1, f0: num.midicps, structure: 1, brightness: 0.3, damping: 0.1, accent: 0.9, stretch: 0.7, position: 0.5, loss: 0.5, modeNum: 4, cosFreq:1) * Env.perc.kr(1);
}.play;
});
)

Platform.userExtensionDir