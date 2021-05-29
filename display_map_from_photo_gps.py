#   05/27/2021
#
#   name: display_map_from_photo_gps.py
#
#   Description:
#      This is GUI application.  Drop and Drop a photo image.
#      Extract the photo EXIF GPS Latitude and Longitude
#      Launch a map into the default web browser with this data.
#
#   Editor/Author: Warren Van Wyck   wvanwyck@outlook.com
#
#   Copied and modified code from:
#   https://learndataanalysis.org/how-to-implement-image-drag-and-drop-feature-pyqt5-tutorial/
#   https://www.thepythoncode.com/article/extracting-image-metadata-in-python

#   H:\WVWinstall\Python\environments\pyqt_env\Scripts\activate

#   pyinstaller  --onefile  display_map_from_photo_gps.py

#  05/27/21 WVW: Add to GitHub.

import sys

from   PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from   PyQt5.QtCore    import Qt

from   PIL             import Image
from   PIL.ExifTags    import TAGS, GPSTAGS
from   webbrowser      import open

drag_drop_prompt = '\n\n Drop Image Here \n\n'

# ===================================================================================

def extract_exif(exif):

    exif_out = {}

    exif_gps = {}
    exif_gps["GPSInfo"] = {}

    if exif is not None:
        for key, value in exif.items():
            name = TAGS.get(key, key)
            exif_out[name] = exif[key]

        if 'GPSInfo' in exif_out:
            for key in exif_out['GPSInfo'].keys():
                name = GPSTAGS.get(key, key)
                exif_gps['GPSInfo'][name] = exif_out['GPSInfo'][key]

    return exif_out, exif_gps

# ===================================================================================

def get_coordinates(info):
    for key in ['Latitude', 'Longitude']:
        if 'GPS' + key in info and 'GPS' + key + 'Ref' in info:
            e = info['GPS' + key]
            ref = info['GPS' + key + 'Ref']

            info[key] = ( str(int(e[0]))   + '°' +
                          str(int(e[1]))   + '′' +
                          str(float(e[2])) + '″ ' +
                          ref )

    if 'Latitude' in info and 'Longitude' in info:
        return [info['Latitude'], info['Longitude']]

# ===================================================================================

def get_coordinates_decimal(info):
    for key in ['Latitude', 'Longitude']:
        if 'GPS' + key in info and 'GPS' + key + 'Ref' in info:
            e = info['GPS' + key]
            ref = info['GPS' + key + 'Ref']
            coordinate =   float(e[0]) +             \
                           float(e[1]) / 60.0   +    \
                           float(e[2]) / 3600.0

            if ref in ['W', 'S']:
                coordinate = -coordinate

            info[key] = round(coordinate, 8)

    if 'Latitude' in info and 'Longitude' in info:
        return [info['Latitude'], info['Longitude']]

# ===================================================================================

def extract_latitude_longitude(imagename):

    trx_status = ''
    error_message = ''

    lat_lon_decimal = None
    trx_status = '*** not processed ***: '

    try:
        exif = Image.open(imagename)._getexif()
    except:  # noqa: E722
        exif = None

    if exif is None:
        error_message = 'no EXIF data extracted '
    else:
        exif_out, exif_gps = extract_exif(exif)

        print()
        try:
            disp_date_time = ' Date-Time: '  +  exif_out['DateTime']
        except KeyError:
            error_message += '*** no Date-Time ***'

        coordinate_info = get_coordinates(exif_gps['GPSInfo'])

        print()
        print("coordinate_info:", coordinate_info)
        print()

        if coordinate_info is None:
            error_message += '*** no GPS data found/processed *** '
        else:
            print('For Google Maps/Earth copy and paste:')
            print(coordinate_info[0]  +  ', '  +  coordinate_info[1])
            coordinate_info_decimal = get_coordinates_decimal(exif_gps['GPSInfo'])
            lat_lon_decimal = str(coordinate_info_decimal[0])  +  ', '  +  str(coordinate_info_decimal[1])
            print(lat_lon_decimal)
            error_message +=  lat_lon_decimal  +  ' '
            trx_status = 'Success! '  +  disp_date_time  +  '\n'

    trx_status += error_message

    return lat_lon_decimal, trx_status

# ===================================================================================

class ImageLabel(QLabel):
    def __init__(self):
        super().__init__()

        self.setAlignment(Qt.AlignCenter)
        self.setText(drag_drop_prompt  +  'Initiate')
        self.setStyleSheet('''
            QLabel{
                border: 4px dashed #aaa
            }
        ''')

# ===================================================================================

class AppDemo(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(400, 400)
        self.setAcceptDrops(True)

        mainLayout = QVBoxLayout()

        self.photoViewer = ImageLabel()
        mainLayout.addWidget(self.photoViewer)

        self.setLayout(mainLayout)

    def dragEnterEvent(self, event):
        if event.mimeData().hasImage:
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasImage:
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasImage:
            event.setDropAction(Qt.CopyAction)
            file_path = event.mimeData().urls()[0].toLocalFile()
            print()
            print('file_path:', file_path)

            lat_lon_decimal, out_status = extract_latitude_longitude(file_path)
            if lat_lon_decimal is None:
                print('***', out_status)
            else:
                open("http://www.google.com/maps/place/" + lat_lon_decimal)

            self.set_image(file_path, out_status)

            event.accept()
        else:
            event.ignore()

    def set_image(self, file_path, status):
        self.photoViewer.setText('Done: '  +  file_path  +
                drag_drop_prompt  +  status)

# ===================================================================================

app = QApplication(sys.argv)
demo = AppDemo()
demo.show()
sys.exit(app.exec_())
