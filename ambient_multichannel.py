#!/usr/bin/env python3

import signalflow as sf
import time
import threading
import random
import numpy as np
from scipy.io import wavfile

class AmbientSoundscape:

    def __init__(self):
        self.graph = sf.AudioGraph()
        self.env = sf.SpatialEnvironment()
        self.setup_speakers()
        self.layers = []
        self.running = False
        
    def setup_speakers(self):
        # Stereo setup: left and right speakers
        self.env.add_speaker(0, -1.0, 0.0, 0.0)   # Left
        self.env.add_speaker(1, 1.0, 0.0, 0.0)    # Right
    
    def create_pad_layer(self, base_freq, x_pos, y_pos, detune_amount=0.02):
        # Create detuned oscillators for richness
        osc1 = sf.SineOscillator(base_freq)
        osc2 = sf.SineOscillator(base_freq * (1 + detune_amount))
        osc3 = sf.SineOscillator(base_freq * (1 - detune_amount))
        
        # Mix oscillators
        pad = (osc1 + osc2 + osc3) * 0.15
        
        # Apply very slow filter modulation
        filter_lfo = sf.SineLFO(frequency=0.03, min=base_freq * 0.5, max=base_freq * 4)
        filtered_pad = sf.SVFilter(pad, "low_pass", cutoff=filter_lfo, resonance=0.5)
        
        # Add reverb with delay
        delayed = sf.CombDelay(filtered_pad, delay_time=1.2, feedback=0.8, max_delay_time=5.0)
        
        # Apply amplitude modulation for breathing effect
        amp_lfo = sf.SineLFO(frequency=0.008, min=0.3, max=1.0)
        breathing_pad = delayed * amp_lfo
        
        # Add dramatic panning modulation
        pan_lfo = sf.SineLFO(frequency=0.05, min=-1.0, max=1.0)  # Faster pan (20 second cycle)
        pan_position = pan_lfo  # Full left-right sweeps
        
        # Position in space
        positioned = sf.SpatialPanner(self.env, breathing_pad, x=pan_position, y=y_pos, z=0.0)
        
        return positioned
    
    def create_texture_layer(self, x_pos, y_pos):
        # Noise-based texture
        noise = sf.WhiteNoise() * 0.08
        
        # Multiple filter stages for complex texture
        hp_filtered = sf.SVFilter(noise, "high_pass", cutoff=800, resonance=0.1)
        
        # Modulated bandpass for evolving texture
        bp_freq_lfo = sf.SineLFO(frequency=0.04, min=1200, max=3000)
        bp_filtered = sf.SVFilter(hp_filtered, "band_pass", cutoff=bp_freq_lfo, resonance=0.6)
        
        # Tremolo effect - increased sustain, slower tremolo
        tremolo_lfo = sf.SineLFO(frequency=0.03, min=0.5, max=1.0)
        textured = bp_filtered * tremolo_lfo
        
        # Add reverb
        reverb_textured = sf.CombDelay(textured, delay_time=1.5, feedback=0.85, max_delay_time=4.5)
        
        # Position in space
        positioned = sf.SpatialPanner(self.env, reverb_textured, x=x_pos, y=y_pos, z=0.0)
        
        return positioned
    
    def create_drone_layer(self, freq, x_pos, y_pos):
        # Very slow frequency modulation
        freq_mod_lfo = sf.SineLFO(frequency=0.01, min=freq * 0.98, max=freq * 1.02)
        
        # Deep drone with subtle movement
        drone_osc = sf.SineOscillator(freq_mod_lfo)
        
        # Low pass filtering
        filtered_drone = sf.SVFilter(drone_osc, "low_pass", cutoff=freq * 2, resonance=0.1)
        
        # Subtle amplitude envelope
        amp_mod = sf.SineLFO(frequency=0.01, min=0.6, max=1.0)
        modulated_drone = filtered_drone * amp_mod * 0.2
        
        # Add reverb
        reverb_drone = sf.CombDelay(modulated_drone, delay_time=1.6, feedback=0.8, max_delay_time=6.0)
        
        # Add moderate panning modulation for drones
        drone_pan_lfo = sf.SineLFO(frequency=0.02, min=-0.8, max=0.8)  # Moderate pan (50 second cycle)
        drone_pan_position = drone_pan_lfo * 0.6  # Substantial movement but not full sweep
        
        # Position in space
        positioned = sf.SpatialPanner(self.env, reverb_drone, x=drone_pan_position, y=y_pos, z=0.0)
        
        return positioned
    
    def create_bass_layer(self, freq, x_pos, y_pos):
        # Bass layer - offset frequency to avoid masking
        bass_freq = freq * 0.75  # Between drone and octave below for distinction
        
        # Very slow frequency modulation
        freq_mod_lfo = sf.SineLFO(frequency=0.005, min=bass_freq * 0.98, max=bass_freq * 1.02)
        
        # Deep bass oscillator - saw wave for more harmonics
        bass_osc = sf.SawOscillator(freq_mod_lfo)
        
        # Low pass filtering for deep tone - higher cutoff to preserve more harmonics
        filtered_bass = sf.SVFilter(bass_osc, "low_pass", cutoff=bass_freq * 3, resonance=0.2)
        
        # Very subtle amplitude envelope - twice as long as drone
        amp_mod = sf.SineLFO(frequency=0.0125, min=0.8, max=1.0)  # Half the frequency = twice as long
        modulated_bass = filtered_bass * amp_mod * 0.5  # Much higher volume
        
        # Add deep reverb
        reverb_bass = sf.CombDelay(modulated_bass, delay_time=2.4, feedback=0.85, max_delay_time=8.0)
        
        # Keep bass centered - no panning
        # Position in space
        positioned = sf.SpatialPanner(self.env, reverb_bass, x=0.0, y=y_pos, z=0.0)
        
        return positioned
    
    def create_bell_layer(self, base_freq, x_pos, y_pos):
        # Add some detuning modulation to base frequency
        detune_lfo = sf.SineLFO(frequency=0.09, min=0.99, max=1.01)
        modulated_freq = base_freq * detune_lfo
        
        # Chord-like harmonics for warmer, more musical bell sound
        root = sf.SineOscillator(modulated_freq) * 0.8           # Root note
        third = sf.SineOscillator(base_freq * 1.25) * 0.6       # Major third
        fifth = sf.SineOscillator(base_freq * 1.5) * 0.5        # Perfect fifth
        octave = sf.SineOscillator(base_freq * 2.0) * 0.3       # Octave
        
        bell = root + third + fifth + octave
        
        # Add low-pass filtering for deeper tone
        filtered_bell = sf.SVFilter(bell, "low_pass", cutoff=base_freq * 6, resonance=0.2)
        
        # Slow attack envelope that repeats
        bell_env = sf.ASREnvelope(8.0, 12.0, 8.0)  # Very slow envelope
        bell_sound = filtered_bell * bell_env * 0.15
        
        # Add reverb for bells
        reverb_bell = sf.CombDelay(bell_sound, delay_time=2.0, feedback=0.9, max_delay_time=8.0)
        
        # Add dramatic panning modulation for bells
        bell_pan_lfo = sf.SineLFO(frequency=0.03, min=-1.0, max=1.0)  # Faster pan (33 second cycle)
        bell_pan_position = bell_pan_lfo  # Full left-right sweeps
        
        # Position in space
        positioned = sf.SpatialPanner(self.env, reverb_bell, x=bell_pan_position, y=y_pos, z=0.0)
        
        return positioned, bell_env
    
    def start_composition(self, duration_minutes=5):
        print(f"Starting {duration_minutes}-minute ambient soundscape...")

        # Create multiple layers across the stereo field
        
        # Deep drones positioned left and right
        drone1 = self.create_drone_layer(55, -0.8, 0.0)   # Left
        drone2 = self.create_drone_layer(82.4, 0.8, 0.0)   # Right
        
        # Pad layers positioned across stereo field
        pad1 = self.create_pad_layer(220, -0.5, 0.0, 0.015)  # Left side
        pad2 = self.create_pad_layer(329.6, 0.5, 0.0, 0.025)  # Right side
        pad3 = self.create_pad_layer(164.8, 0.0, 0.0, 0.03)   # Center
        
        # Texture layers for movement
        texture1 = self.create_texture_layer(-0.6, 0.0)  # Left
        texture2 = self.create_texture_layer(0.6, 0.0)    # Right
        
        # Bell layers for sparkle
        bell1, bell1_env = self.create_bell_layer(220, -0.7, 0.0)
        bell2, bell2_env = self.create_bell_layer(330, 0.7, 0.0)
        
        # Mix all layers together with reduced gain to prevent clipping
        mixed_layers = (drone1 + drone2 + pad1 + pad2 + pad3 + texture1 + texture2 + bell1 + bell2) * 0.7
        
        # Apply light compression/maximizer to the mix
        compressed = sf.Compressor(mixed_layers, threshold=-18, ratio=2.5, attack_time=0.1, release_time=0.5)
        
        # Apply EQ - gentle high frequency roll-off around 7kHz
        eq_output = sf.SVFilter(compressed, "low_pass", cutoff=8000, resonance=0.2)
        
        # Create buffer for recording (stereo, duration in seconds)
        # Use the actual audio graph sample rate
        sample_rate = self.graph.sample_rate
        buffer_seconds = duration_minutes * 60
        buffer = sf.Buffer(2, int(sample_rate * buffer_seconds))
        
        # Record the final output to buffer
        recorder = sf.BufferRecorder(buffer, eq_output)
        recorder.play()
        
        # Also play the processed mix for real-time listening
        eq_output.play()
        
        # Start bell envelopes on different schedules
        def trigger_bells():
            while self.running:
                time.sleep(random.uniform(15, 30))  # Random intervals
                if self.running:
                    bell1_env.trigger()
                time.sleep(random.uniform(10, 25))
                if self.running:
                    bell2_env.trigger()
        
        self.running = True
        bell_thread = threading.Thread(target=trigger_bells)
        bell_thread.daemon = True
        bell_thread.start()
        
        # Let the composition play
        time.sleep(duration_minutes * 60)
        
        # Clean up
        self.running = False
        
        # Export the recorded audio to WAV file
        print("Exporting audio to WAV file...")
        audio_data = buffer.data  # Shape: (channels, frames)
        
        # Transpose for scipy (expects frames, channels)
        audio_data = audio_data.T
        
        # Normalize to prevent clipping
        max_val = np.max(np.abs(audio_data))
        if max_val > 0:
            audio_data = audio_data / max_val
        
        # Apply gentle limiting to prevent crackling
        audio_data = np.clip(audio_data, -0.95, 0.95)
        
        # Convert to 16-bit integer
        audio_data = np.int16(audio_data * 32767)
        
        # Save as WAV file
        filename = f"ambient_soundscape_{duration_minutes}min.wav"
        wavfile.write(filename, sample_rate, audio_data)
        print(f"Audio exported to: {filename}")
        
        self.graph.stop()
        self.graph.destroy()
        print("Ambient soundscape completed.")

def main():
    soundscape = AmbientSoundscape()
    
    print("Multi-channel Ambient Soundscape")
    print("Features:")
    print("- Deep drones positioned left and right")
    print("- Evolving pads across the stereo field")
    print("- Textural elements for movement")
    print("- Sparse bell-like tones for punctuation")
    print("- Stereo spatial positioning with dramatic panning")
    print()
    
    try:
        soundscape.start_composition(duration_minutes=3)  # 3-minute demo
    except KeyboardInterrupt:
        print("\nStopping soundscape...")
        soundscape.running = False
        soundscape.graph.stop()
        soundscape.graph.destroy()

if __name__ == "__main__":
    main()