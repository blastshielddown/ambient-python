# Ambient Python

A collection of ambient music generators using Python and SignalFlow for real-time audio synthesis.

## Overview

This repository contains multiple ambient music compositions that generate evolving soundscapes through algorithmic synthesis. Each piece uses different synthesis techniques to create immersive, meditative audio experiences with unique characteristics and moods.

## Requirements

- Python 3.7+
- SignalFlow audio library
- NumPy
- SciPy (for WAV export functionality)

Install dependencies:
```bash
pip install signalflow numpy scipy
```

## Compositions

### FM Dorian Ambient (Featured)
**`fm_dorian_ambient.py`** - A sophisticated 3-minute ambient piece featuring:
- C Dorian mode chord progressions with random 7th extensions
- FM synthesis electric keyboard with saw wave harmonics
- 24-tap cascading delay system creating lush echo trails
- Continuous C2 drone with auto-retriggering
- Ethereal shimmer layer with ultra-slow LFO modulation
- Random chord timing offsets (0-0.5 seconds) for organic feel
- Comprehensive spatial reverb effects

**WAV Export Version:** `fm_dorian_ambient_export.py` - Silent recording version that exports to WAV file

Run live:
```bash
python fm_dorian_ambient.py
```

Export to WAV:
```bash
python fm_dorian_ambient_export.py
```

### Multi-Channel Ambient Soundscape
**`ambient_multichannel.py`** - A layered ambient composition featuring:
- Deep drones positioned across stereo field
- Evolving pad layers with filter modulation
- Textural noise elements for movement
- Sparse bell-like tones with dramatic panning
- Spatial positioning with dynamic movement
- Auto-exports to WAV after performance

Run:
```bash
python ambient_multichannel.py
```

### FM Wind Chime Ambient
**`fm_windchime_ambient.py`** - The original wind chime piece featuring:
- Multiple wind chime voices with random timing
- FM synthesis bell tones
- Spatial positioning across stereo field
- Evolving harmonic progressions
- Natural decay and resonance

Run:
```bash
python fm_windchime_ambient.py
```

### Additional Examples
The repository also includes various synthesis examples and building blocks:
- `lydian_piano.py` - Piano composition in Lydian mode
- `fm_synth_demo.py` - FM synthesis demonstration
- `sound_generator.py` - Basic synthesis examples

## Features

- **Real-time audio synthesis** using SignalFlow
- **Algorithmic composition** with generative elements
- **Spatial audio positioning** and stereo effects
- **Professional delay and reverb processing**
- **WAV export capabilities** for high-quality recordings
- **Multiple synthesis techniques** (FM, subtractive, additive)
- **Unique performances** each time due to randomization

## Usage Tips

- Use headphones or good monitors for the best spatial experience
- Each piece generates unique variations on every run
- Export versions create WAV files for sharing or further processing
- Adjust volume appropriately as pieces build in intensity

## License

This project is open source and available under the MIT License.