#!/usr/bin/env python3

import signalflow as sf
import time
import random
import numpy as np
from scipy.io import wavfile

def create_electric_keyboard_note(frequency, velocity=1.0):
    """Create an electric keyboard sound using FM synthesis"""
    
    # Classic electric piano FM parameters
    mod_ratio = 1.0  # 1:1 ratio for bell-like electric piano tone
    mod_freq = frequency * mod_ratio
    
    # Create gate that starts at 0 (silent)
    gate = sf.Constant(0)
    
    # Modulator with envelope
    modulator = sf.SineOscillator(mod_freq)
    mod_env = sf.ASREnvelope(0.2, 0.05, 0.8)  # Faster attack for brighter sound
    
    # Modulation index for electric piano brightness (increased for brighter timbre)
    mod_index = 4.5
    modulation = modulator * mod_env * mod_index * frequency
    
    # Carrier frequency with FM
    carrier_freq = frequency + modulation
    carrier = sf.SineOscillator(carrier_freq)
    
    # Carrier envelope with long sustain for ambient chords
    carrier_env = sf.ASREnvelope(1.0, 0.0, 8.0)  # Long attack, infinite sustain, long release
    
    # Apply envelope and velocity, gated by the gate signal
    electric_tone = carrier * carrier_env * velocity * gate
    
    # Add brighter harmonic content with saw wave for bite
    harmonic = sf.SineOscillator(frequency * 2.0) * carrier_env * 0.3 * gate
    harmonic3 = sf.SawOscillator(frequency * 3.0) * carrier_env * 0.12 * gate  # Saw wave for bite
    
    # Mix fundamental and harmonics
    mixed = electric_tone + harmonic + harmonic3
    
    # Add slight chorus effect for electric keyboard character
    chorus_delay = sf.OneTapDelay(mixed, delay_time=0.007, max_delay_time=0.02)
    
    # Mix dry and chorus
    final = mixed * 0.8 + chorus_delay * 0.3
    
    return final * 0.08, mod_env, carrier_env, gate

def export_to_wav(filename="dorian_ambient_3min.wav"):
    """Export the 3-minute ambient piece to a WAV file"""
    print(f"Exporting Dorian ambient piece to {filename}...")
    
    # Initialize audio graph
    graph = sf.AudioGraph()
    
    # Calculate timing first
    bpm = 82
    measures_per_chord = 4
    beats_per_measure = 4
    chord_duration = (measures_per_chord * beats_per_measure * 60) / bpm  # 11.71 seconds
    total_duration = 180.0  # 3 minutes
    
    # Define 4 different chord intervals in C Dorian mode with optional 7ths
    # C Dorian: C D Eb F G A Bb C
    chord_definitions = [
        [('C3', 130.81), ('F3', 174.61), ('Bb3', 233.08)],   # C - F - Bb (C minor 7th)
        [('D3', 146.83), ('G3', 196.00), ('C4', 261.63)],    # D - G - C (D minor 7th) 
        [('F3', 174.61), ('Bb3', 233.08), ('Eb4', 311.13)],  # F - Bb - Eb (F minor 7th)
        [('G3', 196.00), ('C4', 261.63), ('F4', 349.23)]     # G - C - F (G minor 7th)
    ]
    
    # Create all possible voices for all chord notes
    all_voices = {}
    
    # Create voices for each unique note
    unique_notes = {}
    for chord in chord_definitions:
        for note_name, freq in chord:
            if note_name not in unique_notes:
                unique_notes[note_name] = freq
    
    print(f"Creating voices for notes: {list(unique_notes.keys())}")
    
    # Create master mixer for recording
    master_mix = sf.Sum()
    
    # Create continuous drone voice (C2 - low C for foundational drone)
    drone_freq = 65.41  # C2
    drone_voice, drone_mod_env, drone_carrier_env, drone_gate = create_electric_keyboard_note(drone_freq, velocity=0.1)
    
    # Add heavy reverb to drone for atmospheric effect
    drone_reverb1 = sf.CombDelay(drone_voice, delay_time=0.3, feedback=0.8, max_delay_time=1.0)
    drone_reverb2 = sf.CombDelay(drone_voice, delay_time=0.45, feedback=0.7, max_delay_time=1.0)
    drone_reverb3 = sf.CombDelay(drone_voice, delay_time=0.6, feedback=0.6, max_delay_time=1.0)
    
    # Mix drone with heavy reverb
    drone_output = (drone_voice * 0.3 + 
                   drone_reverb1 * 0.4 + 
                   drone_reverb2 * 0.2 + 
                   drone_reverb3 * 0.1)
    
    # Center the drone in stereo field
    drone_stereo = sf.StereoPanner(drone_output, 0.0)
    master_mix.add_input(drone_stereo)
    
    # Start the drone immediately
    drone_gate.set_value(1)
    drone_mod_env.trigger()
    drone_carrier_env.trigger()
    print("Started continuous C2 drone")
    
    # Create ethereal shimmer layer - starting at C5
    shimmer_freq1 = 523.25  # C5
    shimmer_freq2 = 1046.5  # C6 (one octave above C5)
    
    # Create LFOs for organic movement (slowed to 1/3 rate)
    shimmer_lfo1 = sf.SineLFO(0.023, 0.95, 1.05)  # Ultra slow frequency modulation
    shimmer_lfo2 = sf.SineLFO(0.037, 0.0, 0.3)    # Ultra slow amplitude modulation
    shimmer_lfo3 = sf.SineLFO(0.043, -0.8, 0.8)   # Ultra slow stereo panning
    
    # Create the shimmer oscillators with LFO modulation
    shimmer_osc1 = sf.SineOscillator(shimmer_freq1 * shimmer_lfo1)
    shimmer_osc2 = sf.TriangleOscillator(shimmer_freq2 * 0.5 * shimmer_lfo1 * 1.02)  # Triangle wave one octave lower
    
    # Mix shimmer oscillators with gentle amplitude modulation (heavily reduced)
    shimmer_mix = (shimmer_osc1 + shimmer_osc2) * 0.004 * (1.0 + shimmer_lfo2)
    
    # Add high-frequency EQ cut around 8kHz using low-pass filter
    shimmer_filtered = sf.SVFilter(shimmer_mix, "low_pass", cutoff=8000, resonance=0.3)  # Gentle roll-off above 8kHz
    
    # Add ethereal reverb to shimmer
    shimmer_reverb1 = sf.CombDelay(shimmer_filtered, delay_time=0.8, feedback=0.85, max_delay_time=2.0)
    shimmer_reverb2 = sf.CombDelay(shimmer_filtered, delay_time=1.1, feedback=0.75, max_delay_time=2.0)
    shimmer_with_reverb = shimmer_filtered + shimmer_reverb1 * 0.6 + shimmer_reverb2 * 0.4
    
    # Apply dynamic stereo panning to shimmer for movement
    shimmer_stereo = sf.StereoPanner(shimmer_with_reverb, shimmer_lfo3)
    master_mix.add_input(shimmer_stereo)
    
    print("Added ethereal shimmer layer")
    
    # Create chord voices
    for note_name, freq in unique_notes.items():
        voice, mod_env, carrier_env, gate = create_electric_keyboard_note(freq, velocity=0.2)
        
        # Add stereo positioning based on pitch
        if note_name.endswith('3'):
            pan_pos = -0.3  # Lower notes to the left
        else:
            pan_pos = 0.3   # Higher notes to the right
        
        stereo_voice = sf.StereoPanner(voice, pan_pos)
        
        # Add rhythmic delay effect - half-measure delay (1.46 seconds at 82 BPM)
        delay_time = (2 * 60) / bpm  # Half-measure = 2 beats
        
        # Create multiple feedback delays for repeating echoes (24 echoes total for longer tail)
        delay1 = sf.OneTapDelay(stereo_voice, delay_time=delay_time, max_delay_time=12.0)
        delay2 = sf.OneTapDelay(delay1, delay_time=delay_time, max_delay_time=12.0) * 0.8
        delay3 = sf.OneTapDelay(delay2, delay_time=delay_time, max_delay_time=12.0) * 0.8
        delay4 = sf.OneTapDelay(delay3, delay_time=delay_time, max_delay_time=12.0) * 0.8
        delay5 = sf.OneTapDelay(delay4, delay_time=delay_time, max_delay_time=12.0) * 0.8
        delay6 = sf.OneTapDelay(delay5, delay_time=delay_time, max_delay_time=12.0) * 0.8
        delay7 = sf.OneTapDelay(delay6, delay_time=delay_time, max_delay_time=12.0) * 0.8
        delay8 = sf.OneTapDelay(delay7, delay_time=delay_time, max_delay_time=12.0) * 0.8
        delay9 = sf.OneTapDelay(delay8, delay_time=delay_time, max_delay_time=12.0) * 0.8
        delay10 = sf.OneTapDelay(delay9, delay_time=delay_time, max_delay_time=12.0) * 0.8
        delay11 = sf.OneTapDelay(delay10, delay_time=delay_time, max_delay_time=12.0) * 0.8
        delay12 = sf.OneTapDelay(delay11, delay_time=delay_time, max_delay_time=12.0) * 0.8
        delay13 = sf.OneTapDelay(delay12, delay_time=delay_time, max_delay_time=12.0) * 0.8
        delay14 = sf.OneTapDelay(delay13, delay_time=delay_time, max_delay_time=12.0) * 0.8
        delay15 = sf.OneTapDelay(delay14, delay_time=delay_time, max_delay_time=12.0) * 0.8
        delay16 = sf.OneTapDelay(delay15, delay_time=delay_time, max_delay_time=12.0) * 0.8
        delay17 = sf.OneTapDelay(delay16, delay_time=delay_time, max_delay_time=12.0) * 0.8
        delay18 = sf.OneTapDelay(delay17, delay_time=delay_time, max_delay_time=12.0) * 0.8
        delay19 = sf.OneTapDelay(delay18, delay_time=delay_time, max_delay_time=12.0) * 0.8
        delay20 = sf.OneTapDelay(delay19, delay_time=delay_time, max_delay_time=12.0) * 0.8
        delay21 = sf.OneTapDelay(delay20, delay_time=delay_time, max_delay_time=12.0) * 0.8
        delay22 = sf.OneTapDelay(delay21, delay_time=delay_time, max_delay_time=12.0) * 0.8
        delay23 = sf.OneTapDelay(delay22, delay_time=delay_time, max_delay_time=12.0) * 0.8
        delay24 = sf.OneTapDelay(delay23, delay_time=delay_time, max_delay_time=12.0) * 0.8
        
        # Mix all delay taps with heavily reduced levels to prevent buffer overrun
        delay_output = (delay1 * 0.3 + delay2 * 0.28 + delay3 * 0.26 + delay4 * 0.24 + 
                       delay5 * 0.22 + delay6 * 0.2 + delay7 * 0.18 + delay8 * 0.16 + 
                       delay9 * 0.14 + delay10 * 0.12 + delay11 * 0.1 + delay12 * 0.09 + 
                       delay13 * 0.08 + delay14 * 0.07 + delay15 * 0.06 + delay16 * 0.05 +
                       delay17 * 0.04 + delay18 * 0.03 + delay19 * 0.025 + delay20 * 0.02 +
                       delay21 * 0.015 + delay22 * 0.01 + delay23 * 0.008 + delay24 * 0.005)
        
        # Add multiple reverb stages for spacious feeling
        reverb1 = sf.CombDelay(stereo_voice, delay_time=0.18, feedback=0.75, max_delay_time=1.0)
        reverb2 = sf.CombDelay(stereo_voice, delay_time=0.27, feedback=0.65, max_delay_time=1.0)
        reverb3 = sf.CombDelay(stereo_voice, delay_time=0.35, feedback=0.55, max_delay_time=1.0)
        reverb4 = sf.CombDelay(stereo_voice, delay_time=0.43, feedback=0.45, max_delay_time=1.0)
        
        # Mix dry signal, delay, and multiple reverbs (extremely reduced for stability)
        final_voice = (stereo_voice * 0.03 + 
                      delay_output * 0.1 +
                      reverb1 * 0.03 + 
                      reverb2 * 0.015 + 
                      reverb3 * 0.003 + 
                      reverb4 * 0.0)
        
        all_voices[note_name] = {
            'output': final_voice,
            'mod_env': mod_env,
            'carrier_env': carrier_env,
            'gate': gate,
            'freq': freq
        }
        
        # Connect to master mix
        master_mix.add_input(final_voice)
    
    # Create recording buffer and recorder
    sample_rate = graph.sample_rate
    buffer = sf.Buffer(2, int(sample_rate * total_duration))  # Stereo buffer
    recorder = sf.BufferRecorder(buffer, master_mix)
    recorder.play()
    
    print(f"Each chord will be sustained for {chord_duration} seconds")
    
    # Create random chord sequence for 3 minutes
    num_chords = int(total_duration / chord_duration)  # About 15 chords
    
    # Generate random chord sequence
    random.seed(42)  # For reproducible randomness
    chord_sequence = []
    for i in range(num_chords):
        chord_idx = random.randint(0, 3)
        chord_sequence.append(chord_idx)
    
    print(f"Generated random sequence of {len(chord_sequence)} chords")
    print("Chord sequence:", [f"Chord {i+1}" for i in chord_sequence])
    
    # Play the sequence
    start_time = time.time()
    last_drone_trigger = 0  # Track when we last triggered the drone
    
    for seq_idx, chord_idx in enumerate(chord_sequence):
        chord_notes = chord_definitions[chord_idx]
        chord_name = f"Chord {chord_idx + 1}: {chord_notes[0][0]}-{chord_notes[1][0]}"
        
        current_time = time.time() - start_time
        
        # Re-trigger drone every 5 measures (5 * 4 beats * 60s / 82 BPM = 14.63 seconds)
        drone_retrigger_interval = (5 * 4 * 60) / bpm  # 5 measures
        if current_time - last_drone_trigger >= drone_retrigger_interval:
            drone_mod_env.trigger()
            drone_carrier_env.trigger()
            last_drone_trigger = current_time
            print(f"Re-triggered drone at {current_time:.1f}s")
        
        # Trigger chord notes with random timing (including optional 7th)
        chord_triggers = []
        
        # Always include the first two notes (root and 5th/4th)
        for i in range(2):
            note_name, freq = chord_notes[i]
            offset = random.uniform(0.0, 0.5)  # Random offset up to 0.5 seconds
            chord_triggers.append((offset, note_name))
        
        # Randomly include the 7th (third note) - 70% chance
        if len(chord_notes) > 2 and random.random() < 0.7:
            note_name, freq = chord_notes[2]  # The 7th
            offset = random.uniform(0.0, 0.5)
            chord_triggers.append((offset, note_name))
        
        # Sort by offset time
        chord_triggers.sort(key=lambda x: x[0])
        
        # Show what notes are being played
        played_notes = [note_name for offset, note_name in chord_triggers]
        has_seventh = len(chord_triggers) > 2
        seventh_indicator = " (+7th)" if has_seventh else ""
        print(f"Time {current_time:.1f}s: Playing {played_notes}{seventh_indicator}")
        
        # Trigger notes with their calculated offsets
        start_chord_time = time.time()
        for offset, note_name in chord_triggers:
            # Wait until it's time for this note
            elapsed = time.time() - start_chord_time
            if offset > elapsed:
                time.sleep(offset - elapsed)
            
            voice = all_voices[note_name]
            voice['gate'].set_value(1)
            voice['mod_env'].trigger()
            voice['carrier_env'].trigger()
        
        # Wait for chord duration (accounting for maximum random offset)
        time.sleep(chord_duration - 0.5)  # Subtract the maximum offset time
        
        # Check if we're approaching 3 minutes
        if time.time() - start_time > 170:  # Stop triggering new chords near the end
            break
    
    # Let final chord ring out to complete 3 minutes
    final_time = time.time() - start_time
    remaining_time = 180.0 - final_time
    
    if remaining_time > 0:
        print(f"Letting final chord decay for {remaining_time:.1f} seconds...")
        time.sleep(remaining_time)
    
    print("Recording complete, processing audio...")
    
    # Export to WAV
    audio_data = buffer.data.T  # Transpose for correct channel format
    
    # Normalize to prevent clipping
    max_val = np.max(np.abs(audio_data))
    if max_val > 0:
        audio_data = audio_data / max_val * 0.9  # Leave some headroom
    else:
        print("Warning: No audio data recorded!")
        audio_data = np.zeros_like(audio_data)
    
    # Convert to 16-bit integer
    audio_data = np.int16(audio_data * 32767)
    
    # Write WAV file
    wavfile.write(filename, sample_rate, audio_data)
    
    # Clean up
    graph.stop()
    graph.destroy()
    
    print(f"Successfully exported to {filename}")
    print(f"Duration: {total_duration} seconds")
    print(f"Sample rate: {sample_rate} Hz")
    print(f"Channels: 2 (stereo)")
    
    return filename

if __name__ == "__main__":
    filename = "dorian_ambient_3min.wav"
    export_to_wav(filename)