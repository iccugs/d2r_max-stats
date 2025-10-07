# Diablo 2 Resurrected Save File Stats Editor

A Python utility for modifying character statistics in Diablo 2 Resurrected save files (.d2s). This tool allows you to set character attributes (Strength, Energy, Dexterity, Vitality) and optionally modify HP and Mana display values.

## Features

- Set character stats (STR/ENE/DEX/VIT) to any value up to 1023 (10-bit maximum)
- Optionally modify HP and Mana display values
- Automatically backs up original save files
- Recomputes and updates the save file checksum to maintain file integrity
- Creates a new modified file while preserving the original

## Requirements

- Python 3.x
- Diablo 2 Resurrected save files (.d2s format)

## Installation

1. Clone or download this repository
2. Ensure Python 3 is installed on your system
3. No additional dependencies required - uses only Python standard library

## Usage

### Basic Usage

```bash
python set_stats_and_hpmp.py <file.d2s>
```

This will set all four main stats (Strength, Energy, Dexterity, Vitality) to 999 (default value).

### Advanced Usage

```bash
python set_stats_and_hpmp.py <file.d2s> [stat_value] [hp_display] [mana_display]
```

#### Parameters

- `file.d2s` - Path to your Diablo 2 Resurrected save file
- `stat_value` - Value to set for all four main stats (default: 999, max: 1023)
- `hp_display` - Optional HP display value (e.g., 5000)
- `mana_display` - Optional Mana display value (e.g., 5000)

### Examples

```bash
# Set stats to default 999
python set_stats_and_hpmp.py MyCharacter.d2s

# Set stats to 500
python set_stats_and_hpmp.py MyCharacter.d2s 500

# Set stats to 999 and HP/Mana display to 5000 each
python set_stats_and_hpmp.py MyCharacter.d2s 999 5000 5000

# Set only stats to maximum (1023)
python set_stats_and_hpmp.py MyCharacter.d2s 1023
```

## How It Works

1. **File Reading**: Reads the binary .d2s save file
2. **Backup Creation**: Creates a backup copy with .bak extension
3. **Attribute Parsing**: Locates and parses the character attributes section
4. **Bit Manipulation**: Modifies the packed bit fields containing stat values
5. **Checksum Update**: Recalculates and updates the file checksum
6. **File Output**: Writes the modified data to a new file with "_modified" suffix

## File Output

- **Original file**: Remains unchanged
- **Backup file**: `filename.d2s.bak` (exact copy of original)
- **Modified file**: `filename_modified.d2s` (contains your changes)

## Technical Details

### Save File Structure

The tool manipulates specific sections of the Diablo 2 save file format:

- **Attributes Offset**: 0x2FD (765 bytes from start)
- **Checksum Offset**: 0x0C (12 bytes from start)
- **Section Header**: `0x67 0x66` (marks start of attributes)

### Stat Bit Lengths

Different stats use different bit lengths in the save file:
- STR/ENE/DEX/VIT: 10 bits each (max value 1023)
- HP/MaxHP/Mana/MaxMana: 21 bits each
- HP/Mana values are stored as fixed-point numbers (display_value × 256)

### Safety Features

- Automatic value clamping to prevent overflow
- Checksum recalculation to prevent file corruption
- Original file preservation through backup system
- Error handling for invalid files or missing sections

## Limitations

- Only works with Diablo 2 Resurrected save files (.d2s format)
- Maximum stat value is 1023 due to 10-bit storage limitation
- Modifies only the four main character attributes and HP/Mana display values
- Does not modify skill points, inventory, or other character data

## Safety and Backup

This tool automatically creates backups of your save files. However, it's recommended to:

1. Keep additional backups of important characters
2. Test modifications on characters you don't mind losing
3. Verify the game accepts modified files before relying on them

## Troubleshooting

### Common Issues

- **"file not found"**: Check the file path and ensure the .d2s file exists
- **"file too small"**: The file may be corrupted or not a valid .d2s file
- **"attributes header missing"**: The save file format may be different than expected

### File Compatibility

This tool is designed for Diablo 2 Resurrected save files. It may not work with:
- Original Diablo 2 save files
- Corrupted save files
- Save files from unsupported game versions

## License

This project is provided as-is for educational and personal use. Use at your own risk.

## Disclaimer

Modifying save files may violate game terms of service. This tool is intended for single-player use only. The authors are not responsible for any consequences of using modified save files, including but not limited to account bans or character loss.