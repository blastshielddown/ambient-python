# FM Wind Chime Ambient

An ambient audio generator that creates the sound of wind chimes being triggered by a varying breeze, using FM synthesis for rich, tubular bell sounds.

## Features

- **FM-synthesized tubular bells** with metallic, resonant timbres
- **Wind-driven triggering system** that responds to dynamic wind patterns
- **Stereo positioning** with bells arranged from low (left) to high (right) frequencies
- **Adjacent bell harmonies** - bells next to each other sometimes ring together
- **Dynamic velocity range** for natural-sounding strikes
- **3-minute ambient compositions** with automatic WAV export

## Requirements

- Python 3.7+
- signalflow library
- scipy
- numpy

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Run the ambient generator:
```bash
python fm_windchime_ambient.py
```

The script will:
- Generate a 3-minute ambient wind chime composition
- Play it in real-time through your speakers
- Automatically export it as `fm_windchime_ambient_3min.wav`

## How It Works

### Bell Synthesis
Each bell is created using FM synthesis with:
- A 3.5x frequency modulator for metallic character
- Multiple harmonics for richness
- Individual stereo positioning
- Velocity-sensitive brightness

### Wind System
The wind system controls:
- **Timing**: Stronger wind = more frequent chime strikes
- **Velocity**: Wind strength affects how loud each strike is
- **Grouping**: Adjacent bells can ring together in stronger wind
- **Harmonies**: Occasional harmonic intervals (3rds, 5ths)

### Stereo Arrangement
Bells are positioned across the stereo field by pitch:
- **Left**: Lower frequencies (A3, B3, D4)
- **Center**: Mid frequencies (E4, G4)  
- **Right**: Higher frequencies (A4, B4, D5, E5)

## Generated Files

- `fm_windchime_ambient_3min.wav` - The generated ambient composition

## License

MIT License - Feel free to use and modify for your projects!