# Record Generator

Converts wave and aifc files to an STL file of a properly encoded of 45 rpm record.
As of v0.2 record shape is configurable.

## Depndencies

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install dependencies.

```bash
pip install -r requirements.txt 
```

## Usage

Add audio file, wav, wave, aifc or aiff, to audio folder then run
```bash
python3 src/lpcm_to_csv.py <filename>
python3 src/record_gen.py
```

## Contributing
For major changes, open an issue to discuss what you would like to change.
