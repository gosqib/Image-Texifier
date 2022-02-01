from typing import Annotated, Any, Generator, List, Literal, Optional, Tuple, Union
import cv2 as cv # type: ignore
import numpy as np
from math import ceil

def black_white(img: np.ndarray) -> np.ndarray:
    return cv.cvtColor(img, cv.COLOR_BGR2GRAY)

def C_resize(img: np.ndarray, text_width_min: int = 800) -> np.ndarray:
    """resize image - used to resize the text image accordingly
    width_min expects the minimum width of the text-based image's 
    which is used to create the image with
    """

    scale_factor = text_width_min / img.shape[1] #img.shape[1] is width
    height, width = (
        dimension * scale_factor
        for dimension
        in img.shape[: 2] # gives (height, width)
    )

    # cv2.resize requires int arguments
    # map over list comp for performance boost even accounting for tuple conversion
    dimensions: map[int] = map(int, (width, height))
    
    # tuple > list for space
    return cv.resize(img, tuple(dimensions))



"""
    resize image till width is <= the amount where x ░'s length passes a certain threshold
    TEXT_IMG will hold a list of tuples where each tuple will be separated by a new line

    # indexing is [height, width]
    print(THRESH[200, 0])

    dimensions
    cv.imshow('qwejlkqsdjkl', THRESH[0:22, 0:8])
    # print('░' * 50 + '█'*55)
"""
def texify(img: np.ndarray, 
        text_width_min: int = 800,
        spec_height: int = 22, 
        spec_width: int = 8
    ) -> Generator[Literal['█', '.', '\n'], None, None]:
    """
    the img that's taken in as argument assumes a completely unmodified, original
    version
    """

    proportioned = C_resize(img, text_width_min=text_width_min)
    gray = black_white(proportioned)
    _, thresh = cv.threshold(gray, 125, 255, 0)


    # gets height/width
    img_height, img_width = thresh.shape[: 2]
    maximum_img_pixels = spec_height * spec_width
    
    # the A to B crop for each vertical line in the text image
    vertical_track = (
        y * spec_height 
        for y in range(ceil(img_height / spec_height))
    )
    # have no clue why not using list here makes thing not work
    horizontal_track = [
        x * spec_width 
        for x in range(ceil(img_width / spec_width))
   ]

    # idea here is to check each small image for pixels, cropping a size similar to '█'
    for current_YCoordinate in vertical_track:
        for current_XCoordinate in horizontal_track:
            portion = thresh[
                current_YCoordinate : current_YCoordinate + spec_height, 
                current_XCoordinate : current_XCoordinate + spec_width
            ]

            # count the number of black pixels in that image
            # -10 is random offset doesnt matter
            """█░"""
            if (np.sum(portion == 0)) > ((maximum_img_pixels / 2) - 10):
                yield '█'
            else:
                yield '.'
        
        # new line after row of text is done
        yield '\n'

