import time
from tiny_fx import TinyFX
from machine import Pin
from neopixel import NeoPixel
from picofx import ColourPlayer, MonoPlayer
from picofx.colour import RGBBlinkFX, RainbowFX
from picofx.mono import PulseWaveFX, BlinkWaveFX, FlickerFX

# Program settings
TEST_MODE = False
NEOPIXELS_COUNT = 3

# Initialize hardware
tiny = TinyFX()
sensor_pin = Pin(tiny.SENSOR_PIN)
pixels = NeoPixel(sensor_pin, n=NEOPIXELS_COUNT, bpp=3)
colour_player = ColourPlayer(tiny.rgb)
mono_player = MonoPlayer(tiny.outputs)

# Christmas colors (RGB values)
COLORS = [
    (255, 0, 0),     # Red
    (0, 255, 0),     # Green
    (0, 0, 255),     # Blue
    (255, 255, 0),   # Yellow
    (255, 0, 255),   # Magenta
    (0, 255, 255),   # Cyan
    (255, 255, 255), # White
    (255, 128, 0),   # Orange
]

def test_mono_outputs(tiny):
    # Turn all on
    for _ in range(2):
        for output in tiny.outputs:
            output.brightness(1.0)
            time.sleep(0.5)
            output.brightness(0)
    time.sleep(0.5)  # All off period
    for output in tiny.outputs:
        output.brightness(1.0)
    time.sleep(0.5)
    for output in tiny.outputs:
        output.brightness(0)
    time.sleep(0.5)

def test_rgb_output(tiny):
    # Test each color channel individually
    test_colors = [
        (255, 255, 255), # White
        (255, 0, 0),    # Red
        (0, 255, 0),    # Green
        (0, 0, 255),    # Blue
        (255, 255, 0),  # Yellow
        (255, 0, 255),  # Magenta
        (0, 255, 255),  # Cyan
        (255, 255, 255), # White
        (0, 0, 0), # Off
        (255, 255, 255), # White
        (255, 255, 255) # White
    ]
        
        # Turn on each color for 0.5s
    for color in test_colors:
        for i in range(NEOPIXELS_COUNT):
            pixels[i] = color
            pixels.write()
            time.sleep(0.5)
        tiny.rgb.set_rgb(*color)
        time.sleep(0.5)
        for i in range(NEOPIXELS_COUNT):
            pixels[i] = (0, 0, 0)
            pixels.write()
            time.sleep(0.5)
        tiny.rgb.set_rgb(0, 0, 0)
        time.sleep(0.5)


def setup_christmas_effects():
    # RGB effects
    rgb_effects = [
        RainbowFX(speed=0.5),
        RGBBlinkFX(colour=COLORS, speed=1, duty=0.5),
        RainbowFX(speed=2.0)
    ]

    # Mono effects - distribute across outputs with phase offsets
     #[
        #[
    mono_effects = [PulseWaveFX(speed=0.3, length=2)(i % 2) for i in range(0, 6)]
        # [PulseWaveFX(speed=1, length=6) for _ in range(6)],
        # [BlinkWaveFX(speed=1, length=6, duty=0.5) for _ in range(6)],
        # [BlinkWaveFX(speed=1, length=6, duty=0.5) for _ in range(6)],
        # [FlickerFX(brightness=1.0, dimness=0.3) for _ in range(6)],
        # [FlickerFX(brightness=1.0, dimness=0.3) for _ in range(6)]
    # ]

    return rgb_effects, mono_effects

def button_switch_mode_check():
    if tiny.boot_pressed():
        while tiny.boot_pressed():
            pass
        return True
    return False

setup = False
try:
    while True:
        if TEST_MODE:
            test_mono_outputs(tiny)
            if button_switch_mode_check():
                TEST_MODE = False
                continue
            test_rgb_output(tiny)
            setup = False
            if button_switch_mode_check():
                TEST_MODE = False
        else:
            if not setup:
                setup = True
                rgb_effects, mono_effects = setup_christmas_effects()
                mono_player.effects = mono_effects
                colour_player.effects = rgb_effects[0]
                colour_player.pair(mono_player)
            colour_player.start()

            while colour_player.is_running():
                if button_switch_mode_check():
                    colour_player.stop()
                    TEST_MODE = True
                    break
                # attribute not available until after first tick, comes as float 0-1 brightness per channel
                r = getattr(tiny.rgb.led_r,"__brightness") if hasattr(tiny.rgb.led_r,"__brightness") else 0
                g = getattr(tiny.rgb.led_g,"__brightness") if hasattr(tiny.rgb.led_g,"__brightness") else 0
                b = getattr(tiny.rgb.led_b,"__brightness") if hasattr(tiny.rgb.led_b,"__brightness") else 0
                r = min(255, round(r * 255))
                g = min(255, round(g * 255))
                b = min(255, round(b * 255))
                # copy the RGB effect to the NeoPixels
                pixels.fill((r, g, b))
                pixels.write()
                time.sleep(0.002)
            
            # # Run each pattern type for 2 cycles
            # for rgb_effect, mono_effect in zip(rgb_effects, mono_effects):
                
            #     for _ in range(2):  # 2 cycles

finally:
    colour_player.stop()
    # mono_player.stop()
    tiny.shutdown()

