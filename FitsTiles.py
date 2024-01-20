import math

from astropy.coordinates import SkyCoord

from astropy.io import fits
from astropy.wcs import WCS
from astropy.wcs import utils


def get_wcs_tiles(fits_file_path: str) -> (list[WCS], list[float]):
    """
    Gets the WCS tiles from a fits file
    :param fits_file_path: The path of the FITS file
    :return: A tuple containing:
     1. A list of WCS tiles each one of them with the values:
      - CD: Transformation matrix from pixel to coordinates
      - CRPIX: Axes reference pixels.
      - CRVAL: Axes reference coordinates.
      - CTYPE: Axes coordinate labels.
      - LATPOLE: Reference latitude at the pole.
      - LONGPOLE: Reference longitude at the pole.
      - CDELT: Pixels coordinate system origin (we suppose the same origin for all axes).
     2. A list of Pixel coordinate system origins for each tile.
     Positions in both lists refers to the same tile.
    """
    hdu_list = None
    try:
        hdu_list = fits.open(fits_file_path)
        data = hdu_list[1].data
        tile_list = []
        origin_list = []
        for row in data:
            naxis = len(row["NAXIS"])
            w = WCS(naxis=naxis)
            w.wcs.cd = row['CD']
            w.wcs.crpix = row['CRPIX']
            w.wcs.crval = row["CRVAL"]
            w.wcs.ctype = row["CTYPE"]
            w.wcs.latpole = row["LATPOLE"]
            w.wcs.lonpole = row["LONGPOLE"]
            tile_list.append(w)
            origin_list.append(row["CDELT"][0])
    finally:
        if hdu_list is not None:
            hdu_list.close()
    return tile_list, origin_list


def get_sub_tile_lower_left(wcs_list: list[WCS], origin_list: list[int], tile_number: int, ra_center: float,
                            dec_center: float) -> (float, float):
    """
    Get the lower left pixel coordinates of a given tile number
    :param wcs_list: the list of WCS tiles
    :param origin_list: the list of pixel coordinate system origin for each tile
    :param tile_number: the given tile number
    :param ra_center: the tile center RA.
    :param dec_center: the tile center Dec.
    :return: A tuple containing the lower left pixels of a given tile (x, y).
    """
    sky_coordinates = SkyCoord(ra=ra_center, dec=dec_center, frame="icrs", unit="deg")
    pixel = utils.skycoord_to_pixel(sky_coordinates, wcs_list[tile_number], origin_list[tile_number], "wcs")
    pos_horizontal = math.floor((round(pixel[0].item(0)) / 128.0 - 1) * 0.5)
    pos_vertical = math.floor((round(pixel[1].item(0)) / 128.0 - 1) * 0.5)
    if (pos_horizontal < 0) or (pos_horizontal > 7) or (pos_vertical < 0) or (pos_vertical > 7):
        return None, None
    ll_x = 256 * pos_horizontal
    ll_y = 256 * pos_vertical
    return ll_x, ll_y
