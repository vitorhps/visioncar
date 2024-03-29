import cv2
import numpy as np
import pytesseract as tess
import imutils
import re
import requests

filename = './files/video.mp4'
degrees = 270
car_plate_text_length = 10


def image_transform(image):
    image = imutils.rotate(image, degrees)
    image = imutils.resize(image, height=300)
    return image


def convert_to_black_white(image):
    image = cv2.blur(image, (3, 3))
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.bilateralFilter(gray, 7, 17, 17)
    edged = cv2.Canny(gray, 30, 200)

    return edged


def get_contours(image, image_org):
    contours = cv2.findContours(image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours = imutils.grab_contours(contours)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:20]

    for contour in contours:
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.035 * peri, True)

        if len(approx) == 4:
            return approx

    return None


def crop_car_plate(image, screenContours):
    ys = [screenContours[0, 0, 1], screenContours[1, 0, 1],
        screenContours[2, 0, 1], screenContours[3, 0, 1]]
    xs = [screenContours[0, 0, 0], screenContours[1, 0, 0],
        screenContours[2, 0, 0], screenContours[3, 0, 0]]

    ys_sorted_index = np.argsort(ys)
    xs_sorted_index = np.argsort(xs)

    x1 = screenContours[xs_sorted_index[0], 0, 0]
    x2 = screenContours[xs_sorted_index[3], 0, 0]

    y1 = screenContours[ys_sorted_index[0], 0, 1]
    y2 = screenContours[ys_sorted_index[3], 0, 1]

    return image[y1:y2, x1:x2]


def extract_car_plate_text(car_plate):
    car_plate = cv2.cvtColor(car_plate, cv2.COLOR_BGR2GRAY)
    car_plate = cv2.blur(car_plate, (3,3))

    car_plate_text = tess.image_to_string(car_plate)

    if len(car_plate_text) != car_plate_text_length:

        _, thresh = cv2.threshold(car_plate, 120, 255, cv2.THRESH_BINARY)
        cv2.imshow('img', thresh)

        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (4,4))
        opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

        car_plate_text = tess.image_to_string(opening)

    return re.sub('[^A-Za-z0-9]+', '', car_plate_text)


cap = cv2.VideoCapture(filename)

while cap.isOpened():

    ret, frame = cap.read()

    if ret == True:

        try:
            image = image_transform(frame)

            edged = convert_to_black_white(image)

            screenContours = get_contours(edged, image)

            car_plate = crop_car_plate(image, screenContours)

            car_plate_text = extract_car_plate_text(car_plate)            

            if len(car_plate_text) != 0:
                print('Placa: ' + car_plate_text)

            cv2.drawContours(image, [screenContours], -1, (0, 0, 255), 3)
            cv2.imshow('image', image)
            cv2.imshow('car plate', car_plate)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        except Exception as err:
            print(err)
