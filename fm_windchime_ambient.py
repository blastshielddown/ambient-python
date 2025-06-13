#!/usr/bin/env python3

import signalflow as sf
import time
import threading
import random
import numpy as np
from scipy.io import wavfile

class FMWindChimeAmbience:
    def __init__(self):
        self.graph = sf.AudioGraph()
        self.running = False
        
    def create_fm_bell(self, frequency, velocity=0.7):
        """Create an FM-synthesized bell with velocity control"""
        
        # FM synthesis parameters - reduced for less distortion
        mod_ratio = 3.5  # Metallic timbre
        mod_index = 0.8 * velocity  # Reduced from 1.5 to prevent distortion
        
        # Create a master gate to control when the bell can sound
        master_gate = sf.Constant(0)  # Start silent
        
        # Modulator
        modulator = sf.SineOscillator(frequency * mod_ratio)
        mod_env = sf.ASREnvelope(0.001, 0.1, 1.5)  # Fast attack, longer release
        
        # Scale modulation properly - divide by carrier frequency for stable FM
        modulation = modulator * mod_env * mod_index
        
        # Carrier with FM
        carrier = sf.SineOscillator(frequency * (1.0 + modulation))
        carrier_env = sf.ASREnvelope(0.01, 0.5, 4.5)  # Extended release for more ambient sustain
        
        # Apply carrier envelope with reduced amplitude
        bell = carrier * carrier_env * 0.3
        
        # Add harmonics for richness with lower levels
        harm2 = sf.SineOscillator(frequency * 2.0) * carrier_env * 0.1
        harm3 = sf.SineOscillator(frequency * 2.95) * carrier_env * 0.05  # Slightly inharmonic
        
        # Mix components with overall velocity scaling
        mixed = (bell + harm2 + harm3) * velocity * 0.5
        
        # Apply master gate to control output
        gated = mixed * master_gate
        
        # Gentle high-frequency damping for warmth
        filtered = sf.SVFilter(gated, "low_pass", cutoff=min(frequency * 8, 8000), resonance=0.2)
        
        # Add reverb for space with reduced feedback
        reverb = sf.CombDelay(filtered, delay_time=0.2, feedback=0.4, max_delay_time=2.0)
        final = filtered * 0.8 + reverb * 0.2
        
        return final, mod_env, carrier_env, master_gate
    
    def create_wind_texture(self):
        """Create subtle wind sound that modulates chime activity"""
        # Wind base - reduced volume
        wind_noise = sf.WhiteNoise() * 0.015
        
        # Filter for wind character
        wind_filtered = sf.SVFilter(wind_noise, "band_pass", cutoff=800, resonance=0.3)
        
        # LFO for wind dynamics
        wind_lfo = sf.SineLFO(frequency=0.05, min=0.2, max=1.0)
        
        # Apply dynamics
        wind = wind_filtered * wind_lfo
        
        # Add some low frequency rumble - reduced
        low_noise = sf.WhiteNoise() * 0.01
        low_filtered = sf.SVFilter(low_noise, "low_pass", cutoff=200, resonance=0.1)
        
        # Mix wind components
        wind_mix = wind + low_filtered
        
        # Light reverb
        wind_reverb = sf.CombDelay(wind_mix, delay_time=0.8, feedback=0.4, max_delay_time=3.0)
        
        return wind_mix + wind_reverb * 0.3, wind_lfo
    
    def start_composition(self, duration_minutes=3):
        """Create a 3-minute ambient wind chime composition"""
        print(f"Starting {duration_minutes}-minute FM wind chime ambient piece...")
        
        # Create wind texture
        wind_sound, wind_strength = self.create_wind_texture()
        
        # Define chime frequencies (pentatonic scale across 2 octaves)
        chime_freqs = [
            220.0,   # A3
            246.94,  # B3
            293.66,  # D4
            329.63,  # E4
            392.0,   # G4
            440.0,   # A4
            493.88,  # B4
            587.33,  # D5
            659.25,  # E5
        ]
        
        # Create chime components
        chimes = []
        for i, freq in enumerate(chime_freqs):
            bell, mod_env, carrier_env, master_gate = self.create_fm_bell(freq)
            
            # Position across stereo field
            pan_pos = -0.8 + (i / (len(chime_freqs) - 1)) * 1.6
            panned_bell = sf.StereoPanner(bell, pan_pos)
            
            chimes.append({
                'output': panned_bell,
                'mod_env': mod_env,
                'carrier_env': carrier_env,
                'master_gate': master_gate,
                'freq': freq,
                'last_hit': 0
            })
            
            # Set up the bell audio path
            panned_bell.play()
        
        # Mix all sounds with reduced levels
        all_chimes = sum(chime['output'] for chime in chimes)
        mixed = (all_chimes * 0.15) + (wind_sound * 0.3)
        
        # Final compression and limiting with gentler settings
        compressed = sf.Compressor(mixed, threshold=-12, ratio=1.5, attack_time=0.05, release_time=0.5)
        
        # Gentle EQ - slight high frequency reduction
        final_output = sf.SVFilter(compressed, "low_pass", cutoff=10000, resonance=0.1)
        
        # Create recording buffer
        sample_rate = self.graph.sample_rate
        buffer_seconds = duration_minutes * 60
        buffer = sf.Buffer(2, int(sample_rate * buffer_seconds))
        
        # Record and play
        recorder = sf.BufferRecorder(buffer, final_output)
        recorder.play()
        final_output.play()
        
        # Wind also plays separately
        wind_sound.play()
        
        # Chime triggering thread
        def trigger_chimes():
            while self.running:
                # Wind strength affects chime frequency
                current_time = time.time()
                
                # Base wind strength (0-1)
                base_wind = 0.3 + 0.7 * (0.5 + 0.5 * np.sin(current_time * 0.02))
                
                # Add gusts
                if random.random() < 0.1:  # 10% chance of gust
                    base_wind = min(1.0, base_wind + random.uniform(0.2, 0.4))
                
                # Interval between chimes based on wind - increased for more space
                base_interval = 1.5
                interval = base_interval * (2.5 - base_wind) + random.uniform(-0.3, 0.3)
                interval = max(0.4, interval)
                
                time.sleep(interval)
                
                if self.running:
                    # Select chimes that haven't been hit recently
                    available = []
                    current_time = time.time()
                    
                    for i, chime in enumerate(chimes):
                        if current_time - chime['last_hit'] > 1.5:  # 1.5 second cooldown for more space
                            available.append(i)
                    
                    if available:
                        # Random chance for adjacent bells to ring together
                        selected = []
                        first_idx = random.choice(available)
                        selected.append(first_idx)
                        
                        # 30% chance for adjacent bells
                        if random.random() < 0.3:
                            adjacent_candidates = []
                            for idx in available:
                                if abs(idx - first_idx) == 1 and idx not in selected:
                                    adjacent_candidates.append(idx)
                            
                            if adjacent_candidates:
                                # Can select 1-2 adjacent bells
                                num_adjacent = random.randint(1, min(2, len(adjacent_candidates)))
                                selected.extend(random.sample(adjacent_candidates, num_adjacent))
                        
                        # Small chance for distant harmony
                        elif random.random() < 0.15:
                            # Look for harmonic intervals (3rd, 5th)
                            harmony_candidates = []
                            for idx in available:
                                interval = abs(idx - first_idx)
                                if interval in [2, 4] and idx not in selected:  # 3rd or 5th in scale
                                    harmony_candidates.append(idx)
                            
                            if harmony_candidates:
                                selected.append(random.choice(harmony_candidates))
                        
                        # Trigger selected chimes
                        for i, idx in enumerate(selected):
                            chime = chimes[idx]
                            
                            # Velocity based on wind with wider range for more variance
                            velocity = 0.15 + (base_wind * 0.5) + random.uniform(-0.1, 0.15)
                            velocity = max(0.1, min(0.8, velocity))
                            
                            # Trigger with slight delay for rolling effect
                            if i > 0:
                                time.sleep(random.uniform(0.02, 0.08))
                            
                            # Enable the bell and trigger envelopes
                            chime['master_gate'].set_value(1)
                            chime['mod_env'].trigger()
                            chime['carrier_env'].trigger()
                            chime['last_hit'] = time.time()
        
        # Start composition
        self.running = True
        
        # Start without any initial chime - let the wind build naturally
        
        # Start chime triggering thread
        chime_thread = threading.Thread(target=trigger_chimes)
        chime_thread.daemon = True
        chime_thread.start()
        
        # Let composition play
        time.sleep(duration_minutes * 60)
        
        # Stop and export
        self.running = False
        
        print("Exporting audio to WAV file...")
        audio_data = buffer.data.T
        
        # Normalize
        max_val = np.max(np.abs(audio_data))
        if max_val > 0:
            audio_data = audio_data / max_val * 0.9
        
        # Apply fade in/out
        fade_samples = int(sample_rate * 2)  # 2 second fades
        # Fade in
        for i in range(fade_samples):
            audio_data[i] *= i / fade_samples
        # Fade out
        for i in range(fade_samples):
            audio_data[-(i+1)] *= i / fade_samples
        
        # Convert to 16-bit
        audio_data = np.int16(audio_data * 32767)
        
        # Save
        filename = f"fm_windchime_ambient_{duration_minutes}min.wav"
        wavfile.write(filename, sample_rate, audio_data)
        print(f"Audio exported to: {filename}")
        
        # Clean up
        self.graph.stop()
        self.graph.destroy()
        print("FM wind chime ambient piece completed!")

def main():
    windchimes = FMWindChimeAmbience()
    
    print("FM Wind Chime Ambient Generator")
    print("Features:")
    print("- FM-synthesized tubular bells")
    print("- Wind-driven triggering system")
    print("- Dynamic wind strength with gusts")
    print("- Multiple chimes triggered in strong wind")
    print("- Stereo positioning")
    print("- Subtle wind texture")
    print()
    
    try:
        windchimes.start_composition(duration_minutes=3)
    except KeyboardInterrupt:
        print("\nStopping composition...")
        windchimes.running = False
        windchimes.graph.stop()
        windchimes.graph.destroy()

if __name__ == "__main__":
    main()