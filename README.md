# Computer vision Handwriting

## What's that?

This project analyzes movements of palm and fingers and applies the corresponding changes. To be specific, man can draw, erase and move the cursor over the canvas.

At the very start the program renders your camera's view to help you with aiming and understanding the boundaries you can draw within. When it notices a palm it opens another window to demonstrate what you are drawing.

## How to use?

If you stick your forefinger out and connect your middle finger with your thumb you can draw with black ink. Due to lags and delays the program is set up to interpolate between points to smoothen the handwriting. It uses a simple linear algorithm to connect a pair of points.

If you connect your forefinger with middle finger you can erase. In order to erase in a more convenient way it applies a white semi-square both to work fast and erase a big spot.

To move the cursor free you can stick your thumb to the side. The program renders the cursor to aid you with aiming (the size of the cursor does not correlate with the size the marker)
