#!/bin/bash

rm -rf build_engine/ build_player/ spec_engine/ spec_player/

# Run Player builder and wait for it to finish
#python3 build_player.py
#wait

# Run Engine builder for gui version and wait for it to finish
python3 build_engine.py gui
wait

# Run Engine builder for CLI version
python3 build_engine.py

# Print success message
echo "Builds complete"
