# Record Generator

Converts wave files to stl of 45 rpm record.

## Depndencies

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install dependencies.

```bash
pip install -r requirements.txt 
```

## Usage

### CLI
Add audio file, wav, wave, aifc or aiff, to audio folder then run
```bash
python3 src/lpcm_to_csv.py <filename>
mkdir pickle
python3 src/basic_shape_gen.py
python3 src/record_gen.py
```

## Contributing
For major changes, open an issue to discuss what you would like to change.
