import datetime
import unittest
import numpy as np
import pytest
from numpy.testing import assert_allclose

from astropy import units as u
from astropy.modeling import models
from astropy.wcs import wcs

import GetClicks as gc


COMPLETE_LINE =  "24558580,MarioMario,1234,127.0.0.1,1687,Start Your Search,45.144,2017-01-12 11:17:04 UTC,,,\"{\"\"session\"\":\"\"c750fa4c6720755e7325b1b98410925e1e76b600364e703057d564ee6298b63c\"\",\"\"viewport\"\":{\"\"width\"\":1408,\"\"height\"\":711},\"\"started_at\"\":\"\"2017-01-12T11:13:09.875Z\"\",\"\"user_agent\"\":\"\"Mozilla/5.0 (Windows NT 10.0; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0\"\",\"\"utc_offset\"\":\"\"0\"\",\"\"finished_at\"\":\"\"2017-01-12T11:17:04.688Z\"\",\"\"live_project\"\":false,\"\"user_language\"\":\"\"en\"\",\"\"user_group_ids\"\":[],\"\"subject_dimensions\"\":[{\"\"clientWidth\"\":361,\"\"clientHeight\"\":358,\"\"naturalWidth\"\":532,\"\"naturalHeight\"\":528},{\"\"clientWidth\"\":361,\"\"clientHeight\"\":358,\"\"naturalWidth\"\":532,\"\"naturalHeight\"\":528},{\"\"clientWidth\"\":361,\"\"clientHeight\"\":358,\"\"naturalWidth\"\":532,\"\"naturalHeight\"\":528},{\"\"clientWidth\"\":361,\"\"clientHeight\"\":358,\"\"naturalWidth\"\":532,\"\"naturalHeight\"\":528}]}\",\"[{\"\"task\"\":\"\"T1\"\",\"\"task_label\"\":\"\"If you don't see any objects of interest, simply click **Done.**  \n\nIf you do see an object of interest (a \"\"mover\"\" or a \"\"dipole\"\"), mark its location using your cursor as a marking tool. Be sure to mark its location in all of the frames. If you see multiple moving objects, mark the locations of all of them. Do not mark artifacts or objects that appear in only one or two frames. Click **Done** when you are finished.\n\n\n\"\",\"\"value\"\":[{\"\"x\"\":73.41880798339844,\"\"y\"\":159.14012145996094,\"\"tool\"\":0,\"\"frame\"\":0,\"\"details\"\":[],\"\"tool_label\"\":\"\"Marking tool\"\"},{\"\"x\"\":71.8450927734375,\"\"y\"\":154.714111328125,\"\"tool\"\":0,\"\"frame\"\":1,\"\"details\"\":[],\"\"tool_label\"\":\"\"Marking tool\"\"},{\"\"x\"\":77.84483337402344,\"\"y\"\":160.78759765625,\"\"tool\"\":0,\"\"frame\"\":2,\"\"details\"\":[],\"\"tool_label\"\":\"\"Marking tool\"\"},{\"\"x\"\":76.2711181640625,\"\"y\"\":162.262939453125,\"\"tool\"\":0,\"\"frame\"\":3,\"\"details\"\":[],\"\"tool_label\"\":\"\"Marking tool\"\"}]}]\",\"{\"\"5192597\"\":{\"\"retired\"\":{\"\"id\"\":3868339,\"\"workflow_id\"\":1687,\"\"classifications_count\"\":15,\"\"created_at\"\":\"\"2017-02-16T15:24:50.721Z\"\",\"\"updated_at\"\":\"\"2017-02-18T00:18:27.035Z\"\",\"\"retired_at\"\":\"\"2017-02-18T00:18:27.025Z\"\",\"\"subject_id\"\":5192597,\"\"retirement_reason\"\":null},\"\"id\"\":\"\"491023\"\",\"\"image0\"\":\"\"unwise-1503m046.x1.y7.e0.jpeg\"\",\"\"image1\"\":\"\"unwise-1503m046.x1.y7.e1.jpeg\"\",\"\"image2\"\":\"\"unwise-1503m046.x1.y7.e2.jpeg\"\",\"\"image3\"\":\"\"unwise-1503m046.x1.y7.e3.jpeg\"\",\"\"!SIMBAD\"\":\"\"http://simbad.u-strasbg.fr/simbad/sim-coo?Coord=150.86998+-3.8591621\u0026Radius=498\u0026Radius.unit=arcsec\"\",\"\"!VizieR\"\":\"\"http://vizier.u-strasbg.fr/viz-bin/VizieR?-source=\u0026-out.add=_r\u0026-out.add=_RAJ%2C_DEJ\u0026-sort=_r\u0026-to=\u0026-out.max=20\u0026-meta.ucd=2\u0026-meta.foot=1\u0026-c.rs=498\u0026-c=150.86998+-3.8591621\"\",\"\"Tile Number\"\":\"\"7672\"\",\"\"subtile center\"\":\"\"R.A.= 150.86998 dec= -3.8591621\"\",\"\"!IRSA Finder Chart\"\":\"\"http://irsa.ipac.caltech.edu/applications/finderchart/#\u0026id=Hydra_finderchart_finder_chart\u0026projectId=finderchart\u0026UserTargetWorldPt=150.86998;-3.8591621;EQ_J2000\u0026subsize=0.195556\u0026sources=DSS,SDSS,2MASS,IRIS,WISE\u0026DoSearch=true\"\",\"\"Motion of Planet Nine\"\":\"\"JUMP-JUMP BACK-JUMP-JUMP BACK\"\",\"\"id numbers of nearest subtiles\"\":\"\"494312, 494320, 491015, 491022, 491031, 491030, 491014, 494304, 494328, 496255\"\",\"\"Modified Julian Dates of Each Epoch\"\":\"\"55336.5, 55526.8, 56799.9, 56990.2\"\"}}\",5192597"

class MyTestCase(unittest.TestCase):

    def test_read_number_from_key(self):
        test_string = ("are finished.\n\n\n\"\",\"\"value\"\":[{\"\"x\"\":73.41880798339844,"
                       "\"\"y\"\":159.14012145996094,\"\"tool\"\":5,\"\"frame\"\":0,\"\"deta y\"\":159.14012145996094,")

        number, next_key = gc.read_number_from_key(test_string, gc.X_PREFIX)
        self.assertEqual(73.41880798339844, float(number))  # add assertion here
        self.assertEqual(54, next_key)  # add assertion here
        number, next_key = gc.read_number_from_key(test_string, gc.Y_PREFIX, 54)
        self.assertEqual(159.14012145996094, float(number))  # add assertion here
        self.assertEqual(79, next_key)  # add assertion here
        number, next_key = gc.read_number_from_key(test_string, gc.TOOL_PREFIX, 79)
        self.assertEqual(5, int(number))  # add assertion here
        self.assertEqual(90, next_key)  # add assertion here
        number, next_key = gc.read_number_from_key(test_string, gc.X_PREFIX, 90)
        self.assertIsNone(number)
        self.assertEqual(next_key, -1)


    def test_extract_clicks(self):
        clicks = gc.extract_clicks(COMPLETE_LINE)
        self.assertEqual(4, len(clicks))
        self.assertEqual(3, clicks[3].frame)
        self.assertEqual(0, clicks[3].tool)
        self.assertEqual(76.2711181640625, clicks[3].x)
        self.assertEqual(162.262939453125, clicks[3].y)


    def test_extract_classification(self):
        classification = gc.extract_classification_data(COMPLETE_LINE)
        self.assertIsNotNone(classification)
        self.assertEqual(24558580, classification.classification_id)
        self.assertEqual("MarioMario", classification.user_name)
        self.assertEqual("1234", classification.user_id)
        self.assertEqual("127.0.0.1", classification.user_ip)
        self.assertEqual("1687", classification.workflow_id)
        self.assertEqual("Start Your Search", classification.workflow_name)
        self.assertEqual("45.144", classification.workflow_version)

        try:
            expected_started_at = datetime.datetime.strptime("2017-01-12 11:17:04 UTC", "%Y-%m-%d %H:%M:%S %Z")
            self.assertEqual(expected_started_at, classification.started_at)
        except:
            self.assertFalse("Error parsing expected date")
        self.assertEqual("", classification.gold_standard)
        self.assertEqual("", classification.expert)
        self.assertEqual(5192597, classification.subject_id)

    def test_extract_sub_tile_center(self):
        coordinate = gc.extract_sub_tile_center(COMPLETE_LINE)
        self.assertIsNotNone(coordinate)
        self.assertEqual(-3.8591621, coordinate.dec)
        self.assertEqual(150.86998, coordinate.ra)

    def test_extract_tile_numnber(self):
        tile_number = gc.extract_tile_number(COMPLETE_LINE)
        self.assertEqual(7672, tile_number)

    def test_against_wcslib(self):
        inp = [(0, 0), (4000, -20.56), (-2001.5, 45.9),
                                       (0, 90), (0, -90), (np.mgrid[:4, :6])]
        w = wcs.WCS()
        crval = [202.4823228, 47.17511893]
        wcs.crval = crval
        wcs.ctype = ['RA---TAN', 'DEC--TAN']

        lonpole = 180
        tan = models.Pix2Sky_Gnomonic()
        n2c = models.RotateNative2Celestial(crval[0] * u.deg, crval[1] * u.deg, lonpole * u.deg)
        c2n = models.RotateCelestial2Native(crval[0] * u.deg, crval[1] * u.deg, lonpole * u.deg)
        m = tan | n2c
        minv = c2n | tan.inverse

        radec = w.wcs_pix2world(inp[0], inp[1], 1)
        xy = w.wcs_world2pix(radec[0], radec[1], 1)



if __name__ == '__main__':
    unittest.main()

