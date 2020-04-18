# Check for latest version at https://github.com/DinJerr/spritefix

import cv2
import numpy as np
import os

def get_image():
    image_list = []
    for dirpath, _, fnames in sorted(os.walk('./input')):
        for fname in sorted(fnames):
            if (fname.endswith('.png')):
                """
				image_path = os.path.join(dirpath, fname)
                image_list.append(image_path)
				"""
                image_list.append(fname)
    assert image_list, 'No valid image file in input folder'
    return image_list

# ==============================================================================
# Credit to Dan Mašek (StackOverflow)
def blend(face_img, overlay_t_img):

    # Split out the transparency mask from the colour info
    overlay_img = overlay_t_img[:,:,:3] # Grab the BRG planes
    overlay_mask = overlay_t_img[:,:,3:]  # And the alpha plane

    # Again calculate the inverse mask
    background_mask = 255 - overlay_mask

    # Turn the masks into three channel, so we can use them as weights
    overlay_mask = cv2.cvtColor(overlay_mask, cv2.COLOR_GRAY2BGR)
    background_mask = cv2.cvtColor(background_mask, cv2.COLOR_GRAY2BGR)

    # Create a masked out face image, and masked out overlay
    # We convert the images to floating point in range 0.0 - 1.0
    face_part = (face_img * (1 / 255.0)) * (background_mask * (1 / 255.0))
    overlay_part = (overlay_img * (1 / 255.0)) * (overlay_mask * (1 / 255.0))

    # And finally just add them together, and rescale it back to an 8bit integer image    
    return np.uint8(cv2.addWeighted(face_part, 255.0, overlay_part, 255.0, 0.0))
# ==============================================================================

def fixsprite(img):
    # Change from 8-bit img to 32-bit
    img = cv2.cvtColor(img, cv2.COLOR_RGB2RGBA)
    height, width = img.shape[:2]

    # Save original mask
    mask = img[:,:,3]

    # Prepare transformation matrix
    nudges = [np.float32([[1, 0, -1], [0, 1, -1]]),
              np.float32([[1, 0, 1], [0, 1, -1]]),
              np.float32([[1, 0, -1], [0, 1, 1]]),
              np.float32([[1, 0, 1], [0, 1, 1]]),
		      np.float32([[1, 0, -1], [0, 1, 0]]),
              np.float32([[1, 0, 1], [0, 1, 0]]),
              np.float32([[1, 0, 0], [0, 1, -1]]),
              np.float32([[1, 0, 0], [0, 1, 1]])]
    # Discard transparency from processed image
    compimg = cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)

    # Apply duped borders around sprite
    for matrix in nudges:		  
        imgnudged = cv2.warpAffine(img, matrix, (width, height))
        compimg=blend(compimg,imgnudged)
    compimg=blend(compimg,img)

    # Reattach original mask
    img = cv2.cvtColor(compimg, cv2.COLOR_RGB2RGBA)
    img[:, :, 3] = mask
    return img

# ==============================================================================

if __name__ == '__main__':
    img_list = get_image()
    for file in img_list:
        print('Fixing ',file)
        img = cv2.imread('./input/'+file, cv2.IMREAD_UNCHANGED)
        img = fixsprite(img)
        cv2.imwrite('./output/'+file, img)
    print('Finished')