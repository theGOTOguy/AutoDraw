import argparse
import pyautogui
import time

from PIL import Image
from PIL import ImageColor


parser = argparse.ArgumentParser(
        "Automatically draw a provided image into Ring of Pain's Twitch Integration.  "
        "Before starting, select the smallest draw cursor size.")

parser.add_argument('--image', required=True, help="Your image to draw.  It should be cropped already to an appropriate dimension.")
parser.add_argument('--delay', type=int, default=5, help="Number of seconds to allow user to adjust mouse cursor.")
parser.add_argument('--dots_horizontal', type=int, default=175, help="Horizontal Resolution")
parser.add_argument('--dots_vertical', type=int, default=225, help="Vertical Resolution")
parser.add_argument('--pause', type=float, help="If provided, pause for this many seconds after each pyautogui action.")
parser.add_argument('--click-pause', type=float, help="If provided, pause for this long after each simualted click.", default=0.5)
parser.add_argument('--draw-rate', type=float, help="The number of seconds to take during each edge draw.", default=0.2)

args = parser.parse_args()

if args.pause:
  pyautogui.PAUSE = args.pause


def get_color_palette(red_location, dark_grey_location):
  html_colors = [
     "#ec2c2f",
     "#ef39b2",
     "#3456aa",
     "#35a0d3",
     "#6aae04",
     "#6fd84d",
     "#f9a225",
     "#f9c62b",
     "#9d6752",
     "#fef8de",
     "#5e6b7c",
     "#afb6ef",
     "#131a20",
     "#2f4346"]

  result = {}
  y_step = int((dark_grey_location.y - red_location.y) / 6.0)
  dark_grey_location_y = red_location.y + y_step * 6 + 1

  html_idx = 0
  for y in range(int(red_location.y), int(dark_grey_location_y), y_step):
    for x in [int(red_location.x), int(dark_grey_location.x)]:
      result[html_colors[html_idx]] = {'x': x, 'y': y}
      html_idx += 1

  return result

def square_error(color_a, color_b):
  return ((color_a[0] - color_b[0]) ** 2 +
          (color_a[1] - color_b[1]) ** 2 +
          (color_a[2] - color_b[2]) ** 2)


def perform_best_area_draw(color, x, y, top_left_draw, bottom_right_draw, color_map, has_been_colored):
  pyautogui.moveTo(
      top_left_draw.x + (bottom_right_draw.x - top_left_draw.x) * (float(x) / float(args.dots_horizontal)),
      top_left_draw.y + (bottom_right_draw.y - top_left_draw.y) * (float(y) / float(args.dots_vertical)))
  pyautogui.mouseDown()

  cx = x
  cy = y

  num_moves = 0
  NUM_MOVE_THRESHOLD = 5

  while True:
    # Evaluate each of the four directions we can go.  We're going to see which way we can
    # go that colors the most of what needs to be colored along the way, then go that way.
    # If nothing can be done, then we break.
    num_moves += 1
    best_up_score = 0
    best_down_score = 0
    best_left_score = 0
    best_right_score = 0

    # Up
    for ty in range(cy, -1, -1):
      if color_map[cx][ty] == color or not has_been_colored[cx][ty]:
        if color_map[cx][ty] == color and not has_been_colored[cx][ty]:
          best_up_score += 1
      else:
        break

    # Down
    for ty in range(cy, args.dots_vertical):
      if color_map[cx][ty] == color or not has_been_colored[cx][ty]:
        if color_map[cx][ty] == color and not has_been_colored[cx][ty]:
          best_down_score += 1
      else:
        break

    # Left
    for tx in range(cx, -1, -1):
      if color_map[tx][cy] == color or not has_been_colored[tx][cy]:
        if color_map[tx][cy] == color and not has_been_colored[tx][cy]:
          best_left_score += 1
      else:
        break

    # Right 
    for tx in range(cx, args.dots_horizontal):
      if color_map[tx][cy] == color or not has_been_colored[tx][cy]:
        if color_map[tx][cy] == color and not has_been_colored[tx][cy]:
          best_right_score += 1
      else:
        break

    # See if we have painted ourselves into a corner.
    if not best_up_score and not best_down_score and not best_left_score and not best_right_score:
      break

    # Otherwise, let's see which one is the biggest.
    if best_left_score >= best_right_score and best_left_score >= best_up_score and best_left_score >= best_down_score:
      # Left
      for tx in range(cx, -1, -1):
        if color_map[tx][cy] == color or not has_been_colored[tx][cy]:
          if color_map[tx][cy] == color and not has_been_colored[tx][cy]:
            has_been_colored[tx][cy] = True
            end = {'x': tx, 'y': cy}
        else:
          break

    elif best_right_score >= best_up_score and best_right_score >= best_down_score:
      # Right
      for tx in range(cx, args.dots_horizontal):
        if color_map[tx][cy] == color or not has_been_colored[tx][cy]:
          if color_map[tx][cy] == color and not has_been_colored[tx][cy]:
            has_been_colored[tx][cy] = True
            end = {'x': tx, 'y': cy}
        else:
          break

    elif best_up_score >= best_down_score:
      # Up
      for ty in range(cy, -1, -1):
        if color_map[cx][ty] == color or not has_been_colored[cx][ty]:
          if color_map[cx][ty] == color and not has_been_colored[cx][ty]:
            has_been_colored[cx][ty] = True
            end = {'x': cx, 'y': ty}
        else:
          break

    else:
      # Down
      for ty in range(cy, args.dots_vertical):
        if color_map[cx][ty] == color or not has_been_colored[cx][ty]:
          if color_map[cx][ty] == color and not has_been_colored[cx][ty]:
            has_been_colored[cx][ty] = True
            end = {'x': cx, 'y': ty}
        else:
          break

    pyautogui.moveTo(
        top_left_draw.x + (bottom_right_draw.x - top_left_draw.x) * (float(end['x']) / float(args.dots_horizontal)),
        top_left_draw.y + (bottom_right_draw.y - top_left_draw.y) * (float(end['y']) / float(args.dots_vertical)),
        args.draw_rate,
        pyautogui.easeOutQuad)

    cx = end['x']
    cy = end['y']

  pyautogui.mouseUp()
  if num_moves < NUM_MOVE_THRESHOLD:
    time.sleep(args.click_pause)


if __name__ == "__main__":
  print("Hover the mouse over the upper left corner of the draw area.  You have {} seconds.".format(args.delay))
  time.sleep(args.delay)
  top_left_draw = pyautogui.position()
  print(top_left_draw)

  print("Hover the mouse over the bottom right corner of the draw area.  You have {} seconds.".format(args.delay))
  time.sleep(args.delay)
  bottom_right_draw = pyautogui.position()
  print(bottom_right_draw)

  print("Hover the mouse over the color palette selector.  You have {} seconds.".format(args.delay))
  time.sleep(args.delay)
  color_palette = pyautogui.position()
  print(color_palette)

  print("Click the color palette and hover over the center of red in the upper left.  You have {} seconds.".format(args.delay))
  time.sleep(args.delay)
  palette_red = pyautogui.position()
  print(palette_red)

  print("Hover over the center of dark grey in the lower right.  You have {} seconds.".format(args.delay))
  time.sleep(args.delay)
  palette_dark_grey = pyautogui.position()
  print(palette_dark_grey)

  color_map = get_color_palette(palette_red, palette_dark_grey)

  img = Image.open(args.image)
  img = img.resize((args.dots_horizontal, args.dots_vertical))

  print("Pre-planning your image.")
  # First we pre-plan the color for each position.
  choice_by_position = [["" for _ in range(args.dots_vertical)] for _ in range(args.dots_horizontal)]
  has_been_drawn_by_position = [[False for _ in range(args.dots_vertical)] for _ in range(args.dots_horizontal)]

  for x in range(args.dots_horizontal):
    for y in range(args.dots_vertical):
      pixel_rgb = img.getpixel((x, y))

      nearest_distance = None 

      for test_color, _ in color_map.items():
        test_color_rgb = ImageColor.getcolor(test_color, "RGB")
        test_distance = square_error(pixel_rgb, test_color_rgb)

        if nearest_distance is None or test_distance < nearest_distance:
          nearest_distance = test_distance
          choice_by_position[x][y] = test_color

  print("Now drawing.")
  # Actually Draw.
  for color, location in color_map.items():
    print("Drawing {}".format(color))
    # Select the color in question.
    pyautogui.moveTo(color_palette.x, color_palette.y)
    time.sleep(args.click_pause)
    pyautogui.click()
    time.sleep(args.click_pause)
    pyautogui.moveTo(location['x'], location['y'])
    time.sleep(args.click_pause)
    pyautogui.click()
    time.sleep(args.click_pause)
 
    for x in range(args.dots_horizontal):
      for y in range(args.dots_vertical):
        if choice_by_position[x][y] == color and not has_been_drawn_by_position[x][y]:
          perform_best_area_draw(color, x, y, top_left_draw, bottom_right_draw, choice_by_position, has_been_drawn_by_position)












