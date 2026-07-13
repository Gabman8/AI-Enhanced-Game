import cv2
import numpy as np

def generate_spites():
    img = cv2.imread("characters_images_raw/Main_running.png", cv2.IMREAD_UNCHANGED)
    print('Image ' + img)
    alpha = img[:, :, 3]

    _, thresh = cv2.threshold(alpha, 1, 255, cv2.THRESH_BINARY)

    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(thresh)

    for i in range(1, num_labels):

        x = stats[i, cv2.CC_STAT_LEFT]
        y = stats[i, cv2.CC_STAT_TOP]
        w = stats[i, cv2.CC_STAT_WIDTH]
        h = stats[i, cv2.CC_STAT_HEIGHT]

        sprite = img[y:y+h, x:x+w]

        cv2.imwrite(f"sprite_{i}.png", sprite)
