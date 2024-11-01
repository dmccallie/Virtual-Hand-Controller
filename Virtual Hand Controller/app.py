from flask import Flask, render_template, request, jsonify
import asyncio
from alpaca.telescope import Telescope

app = Flask(__name__)

# Initialize Telescope
T = Telescope('localhost:32323', 0)  # Local Omni Simulator
print(f'Connected to {T.Name}')
print(T.Description)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

async def slew_telescope(ra, dec):
    """Async function to slew the telescope to given RA and Dec."""
    try:
        if hasattr(T, 'SlewToCoordinatesAsync'):
            slew_method = getattr(T, 'SlewToCoordinatesAsync')
            if callable(slew_method):
                print(f"ready to async slew to coordinates: RA={ra:.2f}, Dec={dec:.2f} using {slew_method}")
                # await slew_method(ra, dec)  # Call the async method
                await T.SlewToCoordinatesAsync(ra, dec) 
            else:
                print("SlewToCoordinatesAsync is not callable.")
        else:
            print("SlewToCoordinatesAsync method not found.")
    except Exception as e:
        print(f"Error during slewing: {e}")

def slew_telescope_sync(ra, dec):
    """SYNCHRONOUS function to slew the telescope to given RA and Dec."""
    try:
        print(f"ready to slew to coordinates: RA={ra:.2f}, Dec={dec:.2f}")
        # await slew_method(ra, dec)  # Call the async method
        T.SlewToCoordinatesAsync(ra, dec) 
    except Exception as e:
        print(f"Error during slewing: {e}")

@app.route('/message', methods=['POST'])
#async def receive_message():
def receive_message():
    """Handle incoming messages and issue commands based on button presses."""
    data = request.get_json()  # Get JSON data
    direction = data.get('message')  # Get the direction sent from the button
    speed = data.get('speed', 100)  # Get speed from JSON, defaulting to 100

    # Adjust the movement increments based on speed
    ra_increment = 0.5 * (speed / 100)  # Scale RA increment by speed
    dec_increment = 0.5 * (speed / 100)  # Scale Dec increment by speed
    print(f"Received {direction} command with speed {speed} dec_inc={dec_increment} ra_inc={ra_increment}")
    try:
        if direction == "up":
            current_dec = T.Declination
            new_dec = current_dec + dec_increment  # Move the telescope up (increase Dec)
            #await slew_telescope(T.RightAscension, new_dec)
            slew_telescope_sync(T.RightAscension, new_dec)

        elif direction == "down":
            current_dec = T.Declination
            new_dec = current_dec - dec_increment  # Move the telescope down (decrease Dec)
            # await slew_telescope(T.RightAscension, new_dec)
            slew_telescope_sync(T.RightAscension, new_dec)

        elif direction == "left":
            current_ra = T.RightAscension
            new_ra = current_ra - ra_increment  # Move the telescope left (decrease RA)
            # await slew_telescope(new_ra, T.Declination)
            slew_telescope_sync(new_ra, T.Declination)

        elif direction == "right":
            current_ra = T.RightAscension
            new_ra = current_ra + ra_increment  # Move the telescope right (increase RA)
            # await slew_telescope(new_ra, T.Declination)
            slew_telescope_sync(new_ra, T.Declination)

        else:
            print("Unknown button direction")
            return jsonify(status="error", message="Unknown direction")

        return jsonify(status="success", message=f"Received {direction} command")

    except Exception as e:
        print(f"Error during processing: {e}")
        return jsonify(status="error", message="Error during processing")

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)  # Disable reloader to avoid threading issues
